# flask_web/app.py

from flask import Flask, render_template, redirect, request, url_for
from forms import PostForm, SignupForm, LoginForm, DescriptionForm
from werkzeug.urls import url_parse
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, MetaData, Table, select
from flask_bootstrap import Bootstrap
import os

app = Flask(__name__)
app.config['SECRET_KEY']=os.environ["SECRET_KEY"] #Clave para ingresar al servidor
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Bootstrap(app)

engine = create_engine (os.environ["ENGINE"]) #Conexion a la base de datos
connection = engine.connect()
metadata = MetaData()

def search_son(concept):
    result = connection.execute('SELECT DISTINCT description_nombre FROM cas_hiba, hiba_snomed, (SELECT hijo FROM cas_hiba, hiba_snomed, transitiva WHERE description_nombre=%s AND "concept_id_HIBA"="conceptid_HIBA" AND "conceptidSN"=padre AND es_directo=true) AS tabla_id_h WHERE hijo="conceptidSN" AND "concept_id_HIBA"="conceptid_HIBA" AND tipo_termino=%s', (concept, 'Preferido'))
    rows = []
    for row in result:
        rowstr = str(row)
        rows.append(rowstr[3:-3])
    return rows

def search_parents(concept):
    result = connection.execute('SELECT DISTINCT description_nombre FROM cas_hiba, hiba_snomed, (SELECT padre FROM cas_hiba, hiba_snomed, transitiva WHERE description_nombre=%s AND "concept_id_HIBA"="conceptid_HIBA" AND "conceptidSN"=hijo AND es_directo=true) AS tabla_id_p WHERE padre="conceptidSN" AND "concept_id_HIBA"="conceptid_HIBA" AND tipo_termino=%s', (concept, 'Preferido'))
    rows = []
    for row in result:
        rowstr = str(row)
        rows.append(rowstr[3:-3])
    return rows

def get_descriptions(inpt, lst):
    sql = 'SELECT DISTINCT description_nombre FROM cas_hiba WHERE description_nombre LIKE %' + inpt + '% LIMIT 10'
    result = connection.execute(sql)
    for row in result:
        rowstr = str(row)
        lst.append(rowstr[3:-3])
    return lst

@app.route('/search_results/<query>')
def search_results(query):
    query = query.upper()
    results_t = connection.execute('SELECT DISTINCT description_h FROM (SELECT DISTINCT description_nombre AS description_p FROM cas_hiba, hiba_snomed, (SELECT padre FROM cas_hiba, hiba_snomed, transitiva WHERE description_nombre=%s AND "concept_id_HIBA"="conceptid_HIBA" AND "conceptidSN"=hijo) AS tabla_id_p WHERE padre="conceptidSN" AND "concept_id_HIBA"="conceptid_HIBA" AND tipo_termino=%s) AS p, (SELECT DISTINCT description_nombre AS description_h FROM cas_hiba, hiba_snomed, (SELECT hijo FROM cas_hiba, hiba_snomed, transitiva WHERE description_nombre=%s AND "concept_id_HIBA"="conceptid_HIBA" AND "conceptidSN"=padre) AS tabla_id_h WHERE hijo="conceptidSN" AND "concept_id_HIBA"="conceptid_HIBA" AND tipo_termino=%s) AS h WHERE description_h!=description_p', (query, 'Preferido', query, 'Preferido'))
    rowsh = search_son(query)
    rowsp = search_parents(query)
    rowst=[]
    for row in results_t:
        rowst.append(row)
    return render_template('desc_view.html', query=query, rowsp=rowsp, rowsh=rowsh, lenp=len(rowsp), lenh=len(rowsh), rowst=rowst, lent=len(rowst))

@app.route('/search', methods=['GET', 'POST'])
def search():
    form = DescriptionForm(list="description-list")
    desc = []
    if request.method == 'POST' and form.validate_on_submit():
        return redirect(url_for('search_results', query=form.description.data))
    return render_template('search.html', form=form, desc = desc)

@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')