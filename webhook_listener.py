import hashlib
import hmac
from flask import Flask, abort, request
import os
import subprocess

app = Flask(__name__)


SECRET_KEY = "fvGL5puCNg7Lud4X"


def verify_secret(request):
    signature = request.headers.get("X-Hub-Signature-256")
    if not signature:
        abort(403)

    _, signature = signature.split("=")
    mac = hmac.new(SECRET_KEY.encode(), msg=request.data, digestmod=hashlib.sha1)
    if not hmac.compare_digest(mac.hexdigest(), signature):
        abort(403)


@app.route("/webhook", methods=["POST"])
def webhook_event():
    verify_secret(request)
    if request.method == "POST":
        subprocess.run(["git", "pull"], cwd="/home/allplay/internetbor-ru-backend")

        subprocess.run(
            ["sudo", "docker", "compose", "up", "-d"],
            cwd="/home/allplay/internetbor-ru-backend",
        )

        return "Webhook event received and processed", 200
    else:
        return "Invalid request method", 405


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9999)
