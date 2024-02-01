import uuid
from typing import Any, AsyncIterator, Iterator, Optional, cast

from langchain.memory import ConversationBufferWindowMemory
from langchain.schema.runnable.base import RunnableSequence
from langchain_core.load.dump import dumpd
from langchain_core.runnables.config import (
    RunnableConfig,
    ensure_config,
    get_async_callback_manager_for_config,
    merge_configs,
    patch_config,
)
from langchain_core.runnables.utils import Input, Output

from weather_chat_ai.callback import Callback
from weather_chat_ai.location_chain import LocationChain
from weather_chat_ai.nws_chain import NWSChain
from weather_chat_ai.reply_chain import ReplyChain
from weather_chat_ai.with_history import WithHistory


class WeatherChatAI(RunnableSequence):
    memory: ConversationBufferWindowMemory = None
    whoami: str = None
    session_id: str = None

    def __init__(
        self,
        session_id: str = None,
        whoami: str = "Anonymous",
    ):
        if session_id is None:
            session_id = str(uuid.uuid4())

        memory = ConversationBufferWindowMemory(
            input_key="input",
        )

        reply_chain = ReplyChain()
        location_chain = LocationChain()

        runnables = [
            WithHistory(memory),
            location_chain.with_retry(),
            NWSChain().with_retry(),
            # this is a runnable sequence instead of a chain to enable streaming more easily
            reply_chain,
        ]

        first = runnables[0]
        middle = runnables[1:-1]
        last = runnables[-1]

        super().__init__(
            first=first,
            middle=middle,
            last=last,
        )

        self.memory = memory
        self.whoami = whoami
        self.session_id = session_id

    def stream(
        self,
        input: Input,
        config: Optional[RunnableConfig] = None,
        **kwargs: Optional[Any],
    ) -> Iterator[Output]:
        yield from self.transform(iter([input]), self.add_callback(config), **kwargs)

    async def astream(
        self,
        input: Input,
        config: Optional[RunnableConfig] = None,
        **kwargs: Optional[Any],
    ) -> AsyncIterator[Output]:
        async def input_aiter() -> AsyncIterator[Input]:
            yield input

        async for chunk in self.atransform(
            input_aiter(), self.add_callback(config), **kwargs
        ):
            yield chunk

    def invoke(
        self,
        input: Input,
        config: Optional[RunnableConfig] = None,
    ) -> Output:
        return super().invoke(input, self.add_callback(config))

    async def ainvoke(
        self,
        input: Input,
        config: Optional[RunnableConfig] = None,
        **kwargs: Optional[Any],
    ) -> Output:
        # setup callbacks
        config = self.add_callback(config)
        config = ensure_config(config)
        callback_manager = get_async_callback_manager_for_config(config)
        # start the root run
        run_manager = await callback_manager.on_chain_start(
            dumpd(self), input, name=config.get("run_name")
        )

        # invoke all steps in sequence
        try:
            for i, step in enumerate(self.steps):
                input = await step.ainvoke(
                    input,
                    # mark each step as a child run
                    patch_config(
                        config, callbacks=run_manager.get_child(f"seq:step:{i+1}")
                    ),
                )
        # finish the root run
        except BaseException as e:
            await run_manager.on_chain_error(e)
            raise
        else:
            await run_manager.on_chain_end(input)
            return cast(Output, input)

    def add_callback(
        self,
        config: Optional[RunnableConfig] = None,
    ) -> RunnableConfig:
        cb = Callback(self.memory, end_of_chain=ReplyChain)
        run_config = RunnableConfig(
            callbacks=[cb],
            metadata={"whoami": self.whoami, "session_id": self.session_id},
        )
        return merge_configs(config, run_config)
