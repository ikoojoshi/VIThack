from flask import Flask, request, jsonify, make_response, render_template;
from flask_pymongo import PyMongo
from HPchatbot import readContents, words, find
from datetime import datetime
from bson import ObjectId
import json
from recommendation import generate_recommendations
from pandas import read_csv,DataFrame;

app = Flask(__name__);
app.config["MONGO_URI"] = "mongodb://localhost:27017/myDatabase";
mongo = PyMongo(app);

questions, answers = readContents();
words,stop_words, doc_text,ps = words(questions);

listt=[];
for i in range(len(questions)):
    listt.append({
        "question": questions[i],
        "questionID":i,
        "visits":0
    })
@app.route("/", methods=["GET"])
def home():
    cookie = request.cookies.get('HPE')
    first = False;
    if (cookie != None):
        user = mongo.db.user.find_one({"_id": ObjectId(cookie)});
        if (user == None):
            user = mongo.db.user.insert_one({"queries":listt});
            user = user.inserted_id;
            first = True;
            if (user==None):
                done = True;
            else:
                done = False;
            queries=[
                "What are the advantages of HPE OneView?","What is a software-defined approach to lifecycle management?"
            ];
        else:
            try:
                userID=[]
                questionID=[]
                visits=[]
                queries = user['queries'];
                ques = []
                for i in range(0,len(questions)):
                    ques.append({
                        "questionID":i,
                        "question":questions[i]
                    })
                for i in queries:
                    userID.append(str(user['_id']));
                    questionID.append(i['questionID'])
                    visits.append(i['visits'])
                users = mongo.db.user.find();
                for i in users:
                    id = str(i["_id"]);
                    ques = i["queries"];
                    if (id!=cookie):
                        for j in ques:
                            userID.append(str(id));
                            questionID.append(j['questionID'])
                            visits.append(j['visits'])
                data = DataFrame({"userID":userID,"questionID":questionID,"visits":visits})
                ques = DataFrame({"questionID":ques})
                queries = generate_recommendations(cookie, 3, data, ques)
            except:
                queries=[
                    "What are the advantages of HPE OneView?","What is a software-defined approach to lifecycle management?"
                ]; 
                # answer,queries = find(queries[-1],stop_words,doc_text,answers,questions,ps)
            
    else:
        user = mongo.db.user.insert_one({"queries":listt});
        user = user.inserted_id;
        first = True;
        if (user == None):
            done = True;
        else:
            done = False;
        queries=[
            "What are the advantages of HPE OneView?","What is a software-defined approach to lifecycle management?"
        ];
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    resp = make_response(render_template("index.html", preview=queries, length=len(queries), time = current_time))
    if (first):
        resp.set_cookie('HPE',str(user));    
    return resp 

@app.route("/getResponse", methods=["POST","GET"])
def findQuery():
    cookie = request.cookies.get('HPE')
    data = request.get_json();
    if (cookie != None):
        question,answer,top = find(data["data"],stop_words,doc_text,answers,questions,ps)
        user = mongo.db.user.update_one({"_id":ObjectId(cookie), 'queries.question': question},{'$inc':{'queries.$.visits':1}});
        try:
            user = mongo.db.user.find_one({"_id":ObjectId(cookie)});
            userID=[]
            questionID=[]
            visits=[]
            queries = user['queries'];
            ques = []
            for i in range(0,len(questions)):
                ques.append(
                    {"questionID":i}
                )
            for i in queries:
                userID.append(str(user['_id']));
                questionID.append(i['questionID'])
                visits.append(i['visits'])
            users = mongo.db.user.find();
            for i in users:
                id = i["_id"];
                ques = i["queries"];
                if (id!=cookie):
                    for j in ques:
                        userID.append(str(id));
                        questionID.append(j['questionID'])
                        visits.append(j['visits'])
            data = DataFrame({"userID":userID,"questionID":questionID,"visits":visits})
            ques = DataFrame({"questionID":ques})
            queries = generate_recommendations(cookie, 3, data, ques)
            print(queries);
        except:
            print('err');
            queries = top;
        done = True;
    else:
        answer,top = find(data["data"],stop_words,doc_text,answers,questions,ps)
        done = True;
        queries = top;
    return jsonify(
        status=200,
        success=done,
        answer=answer,
        preview=queries
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

if __name__ == '__main__':
    app.run(debug=True, port=3000)