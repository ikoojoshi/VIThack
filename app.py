from flask import Flask, request, jsonify, make_response, render_template;
from flask_pymongo import PyMongo
from HPchatbot import readContents, words, find
from datetime import datetime

app = Flask(__name__);
app.config["MONGO_URI"] = "mongodb://localhost:27017/myDatabase";
mongo = PyMongo(app);

questions, answers = readContents();
words,stop_words, doc_text,ps = words(questions);

@app.route("/", methods=["GET"])
def home():
    cookie = request.cookies.get('somecookiename')
    first = False;
    if (cookie != None):
        user = mongo.db.users.find_one({"user": cookie});
        if (user == None):
            user = mongo.db.user.insert_one({"user":request.remote_addr, "queries":[]});
            user = user.inserted_id;
            first = True;
            if (len(user)>0):
                done = True;
            else:
                done = False;
            queries=[]
        else:
            queries = user['queries'];
    else:
        user = mongo.db.user.insert_many([{"user":request.remote_addr, "queries":[]}]);
        user = user.inserted_ids;
        first = True;
        if (len(user)>0):
            done = True;
        else:
            done = False;
        preview=[];
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    resp = make_response(render_template("index.html", preview=queries, length=len(queries), time = current_time))
    if (first):
        resp.set_cookie('HPE',str(user[0]));    
    return resp 

@app.route("/getResponse", methods=["POST","GET"])
def findQuery():
    cookie = request.cookies.get('somecookiename')
    data = request.get_json();
    if (cookie != None):
        user = mongo.db.user.update_one({"user":cookie,"$push":{"queries":data["data"]}});
        answer,top = find(data["data"],stop_words,doc_text,answers,questions,ps)
        done = True;
    else:
        answer,top = find(data["data"],stop_words,doc_text,answers,questions,ps)
        done = True;
    return jsonify(
        status=200,
        success=done,
        answer=answer,
        preview=top
    )