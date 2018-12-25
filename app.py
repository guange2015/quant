#coding=utf-8

import flask
from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return """
    <ul>
    <li><a href="/datas/bchusdt.csv">bchusdt</a></li>
    <li><a href="/datas/btcusdt.csv">btcusdt</a></li>
    <li><a href="/datas/eosusdt.csv">eosusdt</a></li>
    <li><a href="/datas/ethusdt.csv">ethusdt</a></li>
    </ul> 
    """


@app.route("/datas/<path:filename>")
def download(filename):
    return flask.send_from_directory('datas',filename, mimetype="text/csv")
