import json
import openai
from Models.Notion import Notion


class System:
    def __init__(self):
        self.notion = Notion()
        with open("src/prompt.txt", "r") as prompt, open("keys/OPENAI_API_KEY.txt", "r") as OPENAI_API_KEY:
            self.memory = [
                {"role": "system",
                 "content": "You are a helpful task manager who helps set the user’s to-do by setting the right and clear objectives. You keep all created to-dos up to date by updating them when the user acts on objectives"}]
            openai.api_key = OPENAI_API_KEY.readline()
        self.memory.append(
            {"role": "system",
             "content": f"Existing todos are: {self.notion.get_todos()}"}
        )
        self.functions = [
            {
                "name": "create_todo",
                "description": "Create one or multiple to-dos",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "objectives": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "description": "Short name for a to-do",
                            },
                        },
                    },
                    "required": ["objectives"],
                },
            },
            {
                "name": "update_todo",
                "description": "Update one or multiple to-dos",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "todo_name": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "description": f"Name of an existing to-do",
                            },
                        },
                        "todo_status": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["Not started", "In progress", "Done"],
                            },
                        },
                    },
                    "required": ["objectives"],
                },
            },

        ]

    def create_completion(self):
        response = openai.ChatCompletion.create(model="gpt-4", messages=self.memory, functions=self.functions,
                                                function_call="auto")

        response_message = response["choices"][0]["message"]
        print(response_message["content"])
        self.memory.append(response_message)
        if "function_call" in response_message:
            available_functions = {
                "create_todo": self.notion.create_todo,
                "update_todo": self.notion.update_todo,
            }

            function_name = response_message["function_call"]["name"]

            if function_name in available_functions:
                function_to_call = available_functions[function_name]
                function_args = json.loads(response_message["function_call"]["arguments"])
                function_response = function_to_call(**function_args)

                self.memory.append(
                    {
                        "role": "function",
                        "name": function_name,
                        "content": function_response,
                        # "content": f"To-do is successfully {function_name.replace('_', ' ')}d",
                    }
                )
                self.create_completion()
                # second_response = openai.ChatCompletion.create(model="gpt-4", messages=self.memory)
                # second_response_message = second_response["choices"][0]["message"]
                # self.memory.append(second_response_message)
                # print(second_response_message)
