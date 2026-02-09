from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseLanguageHandler(ABC):

    @abstractmethod
    def parse(self, source_code: str) -> Any:
        pass

    @abstractmethod
    def analyze(self, tree: Any) -> Dict:
        pass

    @abstractmethod
    def diff(self, original: str, modified: str) -> Dict:
        pass

    @abstractmethod
    def ai_prompt_context(self) -> str:
        pass
