import json
import openai
from Models.Notion import Notion
from datetime import datetime
import time

# Memory structure:
# memory[0] = prompt
# memory[1] = existing todos
# memory[2] = current date


class System:
    def __init__(self):
        self.notion = Notion()
        self.memory = [{"role": "system", "content": ""} for _ in range(3)]
        self.memory[1]["content"] = self.notion.get_todos()
        self.memory[2]["content"] = f"Today is: {time.ctime()}"
        with open("src/prompt.txt", "r") as prompt, open("keys/OPENAI_API_KEY.txt", "r") as OPENAI_API_KEY:
            self.memory[0]["content"] = prompt.readline()
            openai.api_key = OPENAI_API_KEY.readline()
        self.functions = [
            {
                "name": "create_project",
                "description": "Initialises a task management project",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "link": {
                            "type": "string",
                            "description": "Link of the notion workspace provided by the user where the user wants to "
                                           "initialise the project "
                        },
                        "description": {
                            "type": "string",
                            "description": "OS (NOT THE USER) should generate a description, so the user will "
                                           "understand the purpose of the project "
                        }
                    },
                    "required": ["link", "description"]
                }
            },
            {
                "name": "create_todo",
                "description": "Create todos",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "objectives": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "todo_name": {
                                        "type": "string",
                                        "description": "Short name for a to-do"
                                    },
                                    "start_time": {
                                        "type": "string",
                                        "format": "date-time",
                                        "description": "Start time of the to-do in the format: %H:%M"
                                    },
                                    "end_time": {
                                        "type": "string",
                                        "format": "date-time",
                                        "description": "End time of the to-do in the format: %H:%M"
                                    },
                                    "description": {
                                        "type": "string",
                                        "description": "If the todo requires several steps to complete, then OS (NOT "
                                                       "THE USER) should make a brief description of the steps "
                                    },
                                    "days": {
                                        "type": "array",
                                        "items": {
                                            "type": "string",
                                            "description": "The day for which the todo will be created"
                                        }
                                    }
                                },
                                "required": ["todo_name", "start_time", "end_time", "days"]
                            },
                            "description": "Array of tuples in format (todo_name, start_time, end_time)"
                        }
                    },
                    "required": ["objectives"]
                }
            },

            {
                "name": "update_todo",
                "description": "Update todos",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "todos": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "todo_id": {
                                        "type": "string",
                                        "description": "ID of an existing to-do",
                                    },
                                    "todo_status": {
                                        "type": "string",
                                        "enum": ["Not completed", "Completed"],
                                    }
                                },
                                "required": ["todo_name", "todo_status"]
                            },
                            "description": "Array of tuples in format (todo_name, todo_status)"
                        }
                    },
                    "required": ["todos"],
                }
            }
        ]

    def create_completion(self):
        self.memory[2]["content"] = f"Today is: {time.ctime()}"
        response = openai.ChatCompletion.create(model="gpt-4", messages=self.memory, functions=self.functions,
                                                function_call="auto")

        response_message = response["choices"][0]["message"]
        if response_message["content"] is not None:
            print(response_message["content"])
        self.memory.append(response_message)
        if "function_call" in response_message:
            available_functions = {
                "create_project": self.notion.create_project,
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
                self.memory[1]["content"] = self.notion.get_todos()
                self.create_completion()
