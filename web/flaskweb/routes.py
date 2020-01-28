from flask import Flask, render_template, redirect, request, url_for, jsonify, Response, json
from flaskweb import app
from flaskweb.forms import PostForm, SignupForm, LoginForm, DescriptionForm
from flaskweb.models import connection, session, Cas_hiba, Token_table

lista=[]

def elimCohorte():
    global lista
    lista = []

def search_son(concept):
    result = connection.execute('SELECT DISTINCT termino_preferido FROM cas_hiba, hiba_snomed, (SELECT DISTINCT hijo FROM cas_hiba, hiba_snomed, transitiva WHERE termino_preferido=%s AND "concept_id_HIBA"="conceptid_HIBA" AND "conceptidSN"=padre AND es_directo=true) AS tabla_id_h WHERE hijo="conceptidSN" AND "concept_id_HIBA"="conceptid_HIBA" AND tipo_termino=%s', (concept, 'Preferido'))
    rows = []
    for row in result:
        for i in row:
            rows.append(i)
    return rows

def search_parents(concept):
    result = connection.execute('SELECT DISTINCT termino_preferido FROM cas_hiba, hiba_snomed, (SELECT DISTINCT padre FROM cas_hiba, hiba_snomed, transitiva WHERE termino_preferido=%s AND "concept_id_HIBA"="conceptid_HIBA" AND "conceptidSN"=hijo AND es_directo=true) AS tabla_id_p WHERE padre="conceptidSN" AND "concept_id_HIBA"="conceptid_HIBA" AND tipo_termino=%s', (concept, 'Preferido'))
    rows = []
    for row in result:
        for i in row:
            rows.append(i)
    return rows

def get_descriptions():
    result = connection.execute('SELECT DISTINCT termino_preferido FROM cas_hiba WHERE tipo_termino=%s', "Preferido")
    rows = []
    for row in result:
        for i in row:
            rows.append(i)
    return rows

desc = get_descriptions()
def theForm():
    form = DescriptionForm(list="description-list")
    return form

@app.route('/search_results/<query>', methods=['GET','POST'])
def search_results(query):
    form=theForm()
    if request.method == 'POST' and form.validate_on_submit():
        return redirect(url_for('search_results', query=form.description.data))
    query = query.upper()
    rowsh = search_son(query)
    rowsp = search_parents(query)
    query = connection.execute('SELECT DISTINCT termino_preferido, "concept_id_HIBA" FROM cas_hiba WHERE termino_preferido=%s', query)
    rowst=[]
    for row in query:
        for i in row:
            rowst.append(i) 
    return render_template('desc_view.html', query=rowst, rowsp=rowsp, rowsh=rowsh, lenp=len(rowsp), lenh=len(rowsh), form=form, lista=lista)

@app.route('/search', methods=['GET', 'POST'])
def search():
    form=theForm()
    if request.method == 'POST' and form.validate_on_submit():
        return redirect(url_for('search_results', query=form.description.data))
    return render_template('search.html', form=form)

@app.route("/", methods=['GET', 'POST'])
def index():
    form =theForm()
    if request.method == 'POST' and form.validate_on_submit():
        return redirect(url_for('search_results', query=form.description.data))
    return render_template("index.html", form=form)

@app.route("/test", methods=['GET'])
def test():
    consulta = request.args.get('consulta', default="", type=str)
    if consulta=="" or len(consulta)<3:
        return ""
    filtro = ["EL", "LA", "LOS", "LAS", "EN", "SOBRE", "UN", "UNA", "UNOS", "UNAS", "HASTA", "ANTE", "BAJO", "DE", "DESDE", "CON", "CONTRA", "A"]
    consulta = consulta.split()
    arreglo = ""
    for pal in consulta:
        if pal in filtro:
            pass
        elif pal not in arreglo:
            if arreglo == "":
                arreglo = pal + ":*"
            else:
                arreglo += " & " + pal + ":*"
    result = connection.execute('SELECT termino_preferido FROM token_table WHERE token @@ to_tsquery(%s) LIMIT 10', arreglo)
    obj_result=[]
    for row in result:
        obj_result.append(str(row[0]))
    return Response(json.dumps(obj_result), mimetype='application/json')

@app.route("/show_check", methods=['GET'])
def show_lista():
    tipo=request.args.get('tipo', type=str)
    description=request.args.get('description', type=str)
    try:
        if tipo=='check':
            if description not in lista:
                lista.append(description)
        else:
            lista.remove(description)
    except:
        pass
    return Response(json.dumps(lista), mimetype='application/json')

@app.route("/aceptar_cohorte", methods=['GET', 'POST'])
def create_cohorte():
    form=theForm()
    lista.sort()
    if request.method == 'POST' and form.validate_on_submit():
        return redirect(url_for('search_results', query=form.description.data))
    return render_template('select_cohorte.html', lista=lista, form=form)

@app.route("/elim_rest", methods=['Get'])
def elim_rest():
    action = request.args.get('action', type=str)
    if action == "elim":
        elimCohorte()
    return Response(json.dumps(lista), mimetype='application/json')

@app.route("/get_idcode", methods=['GET'])
def get_idcode():
    desc = request.args.get('descrip', type=str)
    result = connection.execute('SELECT DISTINCT "concept_id_HIBA" FROM cas_hiba WHERE termino_preferido=%s', desc)
    rows = []
    for row in result:
        for i in row:
            rows.append(i)
    return Response(json.dumps(rows), mimetype='application/json')