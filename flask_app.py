from flask import Flask, render_template_string
import sqlite3
from core.utils import setup_logging
from config import DB_PATH

setup_logging()
app = Flask(__name__)

TEMPLATE = """
<!doctype html>
<title>BLE Logs</title>
<h1>Recent Devices</h1>
<table border=1>
<tr><th>MAC</th><th>Name</th><th>Last Seen</th><th>RSSI</th></tr>
{% for d in devices %}
<tr><td>{{ d[0] }}</td><td>{{ d[1] }}</td><td>{{ d[2] }}</td><td>{{ d[3] }}</td></tr>
{% endfor %}
</table>
"""


@app.route("/")
def index():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT mac_address, device_name, last_seen, rssi FROM Devices ORDER BY last_seen DESC LIMIT 20"
    )
    devices = cur.fetchall()
    conn.close()
    return render_template_string(TEMPLATE, devices=devices)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
