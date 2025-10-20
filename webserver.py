from flask import Flask, render_template_string, request, redirect, url_for
from config import watched_metrics_file

app = Flask(__name__)

# Shared in-memory state
watched_metrics_names = []

def load_watched_metrics():
    try:
        with open(watched_metrics_file, "r") as f:
            return [m.strip() for m in f.read().splitlines() if m.strip()]
    except FileNotFoundError:
        return []

def save_watched_metrics(metrics):
    with open(watched_metrics_file, "w") as f:
        f.write("\n".join(metrics))

@app.route("/")
def index():
    html = """
    <h1>OBD2 Display Controller</h1>
    <h3>Currently Watched Metrics:</h3>
    <ul>
    {% for metric in watched %}
        <li>{{ metric }}</li>
    {% endfor %}
    </ul>

    <form action="/update" method="post">
        <label for="metrics">Enter metrics (comma separated):</label><br>
        <input type="text" id="metrics" name="metrics" value="{{ ','.join(watched) }}">
        <br><br>
        <input type="submit" value="Update">
    </form>
    """
    return render_template_string(html, watched=watched_metrics_names)

@app.route("/update", methods=["POST"])
def update():
    global watched_metrics_names
    metrics_str = request.form.get("metrics", "")
    watched_metrics_names = [m.strip() for m in metrics_str.split(",") if m.strip()]
    save_watched_metrics(watched_metrics_names)  # persist to disk
    return redirect(url_for("index"))

def run_webserver():
    global watched_metrics_names
    watched_metrics_names = load_watched_metrics()  # load from file at startup
    app.run(host="0.0.0.0", port=5000, debug=False)

def get_watched_metrics_names():
    global watched_metrics_names
    return watched_metrics_names

def set_watched_metrics_names(new_list):
    global watched_metrics_names
    watched_metrics_names = new_list
    save_watched_metrics(new_list)