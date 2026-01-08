import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

TASKS_FILE = "tasks.txt"
ALLOWED_PRIORITIES = {"low", "normal", "high"}

tasks = []
next_id = 1


def load_tasks():
    "Загружает задачи из файла при старте сервера"
    global tasks, next_id
    if not os.path.exists(TASKS_FILE):
        return

    try:
        with open(TASKS_FILE, encoding="utf-8") as f:
            tasks[:] = json.load(f)
        next_id = max((t["id"] for t in tasks), default=0) + 1
    except (OSError, json.JSONDecodeError):
        tasks[:] = []
        next_id = 1


def save_tasks():
    "Сохраняет задачи в файл"
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)


def find_task(task_id):
    "Ищет задачу по id"
    return next((t for t in tasks if t["id"] == task_id), None)


class Handler(BaseHTTPRequestHandler):

    def send_json(self, data, code=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(body)

    def send_empty(self, code):
        self.send_response(code)
        self.end_headers()

    def do_GET(self):
        if self.path == "/tasks":
            self.send_json(tasks)
        else:
            self.send_empty(404)

    def do_POST(self):

        # Создание задачи
        if self.path == "/tasks":
            length = int(self.headers.get("Content-Length", 0))
            if length == 0:
                self.send_empty(400)
                return

            try:
                data = json.loads(self.rfile.read(length))
            except json.JSONDecodeError:
                self.send_empty(400)
                return

            title = data.get("title")
            priority = data.get("priority")

            if not isinstance(title, str) or priority not in ALLOWED_PRIORITIES:
                self.send_empty(400)
                return

            global next_id
            task = {
                "id": next_id,
                "title": title,
                "priority": priority,
                "isDone": False
            }
            next_id += 1

            tasks.append(task)
            save_tasks()
            self.send_json(task, 200)
            return

        # Отметка задачи как выполненна
        if self.path.startswith("/tasks/") and self.path.endswith("/complete"):
            try:
                task_id = int(self.path.split("/")[2])
            except ValueError:
                self.send_empty(404)
                return

            task = find_task(task_id)
            if not task:
                self.send_empty(404)
                return

            task["isDone"] = True
            save_tasks()
            self.send_empty(200)
            return

        self.send_empty(404)


if __name__ == "__main__":
    load_tasks()
    server = HTTPServer(("0.0.0.0", 8000), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
