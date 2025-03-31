import hashlib
import hmac
from flask import Flask, abort, request
import os
import subprocess

app = Flask(__name__)


SECRET_KEY = "fvGL5puCNg7Lud4X"


def verify_secret(request):
    signature = request.headers.get("X-Hub-Signature-256")
    if signature is None:
        abort(403)

    # Validate format: sha256=<signature>
    try:
        algo, signature = signature.split("=")
        if algo != "sha256":
            abort(403)
    except ValueError:
        abort(403)

    # Compute HMAC with raw payload
    payload = request.get_data(as_text=False)
    mac = hmac.new(SECRET_KEY.encode(), msg=payload, digestmod=hashlib.sha256)

    # Debugging
    computed_signature = mac.hexdigest()
    print(f"Computed: {computed_signature}")
    print(f"Received: {signature}")

    # Compare signatures
    if not hmac.compare_digest(computed_signature, signature):
        abort(403)


@app.route("/backend", methods=["POST"])
def backend_event():
    verify_secret(request)
    if request.method == "POST":
        # ? pull changes
        subprocess.run(["git", "pull"], cwd="/root/the-menu-backend")

        # ? run container
        subprocess.run(
            ["sudo", "docker-compose", "exec", "-T", "the-menu-backend_server_1", "git", "pull"],
            cwd="/root/the-menu-backend",
        )
        # ? makemigrations 
        subprocess.run(
            ["sudo", "docker-compose", "exec", "-T", "the-menu-backend_server_1", "python3", "manage.py", "makemigrations"],
            cwd="/root/the-menu-backend",
        )
        # ? migrate
        subprocess.run(
            ["sudo", "docker-compose", "exec", "-T", "the-menu-backend_server_1", "python3", "manage.py", "migrate"],
            cwd="/root/the-menu-backend",
        )

        return "Backend ci-cd event received and processed", 200
    else:
        return "Invalid request method", 405


@app.route("/frontend", methods=["POST"])
def frontend_event():
    verify_secret(request)
    if request.method == "POST":
        subprocess.run(["git", "pull"], cwd="/root/the-menu-backend")

        subprocess.run(
            ["sudo", "yarn", "build", "&&", "sudo", "yarn", "generate"],
            cwd="/root/the-menu-backend",
        )

        return "Frontend ci-cd event received and processed", 200
    else:
        return "Invalid request method", 405


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9999)
