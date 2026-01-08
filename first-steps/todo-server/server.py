import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

TASKS_FILE = "tasks.txt"

tasks = []
next_id = 1


def load_tasks():
    global tasks, next_id
    if not os.path.exists(TASKS_FILE):
        return

    try:
        with open(TASKS_FILE, encoding="utf-8") as f:
            tasks[:] = json.load(f)

        next_id = max((t["id"] for t in tasks), default=0) + 1

    except Exception:
        tasks[:] = []
        next_id = 1


def save_tasks():
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False)


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
            if self.path != "/tasks":
                self.send_empty(404)
            else:
                self.send_json(tasks, 200)

    def do_POST(self):
        #  создать задачу
        if self.path == "/tasks":
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length))

            global next_id
            task = {
                "title": data["title"],
                "priority": data["priority"],
                "isDone": False,
                "id": next_id
            }
            next_id += 1

            tasks.append(task)
            save_tasks()

            self.send_json(task, 200)
            return

        #  отметить выполненной
        if self.path.startswith("/tasks/") and self.path.endswith("/complete"):
            try:
                task_id = int(self.path.split("/")[2])
            except ValueError:
                self.send_empty(404)
                return

            for task in tasks:
                if task["id"] == task_id:
                    task["isDone"] = True
                    save_tasks()
                    self.send_empty(200)
                    return

            self.send_empty(404)
            return

        self.send_empty(404)


if __name__ == "__main__":
    load_tasks()
    server = HTTPServer(("0.0.0.0", 8000), Handler)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


