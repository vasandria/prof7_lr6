from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, flash, url_for
from datetime import datetime
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
from werkzeug.utils import redirect

app = Flask(__name__)
app.secret_key = 'some secret salt'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///guestbook.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager(app)


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    psw = db.Column(db.String(500), nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<users {self.id}"


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)

class Profiles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=True)
    old = db.Column(db.Integer)
    city = db.Column(db.String(100))

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return f"<users {self.id}"


@app.route("/")
def index():
    return render_template("index.html", title="Главная")


@app.route("/register", methods = ("POST", "GET"))
def register():
    email = request.form.get('email')
    psw = request.form.get('psw')
    psw2 = request.form.get('psw2')
    if request.method == "POST":
        if not (email or psw or psw2):
            flash('Пожалуйста, заполните все поля')
        elif psw != psw2:
            flash('Пароли не совпадают')
        else:
            try:
                hash_psw = generate_password_hash(request.form['psw'])
                u = Users(email=request.form['email'], psw=hash_psw)
                db.session.add(u)
                db.session.flush()

                p = Profiles(name=request.form['name'], old=request.form['old'],
                             city=request.form['city'], user_id=u.id)
                db.session.add(p)
                db.session.commit()
            except:
                db.session.rollback()
                print("Ошибка добавления в БД")
    return render_template("register.html", title="Регистрация")


@app.route("/login", methods = ("POST", "GET"))
def login():
    email = request.form.get('login')
    psw = request.form.get('psw')

    if email and psw:
        user = Users.query.filter_by(email=email).first()

        if user and check_password_hash(user.psw, psw):
            login_user(user)

            next_page = request.args.get('next')
            redirect(next_page)
        else:
            flash('Неверный логин или пароль')
    return render_template('login.html')


@app.route("/logout", methods = ("POST", "GET"))
@login_required
def logout():
    logout_user()
    return redirect(url_for('/'))


@app.after_request
def redirect_to_signin(response):
    if response.status_code ==401:
        return redirect(url_for('login') + '?next=' + request.url)
    return response


if __name__ == "__main__":
    app.run(debug=True)
