from typing import Any, Dict, List, Optional

from langchain.callbacks.manager import CallbackManagerForChainRun
from langchain.chains.base import Chain
from langchain_core.memory import BaseMemory


class WithMemory(Chain):
    # something inherited isn't happy with leading underscore, so we use trailing
    input_keys_: List[str] = []
    output_keys_: List[str] = []

    @property
    def input_keys(self) -> List[str]:
        return self.input_keys_

    @property
    def output_keys(self) -> List[str]:
        return self.output_keys_

    def __init__(
        self,
        memory: BaseMemory,
        input_keys: List[str] = ["input"],
        output_keys: List[str] = ["history"],
    ):
        super().__init__()
        self.memory = memory
        self.input_keys_ = input_keys
        self.output_keys_ = output_keys

    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, Any]:
        return self.memory.load_memory_variables(inputs)
