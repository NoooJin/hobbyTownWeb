from flask import Blueprint, render_template

from pymongo import MongoClient


bp = Blueprint('main', __name__, url_prefix='/')


@bp.route('/')
def hello_pybo():
    return 'Hello, Pybo!'


@bp.route('/mongo', methods=('POST', 'GET'))
def mongoTest():
    client = MongoClient("localhost", 27017)
    db = client.test_db

    return render_template('test.html')