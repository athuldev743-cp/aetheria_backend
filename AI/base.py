from abc import ABC, abstractmethod

class AIplatform(ABC):

    @abstractmethod
    def chat(self, prompt: str) -> str:
        """Send a prompt to AI and return response text."""
        pass
