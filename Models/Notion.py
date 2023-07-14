import requests, json
from datetime import datetime, timezone
from dateutil.parser import parse


def parse_date_string(date_string):
    parsed_date = parse(date_string)
    iso_date = parsed_date.isoformat()
    return iso_date


class Notion:
    def __init__(self):
        with open("keys/NOTION_API_KEY.txt") as key:
            self.notion_api_key = key.readline()

        self.database_id = "458c081d551547e496c1a0bee74763df"
        self.headers = {
            "Authorization": "Bearer " + self.notion_api_key,
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }

    def get_todos(self, include_id=False):
        url = f"https://api.notion.com/v1/databases/{self.database_id}/query"

        payload = {"page_size": 100}
        res = requests.post(url, json=payload, headers=self.headers)
        # print(f"get_todos status code: {res.status_code}")
        data = res.json()

        result = data["results"]
        todos = []
        for todo in result:
            id = todo["id"]
            status = todo["properties"]["Status"]["status"]["name"]
            objective = todo["properties"]["Objective"]["title"][0]["text"]["content"]
            # todos.append(f"Todo name: {objective}. Todo ID: {id}")
            if include_id:
                todos.append((objective, id))
            else:
                todos.append(objective)
        return todos

    def create_todo(self, objectives):
        status_code = 0
        for objective in objectives:
            objective_name = objective["todo_name"]
            start_time = parse_date_string(objective["start_time"])
            end_time = parse_date_string(objective["end_time"])
            create_url = "https://api.notion.com/v1/pages"
            data = {
                "Objective": {"title": [{"text": {"content": objective_name}}]},
                "Status": {"status": {"name": "Not started"}},
                "Date": {"date": {"start": start_time, "end": end_time}}
            }
            payload = {"parent": {"database_id": self.database_id}, "properties": data}

            res = requests.post(create_url, headers=self.headers, json=payload)
            status_code = res.status_code
            # print(f"create_todo status code: {res.status_code}")
            # print(f"create_todo {res}")
        if status_code == 200:
            return json.dumps("Success")
        else:
            return json.dumps("An error occurred")

    def update_todo(self, todos):
        status_code = 0
        for todo_tuple in todos:
            name = todo_tuple["todo_name"]
            status = todo_tuple["todo_status"]
            for todo in self.get_todos(include_id=True):
                if todo[0] == name:
                    url = f"https://api.notion.com/v1/pages/{todo[1]}"

                    payload = {"properties": {"Status": {"status": {"name": status}}}}

                    res = requests.patch(url, json=payload, headers=self.headers)
                    status_code = res.status_code
                    # print(f"update_todo status code: {res.status_code}")
        if status_code == 200:
            return json.dumps("Success")
        else:
            return json.dumps("An error occurred")
