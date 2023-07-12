import openai
import requests, json


class System:
    def __init__(self):
        with open("prompt.txt", "r") as prompt, open("OPENAI_API_KEY.txt", "r") as OPENAI_API_KEY:
            self.memory = [{"role": "system", "content": "You are a ios developer"}]
            openai.api_key = OPENAI_API_KEY.readline()

    def create_completion(self):
        response = openai.ChatCompletion.create(model="gpt-4", messages=self.memory, stream=True)
        for chunk in response:
            res = chunk["choices"][0]["delta"]
            if len(res) != 0:
                print(res["content"], end="")
        print()

    def add_to_memory(self, role, content):
        self.memory.append({"role": role, "content": content})

