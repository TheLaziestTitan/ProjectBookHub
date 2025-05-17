import os

from flask import Flask, render_template, redirect, url_for, flash, jsonify, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_restful import Api, Resource, reqparse
from flask_wtf.csrf import CSRFProtect
from werkzeug.utils import secure_filename

from forms import RegisterForm, LoginForm, BookForm
from models import db, User, Book

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookhub.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'

db.init_app(app)

csrf = CSRFProtect(app)
csrf.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class BooksAPI(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('genre', type=str)
        parser.add_argument('rating', type=float)
        args = parser.parse_args()

        query = Book.query
        if args['genre']:
            query = query.filter(Book.genre == args['genre'])
        if args['rating']:
            query = query.filter(Book.rating >= args['rating'])

        books = query.all()
        return jsonify({
            'books': [book.to_dict() for book in books],
            'total': len(books)
        })


api.add_resource(BooksAPI, '/api/books')


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'covers'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'books'), exist_ok=True)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Пользователь с таким email уже существует')
            return redirect(url_for('register'))

        new_user = User(username=form.username.data, email=form.email.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Регистрация успешна! Теперь вы можете войти.')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('home'))
        flash('Неверный email или пароль')
    return render_template('login.html', form=form)


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
    form = BookForm()
    if form.validate_on_submit():
        cover_file = form.cover.data
        cover_filename = None
        if cover_file and cover_file.filename != '':
            cover_ext = os.path.splitext(cover_file.filename)[1].lower()
            if cover_ext not in ['.jpg', '.jpeg', '.png']:
                flash('Недопустимый формат обложки. Используйте JPG, JPEG или PNG.')
                return redirect(url_for('add_book'))
            cover_filename = secure_filename(cover_file.filename)
            cover_path = os.path.join(app.config['UPLOAD_FOLDER'], 'covers', cover_filename)
            cover_file.save(cover_path)

        book_file = form.file.data
        if book_file and book_file.filename != '':
            book_ext = os.path.splitext(book_file.filename)[1].lower()
            if book_ext not in ['.pdf', '.docx', '.epub']:
                flash('Недопустимый формат файла книги. Используйте PDF, DOCX или EPUB.')
                return redirect(url_for('add_book'))
            book_filename = secure_filename(book_file.filename)
            book_path = os.path.join(app.config['UPLOAD_FOLDER'], 'books', book_filename)
            book_file.save(book_path)

        new_book = Book(
            title=form.title.data,
            author=form.author.data,
            description=form.description.data,
            genre=form.genre.data,
            cover=cover_filename,
            file_path=book_filename,
            rating=form.rating.data,
            added_by=current_user.id,
            is_public=form.is_public.data
        )
        db.session.add(new_book)
        db.session.commit()
        flash('Книга успешно добавлена!')
        return redirect(url_for('recommendations'))
    return render_template('add_book.html', form=form)


@app.route('/book/<int:book_id>')
def view_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        flash('Книга не найдена')
        return redirect(url_for('recommendations'))

    users = {user.id: user for user in User.query.all()}

    return render_template('view_book.html', book=book, recommendations=recommendations, users=users)


@app.route('/')
def home():
    public_books = Book.query.filter_by(is_public=True).all()
    my_books = []

    if current_user.is_authenticated:
        my_books = Book.query.filter(Book.is_public == False, Book.added_by == current_user.id).all()

    return render_template('index.html', public_books=public_books, my_books=my_books)


@app.route('/download/<path:filename>')
def download_file(filename):
    return send_from_directory(
        directory=os.path.join(app.config['UPLOAD_FOLDER'], 'books'),
        path=filename,
        as_attachment=True
    )


@app.route('/recommendations')
def recommendations():
    books = Book.query.filter_by(is_public=True).all()
    books_with_author = []
    for book in books:
        user = db.session.get(User, book.added_by)
        books_with_author.append({
            'book': book,
            'author': user.username if user else 'Неизвестный автор'
        })
    return render_template('recommendations.html', books=books)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
