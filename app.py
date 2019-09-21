from flask import Flask, request, jsonify, make_response, render_template;
from flask_pymongo import PyMongo
from HPchatbot import readContents, words, find
from datetime import datetime
from bson import ObjectId

app = Flask(__name__);
app.config["MONGO_URI"] = "mongodb://localhost:27017/myDatabase";
mongo = PyMongo(app);

questions, answers = readContents();
words,stop_words, doc_text,ps = words(questions);

@app.route("/", methods=["GET"])
def home():
    cookie = request.cookies.get('HPE')
    first = False;
    if (cookie != None):
        user = mongo.db.user.find_one({"_id": ObjectId(cookie)});
        print(user);
        if (user == None):
            user = mongo.db.user.insert_one({"_id":ObjectId(cookie), "queries":[]});
            user = user.inserted_id;
            first = True;
            if (user==None):
                done = True;
            else:
                done = False;
            queries=[]
        else:
            queries = user['queries'];
    else:
        user = mongo.db.user.insert_one({"_id":ObjectId(cookie), "queries":[]});
        user = user.inserted_id;
        first = True;
        if (user == None):
            done = True;
        else:
            done = False;
        queries=[];
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    resp = make_response(render_template("index.html", preview=queries, length=len(queries), time = current_time))
    if (first):
        print(user)
        resp.set_cookie('HPE',str(user));    
    return resp 

@app.route("/getResponse", methods=["POST","GET"])
def findQuery():
    cookie = request.cookies.get('somecookiename')
    data = request.get_json();
    if (cookie != None):
        user = mongo.db.user.update_one({"_id":ObjectId(cookie)},{'$addToSet':{'queries':data["data"]}});
        print(user)
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

@app.route("/satisfied", methods=["POST"])
def dislike():
    data = request.get_json();
    like = mongo.db.dislike.update_one({'answer':data["data"]},{'$inc':"dislikes"});
    if(like == None):
        return jsonify(
            success=False
        )
    else:
        return jsonify(
            success=True
        )