# from pymongo import MongoClient;
# from bson import ObjectId;

# fo
from pymongo import MongoClient
from HPchatbot import readContents, words, find

client = MongoClient('mongodb://localhost:27017/myDatabase')
questions, answers = readContents();

for i in range(len(questions)):
    aa = client.db.dislike.insert_one({"question":questions[i],"answer":answers[i],"dislikes":0})