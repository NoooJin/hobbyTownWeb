from flask import Blueprint, redirect, render_template, request, url_for, session, g, flash
from pymongo import MongoClient
from bson.objectid import ObjectId

from datetime import datetime
import math
from hobbytown.forms import QuestionForm, AnswerForm
from hobbytown.views.auth_views import login_required


bp = Blueprint('question', __name__, url_prefix='/question')

client = MongoClient("localhost", 27017)
db = client.base
question_db = db.question
user_db = db.user
answer_db = db.answer


# 현재 인덱스 번호 + 1 함수
def get_next_index(column_name):
    try:
        last_field = column_name.find().sort('idx', -1).limit(1)
        last_field = list(last_field)[0]['idx'] + 1
    except:
        last_field = 1
    return last_field


@bp.route('/form', methods=('POST', 'GET'))
@login_required
def create_question():
    form = QuestionForm()
    # index 번호 넣어야 함
    if request.method == 'POST' and form.validate_on_submit():
        question_dict = {
                         'idx': get_next_index(question_db),
                         'user_name': g.user,
                         'subject': form.subject.data,
                         'content': form.content.data,
                         'create_date': datetime.now(),
                         }
        question_db.insert_one(question_dict)
        return redirect(url_for('question.question_list'))
    return render_template('question/question_form.html', form=form)


@bp.route('/list')
def question_list():
    # 현재 페이지 번호
    page = request.args.get('page', type=int, default=1)
    # 한 페이지에 보여줄 개수
    limit = 10
    # 페이지에서 보여줄 데이터 리스트
    board_list = question_db.find({}).skip((page - 1) * limit).limit(limit).sort("create_date", -1)
    # DB에 저장된 총 게시물의 개수
    tot_count = question_db.count_documents({})
    # 전체 페이지 수, 마지막 페이지
    last_page_num = math.ceil(tot_count / limit)
    # 페이지 블록 크기
    block_size = 10
    # 현재 블럭의 위치
    block_num = int((page-1) / block_size)
    # 현재 블럭의 맨 처음 페이지 넘버
    block_start = (block_size * block_num) + 1
    # 현재 블럭의 맨 끝 페이지 넘버
    block_end = block_start + (block_size -1)
    question_pagination = {
        'board_list': board_list,
        'limit': limit,
        'tot_count': tot_count,
        'page': page,
        'block_size': block_size,
        'block_start': block_start,
        'block_end': block_end,
        'last_page_num': last_page_num
    }
    kw = request.args.get('kw', type=str, default='')
    question_list = []
    if kw:
        question_list = list(question_db.find( {'$or': [{'subject': {'$regex': kw}}, {'content': {'$regex': kw}}]}))
        question_pagination['board_list'] = question_db.find({'$or': [{'subject': {'$regex': kw}}, {'content': {'$regex': kw}}]}).skip((page - 1) * limit).limit(limit).sort("create_date", -1)
        question_pagination['tot_count'] = question_db.count_documents({'$or': [{'subject': {'$regex': kw}}, {'content': {'$regex': kw}}]})
        question_pagination['last_page_num'] = math.ceil(question_pagination['tot_count'] / limit)

    question_dict = list(question_db.find().sort("create_date", -1))
    return render_template('question/question_list.html', question_dict=question_dict, question_pagination=question_pagination,
                           question_list=question_list, kw=kw)


@bp.route('/detail/<int:question_id>')
def detail(question_id):
    # ObjectID로 검색해야 id 검색 가능
    question_dict = question_db.find_one({'idx': question_id})
    answer_dict = list(answer_db.find({'question_id': question_id}))
    form = AnswerForm()
    return render_template('question/question_detail.html', question_dict=question_dict, answer_dict=answer_dict, form=form, len=len)


@bp.route('/modify/<int:question_id>', methods=('GET', 'POST'))
@login_required
def modify(question_id):
    question_dict = question_db
    if g.user != question_db.find_one({'idx': question_id})['user_name']:
        flash('수정권한이 없습니다')
        return redirect(url_for('question.detail', question_id=question_id))
    if request.method == 'POST':  # POST 요청
        form = QuestionForm()
        if form.validate_on_submit():
            # 수정한 데이터 업그레이드, 수정 시간 추가
            fixes = {'subject': form.subject.data, 'content': form.content.data, 'modify_date': datetime.now()}
            question_db.update_one({'idx': question_id}, {'$set': fixes})
            return redirect(url_for('question.detail', question_id=question_id))
    else:  # GET 요청
        form = QuestionForm()
        question_dict = question_db.find_one({'idx': question_id})
    return render_template('question/question_modify.html', form=form, question_dict=question_dict)


@bp.route('/delete/<int:question_id>')
@login_required
def delete(question_id):
    question_dict = question_db
    # question = Question.query.get_or_404(question_id)
    try:
        if g.user != question_db.find_one({'idx': question_id})['user_name']:
            flash('삭제권한이 없습니다')
            return redirect(url_for('question.detail', question_id=question_id))
    except:
        return redirect(url_for('question.detail', question_id=question_id))
    question_dict.delete_one({'idx': question_id})
    return redirect(url_for('question.question_list'))
