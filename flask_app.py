"""Minimal Flask dashboard for BLE scans."""

import asyncio
import signal
import sqlite3
from typing import List

from flask import Flask, redirect, render_template_string, request, url_for

from config import DB_PATH
from core.utils import setup_logging

setup_logging()
app = Flask(__name__)

STOP_EVENT: asyncio.Event | None = None

TEMPLATE = """
<!doctype html>
<meta http-equiv="refresh" content="5">
<title>BLE Logs</title>
<h1>Recent Devices</h1>
<table border=1>
<tr><th>MAC</th><th>Vendor</th><th>Last Seen</th><th>RSSI</th></tr>
{% for d in devices %}
<tr><td>{{ d.mac }}</td><td>{{ d.vendor }}</td><td>{{ d.last_seen }}</td><td>{{ d.rssi }}</td></tr>
{% endfor %}
</table>
"""


@app.route("/")
def index():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        "SELECT mac, vendor, last_seen, json_extract(rssi_history, '$[-1].rssi') as rssi FROM devices ORDER BY last_seen DESC LIMIT 20"
    )
    devices = cur.fetchall()
    conn.close()
    return render_template_string(TEMPLATE, devices=devices)


@app.get("/history")
def history():
    page = int(request.args.get("page", "1"))
    per_page = 20
    offset = (page - 1) * per_page
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        "SELECT mac, vendor, last_seen FROM devices ORDER BY last_seen DESC LIMIT ? OFFSET ?",
        (per_page, offset),
    )
    rows = cur.fetchall()
    conn.close()
    next_url = url_for("history", page=page + 1)
    prev_url = url_for("history", page=page - 1) if page > 1 else None
    html = (
        "<h1>History</h1><ul>"
        + "".join(
            f"<li>{r['mac']} - {r['vendor']} - {r['last_seen']}</li>" for r in rows
        )
        + "</ul>"
    )
    html += f'<a href="{next_url}">Next</a>'
    if prev_url:
        html += f' | <a href="{prev_url}">Prev</a>'
    return html


@app.route("/shutdown")
def shutdown():
    if STOP_EVENT:
        STOP_EVENT.set()
    else:
        signal.raise_signal(signal.SIGINT)
    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
