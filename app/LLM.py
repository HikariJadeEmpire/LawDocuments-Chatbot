from openai import OpenAI

class start_llm():
    def __init__(self, openai_api_key) -> None:
        self.model = OpenAI(api_key=openai_api_key)
    
    def get_response(self, messages : list, model="gpt-3.5-turbo-0125", temperature=0) -> str:
        response = self.model.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature, # this is the degree of randomness of the model's output
        )
        return response.choices[0].message.content