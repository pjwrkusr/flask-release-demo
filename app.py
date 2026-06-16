from flask import Flask, jsonify, render_template
import os

app = Flask(__name__)

APP_NAME = os.getenv("APP_NAME", "flask-release-demo")
APP_VERSION = os.getenv("APP_VERSION", "0.0.1")

@app.route("/")
def home():
    return render_template("index.html", app_name=APP_NAME, app_version=APP_VERSION)

@app.route("/health")
def health():
    return jsonify({
        "status": "UP",
        "application": APP_NAME,
        "version": APP_VERSION
    })

@app.route("/version")
def version():
    return jsonify({
        "application": APP_NAME,
        "version": APP_VERSION
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)