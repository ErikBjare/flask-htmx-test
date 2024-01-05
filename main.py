import hashlib
import os
from datetime import datetime
from pathlib import Path

import matplotlib.dates as mdates
from flask import Flask, request, url_for
from flask_caching import Cache
from matplotlib.figure import Figure

app = Flask(__name__)

# Configure caching
cache = Cache(app, config={"CACHE_TYPE": "simple", "CACHE_DEFAULT_TIMEOUT": 60})

# Ensure there's a folder to store images
img_folder = Path("static/images/cache")
img_folder.mkdir(parents=True, exist_ok=True)

html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Matplotlib with Flask, HTMX, and Tailwind</title>
    <script src="https://unpkg.com/htmx.org"></script>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
</head>
<body class="bg-gray-100">
    <div class="container mx-auto p-8">
        <h1 class="text-xl font-bold text-center mb-4">Interactive Matplotlib Graphs</h1>
        <form hx-post="/plot" hx-target="#plot" class="mb-4">
            <input type="number" name="number" placeholder="Enter a number" class="p-2 border border-gray-300 rounded mr-2">
            <input type="text" name="text" placeholder="Enter a text" class="p-2 border border-gray-300 rounded mr-2">
            <input type="date" name="date" class="p-2 border border-gray-300 rounded mr-2">
            <button type="submit" class="p-2 border border-gray-300 rounded bg-blue-500 text-white">Generate Plot</button>
        </form>
        <div id="plot" class="bg-white p-4 rounded-lg shadow-lg">
            Submit the form to generate the plot.
        </div>
    </div>
</body>
</html>
"""


@app.route("/")
def index():
    return html_template


@cache.memoize()
def generate_plot_path(number, text, date):
    # Generate a unique file name
    file_hash = hashlib.md5(
        f"{number}{text}{date}".encode(), usedforsecurity=False
    ).hexdigest()
    file_path = img_folder / f"plot_{file_hash}.png"

    if not os.path.exists(file_path):
        fig = Figure()
        axis = fig.add_subplot(1, 1, 1)

        # Example plot
        axis.plot([1, 2, 3], [number, number * 2, number * 3])
        axis.set_title(f"{text} on {date}")
        axis.xaxis.set_major_locator(mdates.DayLocator())
        axis.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))

        fig.savefig(file_path)

    return file_path


@app.route("/plot", methods=["POST"])
def plot():
    number = int(request.form.get("number", 1))
    text = request.form.get("text", "")
    date_str = request.form.get("date", datetime.now().strftime("%Y-%m-%d"))
    date = datetime.strptime(date_str, "%Y-%m-%d")

    plot_path = generate_plot_path(number, text, date)
    print(plot_path)
    print(plot_path.name)
    print(str(img_folder))
    print(url_for("static", filename=str(plot_path)[7:]))
    return f'<img src="{url_for("static", filename=str(plot_path)[7:])}" alt="Plot Image"/>'


if __name__ == "__main__":
    app.run(debug=True)
