import uuid
from typing import AsyncGenerator, List

import structlog
from langchain_core.messages import BaseMessage
from langchain_core.runnables.config import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.graph import END, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode

from weather_chat_ai.tool import get_weather_forecast

logger = structlog.get_logger(__name__)


class WeatherGraphAgent:
    def __init__(
        self,
        messages: List[BaseMessage],
        **metadata,
    ):
        self.messages = messages
        self.metadata = metadata
        tools = [get_weather_forecast]
        tool_node = ToolNode(tools)

        llm = ChatOpenAI(model="gpt-4o-mini").bind_tools(tools)

        def call_model(state: MessagesState):
            messages = state["messages"]
            response = llm.invoke(messages)
            return {"messages": [response]}

        workflow = StateGraph(MessagesState)

        workflow.add_node("agent", call_model)
        workflow.add_node("tools", tool_node)
        workflow.set_entry_point("agent")

        workflow.add_conditional_edges(
            # First, we define the start node. We use `agent`.
            "agent",
            self.should_continue,
        )

        workflow.add_edge("tools", "agent")

        self.app = workflow.compile()

    def should_continue(self, state: MessagesState) -> str:
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools"
        return END

    def run(self):
        result = self.app.invoke({"messages": self.messages})
        return result["messages"][-1].content

    async def astream(self) -> AsyncGenerator[str, None]:
        config = RunnableConfig(run_id=str(uuid.uuid4()), metadata=self.metadata)
        async for event in self.app.astream_events(
            {"messages": self.messages},
            version="v1",
            config=config,
        ):
            event_type = event["event"]
            if event_type not in ("on_chat_model_stream"):
                continue

            content = event["data"]["chunk"].content

            if not content:
                continue

            # anthropic
            if isinstance(content, list):
                text = content[0].get("text", "")
                if text:
                    yield text
            # openai
            else:
                yield content
