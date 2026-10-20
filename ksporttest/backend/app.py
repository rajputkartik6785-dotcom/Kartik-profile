from flask import Flask, request, jsonify, send_from_directory
import os
import socket
import ipaddress

app = Flask(__name__)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND = os.path.join(BASE, "frontend")


@app.route("/")
def home():
    return send_from_directory(FRONTEND, "index.html")


@app.route("/<path:file>")
def frontend_files(file):
    if file in ("style.css", "script.js"):
        return send_from_directory(FRONTEND, file)
    return "Not found", 404


@app.route("/api/scan", methods=["POST"])
def scan():
    data = request.get_json(silent=True) or {}
    host = str(data.get("host", "127.0.0.1")).strip()

    try:
        ip = ipaddress.ip_address(host)

        if not isinstance(ip, ipaddress.IPv4Address):
            raise ValueError()

        if not (ip.is_private or ip.is_loopback):
            return jsonify(error="Use localhost or a private IP."), 400

        start = int(data.get("start", 1))
        end = int(data.get("end", 100))

        if start < 1 or end > 65535 or start > end or end - start >= 100:
            return jsonify(error="Choose a valid range of up to 100 ports."), 400

    except (ValueError, TypeError):
        return jsonify(error="Invalid IP address or port range."), 400

    results = []

    for port in range(start, end + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.2)
            status = "Open" if s.connect_ex((str(ip), port)) == 0 else "Closed"

        results.append({"port": port, "status": status})

    return jsonify(host=str(ip), results=results)


if __name__ == "__main__":
    app.run(debug=True)