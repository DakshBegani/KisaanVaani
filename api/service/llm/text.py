from .bedrock import BedrockModel


class GPTModel:
    def __init__(self):
        self.model = BedrockModel()

    def generate_response(self, query, context):
        result = self.model.generate_response(query, context)
        if isinstance(result, dict):
            return str(result)
        return result
