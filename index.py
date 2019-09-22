from flask import Flask, request, jsonify, make_response, render_template;
from flask_pymongo import PyMongo
from HPchatbot import readContents, words, find
from datetime import datetime
from bson import ObjectId
import json
from recommendation import generate_recommendations
from pandas import read_csv,DataFrame;

app = Flask(__name__)
@app.route("/",methods=["GET"])
def home():
    resp = make_response(render_template("index.html"))
    return resp

if __name__ == '__main__':
    app.run(debug=True, port=3000)