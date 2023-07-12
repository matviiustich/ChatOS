import json
import openai
from Models.Notion import Notion


class System:
    def __init__(self):
        self.notion = Notion()
        with open("src/prompt.txt", "r") as prompt, open("keys/OPENAI_API_KEY.txt", "r") as OPENAI_API_KEY:
            self.memory = [{"role": "system", "content": "You are a helpful assistant"}]
            openai.api_key = OPENAI_API_KEY.readline()
        self.functions = [
            {
                "name": "create_todo",
                "description": "Create a to-do",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "objective": {
                            "type": "string",
                            "description": "Short name for a to-do",
                        },

                    },
                    "required": ["objective"],
                },

            }
        ]

    def create_completion(self):
        response = openai.ChatCompletion.create(model="gpt-4", messages=self.memory, functions=self.functions)
        # for chunk in response:
        #     res = chunk["choices"][0]["delta"]
        #     if len(res) != 0:
        #         print(res["content"], end="")
        # print()
        print(response["choices"][0]["message"]["content"])

        response_message = response["choices"][0]["message"]

        if response_message.get("function_call"):
            available_functions = {
                "create_todo": self.notion.create_todo,
            }
            function_name = response_message["function_call"]["name"]
            function_to_call = available_functions[function_name]
            function_args = json.loads(response_message["function_call"]["arguments"])
            function_response = function_to_call(
                objective=function_args.get("objective"),
            )

            self.memory.append(response_message)
            self.memory.append(
                {
                    "role": "function",
                    "name": function_name,
                    "content": function_response,
                }
            )

    def add_to_memory(self, role, content):
        self.memory.append({"role": role, "content": content})
