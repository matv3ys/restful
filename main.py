from flask import Flask, render_template, redirect
from flask import request, make_response, abort, jsonify
import datetime
from data import db_session
from data.users import User
from data.jobs import Jobs
from data.departments import Department
from data.news import News
from data.categories import CategoryJob
# импорт нужных форм
from forms import RegisterForm, LoginForm, NewsForm, JobForm, DepForm

from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import sqlalchemy

# rest-api
import news_api
import jobs_api
import users_api

# users_show
from get_map import get_map
from requests import get

# restful
from flask_restful import reqparse, abort, Api, Resource
import news_resource
import users_resource

# настройки приложения

app = Flask(__name__)
api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)


def main():
    db_session.global_init("db/mars_db.sqlite")
    app.register_blueprint(news_api.blueprint)
    app.register_blueprint(jobs_api.blueprint)
    app.register_blueprint(users_api.blueprint)

    # restful

    # список новостей
    api.add_resource(news_resource.NewsListResource, '/api/v2/news')

    # одна новость
    api.add_resource(news_resource.NewsResource, '/api/v2/news/<int:news_id>')

    # список пользователей
    api.add_resource(users_resource.UsersListResource, '/api/v2/users')

    # один пользователь
    api.add_resource(users_resource.UsersResource, '/api/v2/users/<int:user_id>')

    app.run()


# hometown
@app.route("/users_show/<int:user_id>", methods=['GET'])
def users_show(user_id):
    request = f'http://localhost:5000/api/users/{user_id}'
    user = get(request).json()
    if 'user' in user:
        name = f'{user["user"]["name"]} {user["user"]["surname"]}'
        city = user["user"]["city_from"]
        photo = get_map(city)
    else:
        name = 'Not Found'
        city = 'Nowhere'
        photo = '/static/img/nf.jpg'
    return render_template("users_show.html", name=name, city=city, photo=photo)


# начальная страница (список работ)
@app.route("/")
def index():
    session = db_session.create_session()
    jobs = session.query(Jobs).all()
    return render_template("works_log.html", title="Mars Colonization", jobs=jobs)


# добавление работы
@app.route("/addjob", methods=['GET', 'POST'])
@login_required
def add_job():
    form = JobForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        job = Jobs()
        job.job = form.title.data
        job.team_leader = form.leader_id.data
        job.work_size = form.work_size.data
        job.collaborators = form.collaborators.data
        job.is_finished = form.is_finished.data
        job.creator = current_user.id

        category_id = form.category.data
        category = session.query(CategoryJob).filter(CategoryJob.id == category_id).first()
        job.categories.append(category)
        session.commit()

        try:
            current_user.jobs.append(job)
        except sqlalchemy.orm.exc.DetachedInstanceError:
            pass
        except sqlalchemy.exc.InvalidRequestError:
            pass
        session.merge(current_user)
        session.commit()
        return redirect('/')
    return render_template('add_job.html', title='Adding a job',
                           form=form)


# редактирование работы
@app.route('/addjob/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_job(id):
    form = JobForm()
    if request.method == "GET":
        session = db_session.create_session()
        if current_user.id == 1:
            job = session.query(Jobs).filter(Jobs.id == id).first()
        else:
            job = session.query(Jobs).filter(Jobs.id == id,
                                             Jobs.creator == current_user.id).first()
        if job:
            form.title.data = job.job
            form.leader_id.data = job.team_leader
            form.work_size.data = job.work_size
            form.collaborators.data = job.collaborators
            form.is_finished.data = job.is_finished
            form.category.data = job.categories[0].id
        else:
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        if current_user.id == 1:
            job = session.query(Jobs).filter(Jobs.id == id).first()
        else:
            job = session.query(Jobs).filter(Jobs.id == id,
                                             Jobs.creator == current_user.id).first()
        if job:
            job.job = form.title.data
            job.team_leader = form.leader_id.data
            job.work_size = form.work_size.data
            job.collaborators = form.collaborators.data
            job.is_finished = form.is_finished.data

            category_id = form.category.data
            category = session.query(CategoryJob).filter(CategoryJob.id == category_id).first()
            job.categories[0] = category
            session.commit()

            try:
                current_user.jobs.append(job)
            except sqlalchemy.orm.exc.DetachedInstanceError:
                pass
            except sqlalchemy.exc.InvalidRequestError:
                pass

            session.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('add_job.html', title='Job edit', form=form)


# удаление работы
@app.route('/job_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def job_delete(id):
    session = db_session.create_session()
    if current_user.id == 1:
        job = session.query(Jobs).filter(Jobs.id == id).first()
    else:
        job = session.query(Jobs).filter(Jobs.id == id,
                                         Jobs.creator == current_user.id).first()
    if job:
        session.delete(job)
        session.commit()
    else:
        abort(404)
    return redirect('/')


# блог с новостями
@app.route("/blog")
def blog():
    session = db_session.create_session()
    if current_user.is_authenticated:
        news = session.query(News).filter(
            (News.user == current_user) | (News.is_private != True))
    else:
        news = session.query(News).filter(News.is_private != True)
    return render_template("blog.html", title="Blog", news=news)


# добавление новостей
@app.route('/news', methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        current_user.news.append(news)
        session.merge(current_user)
        session.commit()
        return redirect('/blog')
    return render_template('add_news.html', title='News add',
                           form=form)


# редактирование новостей
@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        session = db_session.create_session()
        news = session.query(News).filter(News.id == id,
                                          News.user == current_user).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        news = session.query(News).filter(News.id == id,
                                          News.user == current_user).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            session.commit()
            return redirect('/blog')
        else:
            abort(404)
    return render_template('add_news.html', title='News edit', form=form)


# удаление новостей
@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    session = db_session.create_session()
    news = session.query(News).filter(News.id == id,
                                      News.user == current_user).first()
    if news:
        session.delete(news)
        session.commit()
    else:
        abort(404)
    return redirect('/blog')


# список департаментов
@app.route("/departments")
def departments():
    session = db_session.create_session()
    deps = session.query(Department).all()
    return render_template("departments.html", title="List of Departments", deps=deps)


# добавление департамента
@app.route('/add_dep', methods=['GET', 'POST'])
@login_required
def add_dep():
    form = DepForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        dep = Department()
        dep.title = form.title.data
        dep.chief = form.chief_id.data
        dep.members = form.members.data
        dep.email = form.email.data
        dep.creator = current_user.id
        chief = session.query(User).filter(User.id == form.chief_id.data).first()
        chief.deps.append(dep)
        session.merge(current_user)
        session.commit()
        return redirect('/departments')
    return render_template('add_dep.html', title='Add a Department',
                           form=form)


# редактирование департамента
@app.route('/add_dep/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_dep(id):
    form = DepForm()
    if request.method == "GET":
        session = db_session.create_session()
        if current_user.id == 1:
            dep = session.query(Department).filter(Department.id == id).first()
        else:
            dep = session.query(Department).filter(Department.id == id,
                                                   Department.creator == current_user.id).first()
        if dep:
            form.title.data = dep.title
            form.chief_id.data = dep.chief
            form.members.data = dep.members
            form.email.data = dep.email
        else:
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        if current_user.id == 1:
            dep = session.query(Department).filter(Department.id == id).first()
        else:
            dep = session.query(Department).filter(Department.id == id,
                                                   Department.creator == current_user.id).first()
        if dep:
            dep.title = form.title.data
            dep.chief = form.chief_id.data
            dep.members = form.members.data
            dep.email = form.email.data
            session.commit()
            return redirect('/departments')
        else:
            abort(404)
    return render_template('add_dep.html', title='Department edit', form=form)


# удаление департамента
@app.route('/dep_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def dep_delete(id):
    session = db_session.create_session()
    if current_user.id == 1:
        dep = session.query(Department).filter(Department.id == id).first()
    else:
        dep = session.query(Department).filter(Department.id == id,
                                               Department.creator == current_user.id).first()
    if dep:
        session.delete(dep)
        session.commit()
    else:
        abort(404)
    return redirect('/departments')


# вход на сайт
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Sign in', form=form)


# выход пользователя
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


# загрузка текущего пользователя
@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


# регистрация пользователя
@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            surname=form.surname.data,
            name=form.name.data,
            age=form.age.data,
            position=form.position.data,
            speciality=form.speciality.data,
            address=form.address.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/login')
    return render_template('register.html', title='Sign up', form=form)


if __name__ == '__main__':
    main()
