# import pymongo
# import bcrypt
# import time
# from datetime import datetime
#
# connet_to = pymongo.MongoClient("localhost", 27017)
# mdb = connet_to.base
# collections = mdb.question
#
# def get_next_index(column_name):
#     last_field = column_name.find().sort('idx', -1).limit(1)
#     last_field = list(last_field)[0]['idx'] + 1
#     return last_field
#
# for x in range(1, 200):
#     time.sleep(0.1)
#     subject = '데이터'+str(x)
#     content = '테스트입니다'
#     question_dict = {
#                      'idx': get_next_index(collections),
#                      'user_name': 'woo',
#                      'subject': subject,
#                      'content': content,
#                      'create_date': datetime.now(),
#                      }
#
#     collections.insert_one(question_dict)

# connet_to = pymongo.MongoClient("localhost", 27017)
# mdb = connet_to.base
# columns = mdb.test

# columns.insert_one({'_id':'userid', 'seq': 0})

# def get_next_index(column_name):
#     last_field = column_name.find().sort('idx', -1).limit(1)
#     last_field = list(last_field)[0]['idx'] + 1
#     return last_field
#
# print(get_next_index(columns))

# columns.insert_one({'idx': 1, 'user_id': 'zahara'})
# columns.insert_one({'_id': getNextSequence("userid"),
#                     'name': "Bob C."})

# from datetime import datetime
#
# connet_to = pymongo.MongoClient("localhost", 27017)
# mdb = connet_to.base
# columns = mdb.question
#
# columns.insert_one({'idx': 1, 'subject': '테스트1', 'content': '내용무', 'create_date':datetime.now()})

from datetime import datetime

from flask import Blueprint, url_for, request, render_template, g, flash
from werkzeug.utils import redirect
from pymongo import MongoClient

from hobbytown.forms import AnswerForm

client = MongoClient("localhost", 27017)
db = client.base
user_db = db.user
question_db = db.question
answer_db = db.answer

# def get_next_index(column_name):
#     try:
#         last_field = column_name.find().sort('idx', -1).limit(1)
#         last_field = list(last_field)[0]['idx'] + 1
#     except:
#         last_field = 1
#     return last_field
#
# print(get_next_index(question_db))

### 조건 검색
print(list(question_db.find( {'$or': [{'subject': {'$regex': '바요'}}, {'content': {'$regex': '바요'}}]})))
# print(list(question_db.find({'$and': [ {'title':{'$regex':'안녕'}},{'content':{'$regex':'안녕'}} ]})))