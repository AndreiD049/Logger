from flask import Flask, render_template
import sys
import os

from ..server import ServerJSON, Server, ExecFile

HOST = '127.0.0.1'
PORT = 64322

def create_app():

    app = Flask(__name__)
    
    app.config.from_mapping(
        SECRET_KEY = 'dev'
    )

    app.server = ServerJSON((ExecFile(r"client.py", ["Main"]), ExecFile(r"test.py", [])))

    @app.route("/")
    def index():
        return render_template('index.html')

    @app.route("/getinfo", methods=["POST"])
    def getinfo():
        return app.server.get_messages()

    return app

def run(debug=False):
    create_app().run(host=HOST, port=PORT, debug=debug)

if __name__ == "__main__":
    run()