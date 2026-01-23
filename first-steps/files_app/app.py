import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

TASKS_FILE = "tasks.txt"
tasks = []
next_id = 1


# Функция для загрузки задач из файла
def load_tasks():
    global tasks, next_id
    try:
        with open(TASKS_FILE, "r") as f:
            tasks = json.load(f)
            if tasks:
                next_id = max(task["id"] for task in tasks) + 1
    except FileNotFoundError:
        tasks = []


# Функция для сохранения задач в файл
def save_tasks():
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=2)


# Класс обработчика HTTP-запросов
class TodoHandler(BaseHTTPRequestHandler):

    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-type", content_type)
        self.end_headers()

    # Обработка GET-запросов
    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path.rstrip('/') == "/tasks":
            # обработка GET

            self._set_headers()
            self.wfile.write(json.dumps(tasks).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

    # Обработка POST-запросов
    def do_POST(self):
        global next_id
        parsed_path = urlparse(self.path)
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)

        if parsed_path.path == "/tasks":
            # Создание новой задачи
            try:
                data = json.loads(post_data)
                title = data["title"]
                priority = data["priority"]
                task = {
                    "title": title,
                    "priority": priority,
                    "isDone": False,
                    "id": next_id
                }
                tasks.append(task)
                next_id += 1
                save_tasks()
                self._set_headers(200)
                self.wfile.write(json.dumps(task).encode())
            except (KeyError, json.JSONDecodeError):
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid data"}).encode())

        elif parsed_path.path.startswith("/tasks/") and parsed_path.path.endswith("/complete"):
            # Отметка задачи как выполненной
            try:
                task_id_str = parsed_path.path.split("/")[2]
                task_id = int(task_id_str)
                task = next((t for t in tasks if t["id"] == task_id), None)
                if task:
                    task["isDone"] = True
                    save_tasks()
                    self._set_headers(200)
                    self.wfile.write(b'')
                else:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "Task not found"}).encode())
            except (IndexError, ValueError):
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid task id"}).encode())

        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())


def run(server_class=HTTPServer, handler_class=TodoHandler, port=8000):
    load_tasks()
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Server running on port {port}...")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
