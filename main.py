import hashlib
import math
import os
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib.dates as mdates
from flask import Flask, request, url_for
from flask_caching import Cache
from matplotlib.figure import Figure

app = Flask(__name__)

# Configure caching
cache = Cache(app, config={"CACHE_TYPE": "simple", "CACHE_DEFAULT_TIMEOUT": 60})

# hash of this file
src_hash = hashlib.md5(Path(__file__).read_bytes(), usedforsecurity=False).hexdigest()

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
        <h1 class="text-xl font-bold text-center mb-8">Interactive Matplotlib Graphs</h1>
        <form hx-post="/plot" hx-target="#plot" class="mb-8" hx-indicator="#loading">
            <div class="mb-4">
                <label class="block mb-2">Number of days</label>
                <input type="number" name="number" placeholder="Enter a number" class="w-full p-2 border border-gray-300 rounded" value="10">
            </div>
            <div class="mb-4">
                <label class="block mb-2">Text</label>
                <input type="text" name="text" placeholder="Enter a text" class="w-full p-2 border border-gray-300 rounded" value="Cookie production at Cookie Monster Inc.">
            </div>
            <div class="mb-4">
                <label class="block mb-2">Date</label>
                <input type="date" name="date" class="w-full p-2 border border-gray-300 rounded" value="2024-01-01">
            </div>
            <button type="submit" class="w-full p-3 border border-gray-300 rounded bg-blue-500 text-white hover:bg-blue-600">Generate Plot</button>
        </form>
        <div id="loading" class="py-2 htmx-indicator text-center text-gray-500">Loading...</div>
        <div id="plot" class="bg-white p-4 rounded-lg shadow-lg flex justify-center align-center">
            <span class="opacity-50">Submit the form to generate the plot</span>
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
        f"{number}{text}{date}{src_hash}".encode(), usedforsecurity=False
    ).hexdigest()
    file_path = img_folder / f"plot_{file_hash}.png"

    if not os.path.exists(file_path):
        print(f"Generating plot... ({number=}, {text=}, {date=})")
        fig = Figure()
        axis = fig.add_subplot(1, 1, 1)

        # Creating a range of dates around the input date
        dates = [date + timedelta(days=i) for i in range(0, number)]
        values = [1 + math.sin(number + i) + i / 10 for i in range(0, number)]

        axis.plot(dates, values)
        axis.set_title(text)
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
    return f'<img src="{url_for("static", filename=str(plot_path)[7:])}" alt="Plot Image"/>'


if __name__ == "__main__":
    app.run(debug=True)
