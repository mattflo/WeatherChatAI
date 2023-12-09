from typing import Any, Dict, List, Optional
from uuid import UUID

from langchain.callbacks.base import BaseCallbackHandler
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.outputs import LLMResult


class Callback(BaseCallbackHandler):
    run_id_to_name: Dict[UUID, str]
    inputs: Dict[str, Any]

    def __init__(
        self,
        memory: ConversationBufferWindowMemory,
        end_of_chain,
    ):
        self.end_llm = end_of_chain.__name__
        self.memory = memory
        self.run_id_to_name = {}
        self.inputs = {}

    async def on_chain_start(
        self,
        serialized: Dict[str, Any],
        inputs: Dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Run when chain starts running."""
        if not self.inputs and "input" in inputs and inputs["input"]:
            self.inputs = inputs

    async def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: List[str],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Run when LLM starts running."""
        if "name" in metadata:
            self.run_id_to_name[run_id] = metadata["name"]

    async def on_llm_end(
        self,
        response: LLMResult,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        """Run when LLM ends running."""
        if (
            self.run_id_to_name.get(run_id, None) == self.end_llm
            and "input" in self.inputs
        ):
            result = response.generations[0][0].text
            self.memory.save_context(self.inputs, {"text": result})
