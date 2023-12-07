from langchain.schema.runnable import RunnableLambda


from typing import Callable


class MergeKeys(RunnableLambda):
    @staticmethod
    def create_merge_keys(callable: Callable[[dict], dict]):
        def MergeKeys(x: dict):
            x.update(callable(x))
            return x

        return MergeKeys

    def __init__(
        self,
        callable: Callable[[dict], dict] = None,
    ):
        super().__init__(self.create_merge_keys(callable))
