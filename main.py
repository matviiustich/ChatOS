from Models.System import System
from Models.Notion import Notion
from datetime import datetime, timezone


system = System()

notion = Notion()

userInput = input("user: ")
while userInput != "/quit":
    # system.add_to_memory("user", userInput)
    system.memory.append({"role": "user", "content": userInput})
    system.create_completion()
    userInput = input("user: ")

# notion.get_todos()

# print(type(datetime.now().astimezone(timezone.utc).isoformat()))