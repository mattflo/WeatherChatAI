import os
import uuid

from langchain.chains import SequentialChain
from langchain.memory import ConversationBufferWindowMemory, PostgresChatMessageHistory

from weather_chat_ai.location_chain import LocationChain
from weather_chat_ai.nws_chain import NWSChain
from weather_chat_ai.reply_chain import ReplyChain


class WeatherChatChain(SequentialChain):
    def __init__(self, whoami="Anonymous", tags=[], session_id: str = None):
        if session_id is None:
            session_id = str(uuid.uuid4())

        history = PostgresChatMessageHistory(
            connection_string=os.getenv("DATABASE_URL"),
            session_id=session_id,
        )

        memory = ConversationBufferWindowMemory(
            chat_memory=history,
            input_key="input",
        )

        super().__init__(
            chains=[LocationChain(memory), NWSChain(), ReplyChain(memory)],
            input_variables=["input"],
            tags=tags,
            metadata={"whoami": whoami},
        )
