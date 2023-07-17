import json

from Models.Notion import Notion
import requests

url = "https://api.notion.com/v1/databases/f7771e76620e4a529cc135ff907e348a"
headers = {
            "Authorization": "Bearer secret_okDFvW4EV5V4mJXOahMPNGz7mErwFNJCencWSbtEhjt",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }
res = requests.get(url, headers=headers)
with open("db.json", 'a') as file:
    file.write(json.dumps(res.json(), indent=4))
print(res.json())
notion = Notion()
notion.create_project("https://www.notion.so/8092d45fea9b493fbb6e8d63c37f9099?pvs=4")
