from langchain.schema.runnable import RunnableLambda


from typing import Any


class WrapWithKey(RunnableLambda):
    @staticmethod
    def create_add_key(key: str):
        def WrapWithKey(x: Any):
            return {key: x}

        return WrapWithKey

    def __init__(
        self,
        key: str,
    ):
        super().__init__(self.create_add_key(key))
