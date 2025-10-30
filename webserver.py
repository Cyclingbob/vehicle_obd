from flask import Flask, render_template_string, request, redirect, url_for
from config import watched_metrics_file
from metrics import our_metrics

app = Flask(__name__)

# Shared in-memory state
watched_metrics_names = []

def load_watched_metrics():
    try:
        with open(watched_metrics_file, "r") as f:
            return [m.strip() for m in f.readlines() if m.strip()]
    except FileNotFoundError:
        return []

def save_watched_metrics(metrics):
    with open(watched_metrics_file, "w") as f:
        f.write("\n".join(metrics))

def getAllMetrics():
    return sorted(list(our_metrics.keys()))

@app.route("/")
def index():
    all_metrics = sorted(getAllMetrics())
    html = """
    <h1>OBD2 Display Controller</h1>

    <form action="/update" method="post">
        <h3>Select Metrics to Display:</h3>
        <div style="column-count: 3;">
        {% for metric in all_metrics %}
            <label>
                <input type="checkbox" name="metrics" value="{{ metric }}"
                    {% if metric in watched %}checked{% endif %}>
                {{ metric }}
            </label><br>
        {% endfor %}
        </div>
        <br>
        <input type="submit" value="Update">
    </form>
    """
    return render_template_string(html,
                                  watched=watched_metrics_names,
                                  all_metrics=all_metrics)

@app.route("/update", methods=["POST"])
def update():
    global watched_metrics_names
    # Get list of selected checkboxes
    selected = request.form.getlist("metrics")
    watched_metrics_names = selected
    save_watched_metrics(selected)
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