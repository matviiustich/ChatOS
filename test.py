import json

from Models.Notion import Notion
import requests

notion = Notion()
# notion.create_project("https://www.notion.so/8092d45fea9b493fbb6e8d63c37f9099?pvs=4", "This is your todos")
print(notion.create_project("https://www.notion.so/8092d45fea9b493fbb6e8d63c37f9099?pvs=4", "basic project"))
