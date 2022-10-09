from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, EmailField
from wtforms.validators import DataRequired, Length, EqualTo, Email


class UserLoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(), Length(min=3, max=25)])
    secret = PasswordField('secret', validators=[DataRequired()])


class UserCreateForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(), Length(min=3, max=25)])
    secret1 = PasswordField('secret', validators=[DataRequired(), EqualTo('secret2', '비밀번호가 일치하지 않습니다')])
    secret2 = PasswordField('checksecret', validators=[DataRequired()])
    email = EmailField('email', validators=[DataRequired(), Email()])


class QuestionForm(FlaskForm):
    subject = StringField('제목', validators=[DataRequired('제목은 필수 입력 항목입니다')])
    content = TextAreaField('내용', validators=[DataRequired('내용은 필수 입력 항목입니다')])


class AnswerForm(FlaskForm):
    content = TextAreaField('내용', validators=[DataRequired('내용은 필수 입력 항목입니다')])