import hashlib
import hmac
from flask import Flask, abort, request
import os
import subprocess
import threading
from bot import notify_telegram 

app = Flask(__name__)
print(app.name)

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

        def run_deploy():
            # ? pull changes container
            notify_telegram("🚀 *CI/CD triggered for BACKEND*")
            subprocess.run(
                ["git", "pull", "origin", "master"],
                cwd="/projects/the-menu-backend",
            )
            notify_telegram("✅ *Git pull successful*")

            # ? run 
            print("RUNNING CONTAINER")
            subprocess.run(
                ["docker-compose", "up", "-d", '--build'],
                cwd="/projects/the-menu-backend",
            )
            notify_telegram("🐳 *Docker containers restarted*")

            # ? makemigrations 
            print("RUNNING MAKEMIGRATIONS COMMAND")
            subprocess.run(
                ["docker", "exec", "the-menu-backend-server-1", "python3", "manage.py", "makemigrations"],
                cwd="/projects/the-menu-backend",
            )
            # ? migrate
            print("RUNNING MIGRATE COMMAND")
            subprocess.run(
                ["docker", "exec", "the-menu-backend-server-1", "python3", "manage.py", "migrate"],
                cwd="/projects/the-menu-backend",
            )
            notify_telegram("🎉 *Migrations applied successfully*")
            notify_telegram("✅ *CI/CD for BACKEND completed successfully*")

        
        threading.Thread(target=run_deploy).start()

        return "Backend ci-cd event received and processed", 200
    else:
        notify_telegram(f"❌ *CI/CD failed*: `{e}`")
        return "Invalid request method", 405


@app.route("/frontend", methods=["POST"])
def frontend_event():
    verify_secret(request)
    notify_telegram("🚀 *CI/CD triggered for FRONTEND*")

    def run_deploy():
        try:
            subprocess.run(["git", "pull", "origin", "main"], cwd="/root/the-menu-frontend", check=True)
            subprocess.run(["docker-compose", "up", "-d", "--build"], cwd="/root/the-menu-frontend", check=True)
            notify_telegram("✅ *CI/CD for FRONTEND completed successfully*")
        except subprocess.CalledProcessError as e:
            notify_telegram(f"❌ *CI/CD for FRONTEND failed:*\n`{e}`")

    threading.Thread(target=run_deploy).start()
    return "Frontend CI/CD event received and processing in background", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9999)
