import requests
from flask import Flask, render_template

app = Flask(__name__)


YANDEX_TOKEN = "0c4181a7c2cf4521964a72ff57a34a07"
DISK_PATH = "disk:/"

def get_all_uploaded_filenames():
    headers = {"Authorization": f"OAuth {YANDEX_TOKEN}"}
    url = f"https://cloud-api.yandex.net/v1/disk/resources?path={DISK_PATH}&limit=100"
    uploaded_files = []

    while url:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print("Ошибка:", response.status_code)
            break
        data = response.json()
        items = data.get("_embedded", {}).get("items", [])
        for item in items:
            if item["type"] == "file":
                uploaded_files.append(item["name"])
        next_link = data.get("_embedded", {}).get("_links", {}).get("next")
        url = next_link["href"] if next_link else None

    return uploaded_files

@app.route("/")
def index():
    possible_files = ["photo.jpg", "report.pdf", "notes.txt", "diagram.png"]
    uploaded = get_all_uploaded_filenames()
    return render_template("index.html", files=possible_files, uploaded_files=uploaded)

if __name__ == "__main__":
    app.run(debug=True)