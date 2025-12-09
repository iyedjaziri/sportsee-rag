from typing import Any, List, Optional
from langchain_mistralai import ChatMistralAI
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.outputs import ChatResult

class SafeChatMistralAI(ChatMistralAI):
    """
    Wrapper around ChatMistralAI to strip 'stop' parameters 
    and suppress 'Parameter stop not yet supported' warnings.
    """
    def _generate(
        self,
        messages: List[Any],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        # Mistral API (via this client ver) warns if 'stop' is passed.
        # We intercept and remove it if it's causing issues, 
        # acts as if stop was None to the underlying client but we can't implement it client-side easily here 
        # without token processing. 
        # For now, just suppressing it to clean logs as requested.
        
        return super()._generate(messages, stop=None, run_manager=run_manager, **kwargs)
