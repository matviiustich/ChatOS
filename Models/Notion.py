import json
import requests
from dateutil.parser import parse
import tzlocal
from datetime import datetime, timedelta
import pytz

def parse_datetime_string(dt_str):
    return datetime.strptime(dt_str, "%H:%M")

def parse_date_string(date_string):
    parsed_date = parse(date_string)
    iso_date = parsed_date.isoformat()
    return iso_date


class Notion:
    def __init__(self):
        with open("keys/NOTION_API_KEY.txt") as key:
            self.notion_api_key = key.readline()
        with open("src/database.txt", "r") as database_file:
            self.database_id = database_file.readline()
        self.headers = {
            "Authorization": "Bearer " + self.notion_api_key,
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }

    def create_project(self, link: str, description: str):
        if self.database_id == "":
            page_id = link[link.rfind('?') - 32:link.rfind('?')]
            block_data = {
                "children": [{
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": description
                                }
                            }
                        ]
                    }
                }]
            }

            description_url = f"https://api.notion.com/v1/blocks/{page_id}/children"
            res = requests.patch(description_url, headers=self.headers, json=block_data)

            database_url = "https://api.notion.com/v1/databases/"
            payload = {"parent": {"type": "page_id", "page_id": page_id},
                       "title": [{"type": "text", "text": {"content": "To-Do database"}}],
                       "properties": {"Objective": {"title": {}},
                                      "Completed": {"checkbox": {}},
                                      "Date": {"type": "date", "date": {}},
                                      "Description": {"rich_text": {}}
                                      }}
            res = requests.post(url=database_url, json=payload, headers=self.headers)
            with open("src/database.txt", 'a') as database_file:
                database_file.write(res.json()["id"])
                self.database_id = res.json()["id"]
        return json.dumps("Success")

    def get_todos(self) -> str:
        if self.database_id != "":
            url = f"https://api.notion.com/v1/databases/{self.database_id}/query"

            payload = {"page_size": 100}
            res = requests.post(url, json=payload, headers=self.headers)
            data = res.json()
            with open("db.json", "a") as f:
                f.write(json.dumps(data, indent=4))
            result = data["results"]
            todos = []
            for todo in result:
                todo_id = todo["id"]
                todo_status = todo["properties"]["Completed"]["checkbox"]
                todo_objective = todo["properties"]["Objective"]["title"][0]["text"]["content"]
                todos.append(f"Todo: {todo_objective}, ID: {todo_id}, status: {todo_status}")
            return_data = ".".join(todos)
            return f"The project was already initialised. {return_data}"
        else:
            return "User haven’t initialised the project"

    def create_todo(self, objectives):
        status_code = 0
        for objective in objectives:
            objective_days = objective["days"]
            objective_name = objective["todo_name"]
            description = objective["description"]
            start_time = parse_datetime_string(objective["start_time"])
            end_time = parse_datetime_string(objective["end_time"])

            for day in objective_days:
                # Find the date for the upcoming day (next occurrence)
                current_day = datetime.now()
                while current_day.strftime("%A") != day:
                    current_day += timedelta(days=1)

                # Set the start and end datetime for the todo
                start_datetime = current_day.replace(hour=start_time.hour, minute=start_time.minute)
                end_datetime = current_day.replace(hour=end_time.hour, minute=end_time.minute)

                create_url = "https://api.notion.com/v1/pages"
                data = {
                    "Objective": {"title": [{"text": {"content": objective_name}}]},
                    "Completed": {"checkbox": False},
                    "Date": {
                        "date": {
                            "start": start_datetime.isoformat(),
                            "end": end_datetime.isoformat(),
                            "time_zone": str(tzlocal.get_localzone_name())
                        }
                    },
                    "Description": {
                        "rich_text": [{
                            "type": "text",
                            "text": {"content": description}
                        }]
                    }
                }
                payload = {"parent": {"database_id": self.database_id}, "properties": data}

                res = requests.post(create_url, headers=self.headers, json=payload)
                status_code = res.status_code

        if status_code == 200:
            return json.dumps("Success")
        else:
            return json.dumps("An error occurred")

    def update_todo(self, todos):
        status_code = 0
        for todo in todos:
            todo_id = todo["todo_id"]
            todo_status = todo["todo_status"] == "Completed"
            payload = {"properties": {"Completed": {"checkbox": todo_status}}}
            url = f"https://api.notion.com/v1/pages/{todo_id}"
            res = requests.patch(url, json=payload, headers=self.headers)
            status_code = res.status_code

        if status_code == 200:
            return json.dumps("Success")
        else:
            return json.dumps("An error occurred")
