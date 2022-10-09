from datetime import datetime

from flask import Blueprint, url_for, request, render_template, g, flash
from werkzeug.utils import redirect

from pymongo import MongoClient
from .auth_views import login_required

from hobbytown.forms import AnswerForm

client = MongoClient("localhost", 27017)
db = client.base
user_db = db.user
question_db = db.question
answer_db = db.answer

bp = Blueprint('answer', __name__, url_prefix='/answer')


# 현재 인덱스 번호 + 1 함수
def get_next_index(column_name):
    try:
        last_field = column_name.find().sort('idx', -1).limit(1)
        last_field = list(last_field)[0]['idx'] + 1
    except:
        last_field = 1
    return last_field


@bp.route('/create/<int:question_id>', methods=('POST', ))
@login_required
def create(question_id):
    form = AnswerForm()
    question_dict = question_db.find_one({'idx': question_id})
    if form.validate_on_submit():
        content = request.form['content']
        answer = {
            'idx': get_next_index(answer_db),
            'content': content,
            'user_id': g.user,
            'question_id': question_id,
            'create_date': datetime.now()
        }
        answer_db.insert_one(answer)
        return redirect(url_for('question.detail', question_id=question_id))
    return render_template('question/question_detail.html', question_dict=question_dict, form=form)


@bp.route('/modify/<int:answer_id>', methods=('GET', 'POST'))
@login_required
def modify(answer_id):
    answer_dict = answer_db.find_one({'idx': answer_id})
    if g.user != answer_dict['user_id']:
        flash('수정권한이 없습니다')
        return redirect(url_for('question.detail', question_id=answer_dict['question_id']))
    if request.method == "POST":
        form = AnswerForm()
        if form.validate_on_submit():
            # db 데이터 수정
            fixes = {'content': form.content.data, 'modify_date': datetime.now()}
            print(fixes)
            answer_db.update_one({'idx': answer_id}, {'$set': fixes})
            return redirect(url_for('question.detail', question_id=answer_dict['question_id']))
    else:
        form = AnswerForm()
    return render_template('answer/answer_form.html', form=form, answer_dict=answer_dict)


@bp.route('/delete/<int:answer_id>')
@login_required
def delete(answer_id):
    answer_dict = answer_db.find_one({'idx': answer_id})
    question_id = answer_dict['question_id']
    if g.user != answer_dict['user_id']:
        flash('삭제 권한이 없습니다')
        return redirect(url_for('question.detail', question_id=answer_dict['question_id']))
    answer_db.delete_one({'idx': answer_id})
    return redirect(url_for('question.detail', question_id=answer_dict['question_id']))

