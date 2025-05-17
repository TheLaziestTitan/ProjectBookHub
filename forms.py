from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField, TextAreaField, FloatField, FileField, \
    BooleanField
from wtforms.validators import DataRequired, EqualTo
from flask_wtf.file import FileAllowed


class RegisterForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField('Повторите пароль',
                              validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class BookForm(FlaskForm):
    title = StringField('Название книги', validators=[DataRequired()])
    author = StringField('Автор', validators=[DataRequired()])
    description = TextAreaField('Описание')
    genre = StringField('Жанр')
    cover = FileField('Обложка книги', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    file = FileField('Файл книги (PDF/DOCX/EPUB)', validators=[FileAllowed(['pdf', 'docx', 'epub'])])
    is_public = BooleanField('Общий доступ')
    rating = FloatField('Рейтинг (от 1 до 5)', validators=[DataRequired()])
    submit = SubmitField('Добавить книгу')

