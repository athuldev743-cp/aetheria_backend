from abc import ABC, abstractmethod


class AIplatform(ABC):

    @abstractmethod
    def chat(self, prompt: str) -> str:
        """sends a prompt to AI and returns a response text.""" 
        pass