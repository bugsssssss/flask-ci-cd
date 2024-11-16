from flask import Flask, request
import os
import subprocess

app = Flask(__name__)


@app.route("/webhook", methods=["GET"])
def webhook_event():
    if request.method == "GET":
        subprocess.run(["git", "pull"], cwd="/home/allplay/internetbor-ru-backend")

        subprocess.run(
            ["sudo", "docker-compose", "up", "-d"],
            cwd="/home/allplay/internetbor-ru-backend",
        )

        return "Webhook event received and processed", 200
    else:
        return "Invalid request method", 405


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9999)
