import openai
import requests
import json
from datetime import datetime, timezone

from Models.System import System
from Models.Notion import Notion

system = System()

userInput = input("user: ")
while userInput != "/quit":
    system.add_to_memory("user", userInput)
    system.create_completion()
    userInput = input("user: ")

notion = Notion()
print(notion.get_todos())

notion.create_todo("Clean the room")

# url = "Test Url 1"
# title = "Test title 1"
# published_date = datetime.now().astimezone(timezone.utc).isoformat()
# data = {
#     "URL": {"title": [{"text": {"content": url}}]},
#     "Title": {"rich_text": [{"text": {"content": title}}]},
#     "Published": {"date": {"start": published_date, "end": None}}
# }
#
# notion.create_todo(data)
