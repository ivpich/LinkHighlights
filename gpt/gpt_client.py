import openai
from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')


class ChatGPTClient:
    def __init__(self, client, system_prompt='You are a helpful assistant.'):
        self.api_key = api_key
        openai.api_key = self.api_key
        self.client = client
        self.system_prompt = system_prompt

    def get_embedding(self, text, model="text-embedding-3-small"):
        """
        Retrieves embeddings for the given text using the specified model.
        """
        text = text.replace("\n", " ")
        try:
            response = self.client.embeddings.create(input=[text], model=model)
            embedding = response.data[0].embedding

            return embedding
        except Exception as e:
            print(f"Failed to get embedding: {e}")
            return None

    def answer_prompt(self, prompt, model='gpt-3.5-turbo'):
        """
        Generates a response to a given prompt using the specified model.
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Failed to generate answer: {e}")
            return None


my_client = OpenAI(api_key=api_key)
gpt_client = ChatGPTClient(my_client)
