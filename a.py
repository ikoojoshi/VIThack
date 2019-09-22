# from pymongo import MongoClient;
# from bson import ObjectId;

# fo
from pymongo import MongoClient
from HPchatbot import readContents, words, find

client = MongoClient('mongodb://admin123:admin123@ds353007.mlab.com:53007/mydatabase')
questions, answers = readContents();

user = client.db.user.insert_one({"queries":[]})

for i in range(len(questions)):
    aa = client.db.dislike.insert_one({"question":questions[i],"answer":answers[i],"dislikes":0})