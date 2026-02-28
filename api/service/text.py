from abc import ABC, abstractmethod

class TextModel(ABC):
    @abstractmethod
    def generate_response(self, query: str, context: dict) -> str:
        """
        Generate a text response based on the user query and context.
        """
        pass

class GPTModel(TextModel):
    def generate_response(self, query: str, context: dict) -> str:
        """
        Placeholder implementation for GPT-4o-mini or similar LLM.
        """
        # TODO: Integrate with OpenAI or AWS Bedrock
        return f"Response to '{query}' (Context: {len(context)} items)"
