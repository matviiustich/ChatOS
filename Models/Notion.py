import requests, json


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

    def get_todos(self):
        url = f"https://api.notion.com/v1/databases/{self.database_id}/query"

        payload = {"page_size": 100}
        res = requests.post(url, json=payload, headers=self.headers)
        print(f"get_todos status code: {res.status_code}")
        data = res.json()

        # with open('db.json', 'w', encoding='utf8') as f:
        #     json.dump(data, f, ensure_ascii=False, indent=4)
        result = data["results"]
        todos = []
        for todo in result:
            status = todo["properties"]["Status"]["status"]["name"]
            objective = todo["properties"]["Objective"]["title"][0]["text"]["content"]
            todos.append((objective, status))
        return todos

    def create_todo(self, objective: str):
        create_url = "https://api.notion.com/v1/pages"
        data = {
            "Objective": {"title": [{"text": {"content": objective}}]},
            "Status": {"status": {"name": "Not started"}}
        }
        payload = {"parent": {"database_id": self.database_id}, "properties": data}

        res = requests.post(create_url, headers=self.headers, json=payload)
        print(f"create_todo status code: {res.status_code}")
        return res

    def update_todo(self, todo_id: str, data: dict):
        url = f"https://api.notion.com/v1/pages{todo_id}"

        payload = {"properties": data}

        res = requests.patch(url, json=payload, headers=self.headers)
        print(f"update_todo status code: {res.status_code}")
        return res
