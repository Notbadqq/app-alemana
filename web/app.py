# flask_web/app.py

from flask import Flask, render_template, redirect, request, url_for
from forms import PostForm, SignupForm, LoginForm, DescriptionForm
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from models import User, users, get_user
from werkzeug.urls import url_parse
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, MetaData, Table, select

app = Flask(__name__)
app.config['SECRET_KEY'] = '7110c8ae51a4b5af97be6534caef90e4bb9bdcb3380af008f90b23a5d1616bf319bc298105da20fe'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

login_manager = LoginManager(app)
login_manager.login_view = "login"
engine = create_engine ('postgres://postgres:postgres@mydb:5432/data')
connection = engine.connect()
metadata = MetaData()
cas_hiba = Table('cas_hiba', metadata, autoload=True, autoload_with=engine)
someting = select([cas_hiba]).where(cas_hiba.c.concepto_id == 3207566)
data = connection.execute(someting)
posts = []
for row in data:
    posts.append(row)

def search_son(concept):
    result = connection.execute('SELECT DISTINCT description_nombre FROM cas_hiba, hiba_snomed, (SELECT hijo FROM cas_hiba, hiba_snomed, transitiva WHERE description_nombre=%s AND "concept_id_HIBA"="conceptid_HIBA" AND "conceptidSN"=padre AND es_directo=true) AS tabla_id_h WHERE hijo="conceptidSN" AND "concept_id_HIBA"="conceptid_HIBA" AND tipo_termino=%s', (concept, 'Preferido'))
    rows=[]
    for row in result:
        rowstr=str(row)
        rows.append(rowstr[3:-3])
    return rows

def search_parents(concept):
    result = connection.execute('SELECT DISTINCT description_nombre FROM cas_hiba, hiba_snomed, (SELECT padre FROM cas_hiba, hiba_snomed, transitiva WHERE description_nombre=%s AND "concept_id_HIBA"="conceptid_HIBA" AND "conceptidSN"=hijo AND es_directo=true) AS tabla_id_p WHERE padre="conceptidSN" AND "concept_id_HIBA"="conceptid_HIBA" AND tipo_termino=%s', (concept, 'Preferido'))
    rows=[]
    for row in result:
        rowstr=str(row)
        rows.append(rowstr[3:-3])
    return rows

@login_manager.user_loader
def load_user(user_id):
    for user in users:
        if user.id == int(user_id):
            return user
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = get_user(form.email.data)
        if user is not None and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')
            return redirect(next_page)
    return render_template('login_form.html', form=form)

@app.route('/search_results/<query>')
def search_results(query):
    results_t = connection.execute('SELECT DISTINCT description_h FROM (SELECT DISTINCT description_nombre AS description_p FROM cas_hiba, hiba_snomed, (SELECT padre FROM cas_hiba, hiba_snomed, transitiva WHERE description_nombre=%s AND "concept_id_HIBA"="conceptid_HIBA" AND "conceptidSN"=hijo) AS tabla_id_p WHERE padre="conceptidSN" AND "concept_id_HIBA"="conceptid_HIBA" AND tipo_termino=%s) AS p, (SELECT DISTINCT description_nombre AS description_h FROM cas_hiba, hiba_snomed, (SELECT hijo FROM cas_hiba, hiba_snomed, transitiva WHERE description_nombre=%s AND "concept_id_HIBA"="conceptid_HIBA" AND "conceptidSN"=padre) AS tabla_id_h WHERE hijo="conceptidSN" AND "concept_id_HIBA"="conceptid_HIBA" AND tipo_termino=%s) AS h WHERE description_h!=description_p', (query, 'Preferido', query, 'Preferido'))
    rowsh = search_son(query)
    rowsp = search_parents(query)
    rowst=[]
    for row in results_t:
        rowst.append(row)
    return render_template('desc_view.html', query=query, rowsp=rowsp, rowsh=rowsh, lenp=len(rowsp), lenh=len(rowsh), rowst=rowst, lent=len(rowst))

@app.route('/search', methods=['GET', 'POST'])
def search():
    form = DescriptionForm()
    if request.method == 'POST' and form.validate_on_submit():
        return redirect(url_for('search_results', query=form.description.data))
    return render_template('search.html', form=form)

@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template("index.html", posts=posts, data=data, cas_hiba=cas_hiba)

@app.route("/p/<string:query>/")
def show_post(slug):
    return render_template("post_view.html", slug_title=slug, posts=posts)

@app.route("/admin/post/", methods=['GET', 'POST'], defaults={'post_id': None})
@app.route("/admin/post/<int:post_id>/", methods=['GET', 'POST'])
@login_required
def post_form(post_id):
    form = PostForm()
    if form.validate_on_submit():
        title = form.title.data
        title_slug = form.title_slug.data
        content = form.content.data
        post = {'title': title, 'title_slug': title_slug, 'content': content}
        posts.append(post)
        return redirect(url_for('index'))
    return render_template("admin/post_form.html", form=form)

@app.route("/signup/", methods=["GET", "POST"])
def show_signup_form():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = SignupForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        # Creamos el usuario y lo guardamos
        user = User(len(users) + 1, name, email, password)
        users.append(user)
        # Dejamos al usuario logueado
        login_user(user, remember=True)
        next_page = request.args.get('next', None)
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template("signup_form.html", form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')