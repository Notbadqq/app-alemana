from flask import Flask, render_template, redirect, request, url_for, jsonify, Response, json
from flaskweb import app
from flaskweb.forms import DescriptionForm
from flaskweb.models import connection, session, Cas_hiba, Token_table

descripciones = [] #Lista que lleva las descripciones agregadas a la cohorte
hiba_ids = [] #Lista de ids en la cohorte

#Funcion que limpia la cohorte creada de todas las descripciones e ids
def elimCohorte():
    global descripciones
    global hiba_ids
    descripciones = []
    hiba_ids = []

#Funcion para buscar a todos los hijos directos de un concepto
#Toma como variable el concepto a buscar
def search_son(concept):
    result = connection.execute('SELECT DISTINCT termino_preferido, "concept_id_HIBA" FROM cas_hiba, hiba_snomed, (SELECT DISTINCT hijo FROM cas_hiba, hiba_snomed, transitiva WHERE termino_preferido=%s AND "concept_id_HIBA"="conceptid_HIBA" AND "conceptidSN"=padre AND es_directo=true) AS tabla_id_h WHERE hijo="conceptidSN" AND "concept_id_HIBA"="conceptid_HIBA" AND tipo_termino=%s', (concept, 'Preferido'))
    rowresult = []
    for row in result:
        for i in row:
            rowresult.append(i)
    rowstp = []
    rowsid = []
    for i in range(1, len(rowresult), 2):
        rowstp.append(rowresult[i-1])
        rowsid.append(rowresult[i])
    return rowstp, rowsid

#Funcion para buscar a todos los padre directos de un concepto
#Toma como variable el concepto a buscar
def search_parents(concept):
    result = connection.execute('SELECT DISTINCT termino_preferido, "concept_id_HIBA" FROM cas_hiba, hiba_snomed, (SELECT DISTINCT padre FROM cas_hiba, hiba_snomed, transitiva WHERE termino_preferido=%s AND "concept_id_HIBA"="conceptid_HIBA" AND "conceptidSN"=hijo AND es_directo=true) AS tabla_id_p WHERE padre="conceptidSN" AND "concept_id_HIBA"="conceptid_HIBA" AND tipo_termino=%s', (concept, 'Preferido'))
    rowresult = []
    for row in result:
        for i in row:
            rowresult.append(i)
    rowstp = []
    rowsid = []
    for i in range(1, len(rowresult), 2):
        rowstp.append(rowresult[i-1])
        rowsid.append(rowresult[i])
    return rowstp, rowsid

#Ruta a la pagina que muestra los resultados de la busqueda de cierto concepto
#recibe mediante la url el concepto a buscar.
@app.route('/search_results/<query>', methods=['GET','POST'])
def search_results(query):
    form=DescriptionForm(list="description-list") 
    if request.method == 'POST' and form.validate_on_submit():
        return redirect(url_for('search_results', query=form.description.data))
    query = query.upper()
    rowsh, rowshid = search_son(query) #Listado de descripciones e ids de los hijos
    rowsp, rowspid = search_parents(query) #Listado de descripciones e ids de los hijos
    query = connection.execute('SELECT DISTINCT termino_preferido, "concept_id_HIBA" FROM cas_hiba WHERE termino_preferido=%s', query)
    #query realizada para buscar tanto el termino preferido como el id del concepto entregado
    rowst=[]
    for row in query:
        for i in row:
            rowst.append(i) 
    #Se retorna el render junto con el concepto deseado(query), los padres(rowsp),
    #los hijo(rowsh) largo del listado de padres(lenp), largo del listado de los hijos(lenh),
    #ids de padres e hijos(rowspid, rowshid) y el formulario de la descripcion (form)
    return render_template('desc_view.html', query=rowst, rowsp=rowsp, rowsh=rowsh, lenp=len(rowsp), lenh=len(rowsh), form=form, lista=descripciones, rowshid=rowshid, rowspid=rowspid)

#Ruta a la pagina de inicio
@app.route("/", methods=['GET', 'POST'])
def index():
    form =DescriptionForm(list="description-list")
    if request.method == 'POST' and form.validate_on_submit():
        return redirect(url_for('search_results', query=form.description.data))
    return render_template("index.html", form=form)

#Ruta a pagina que resuelve el problema del autocompletado del buscador
@app.route("/autocomplete", methods=['GET'])
def autocomplete():
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

#Ruta a pagina que agrega o saca elementos al listado de descripciones e ids
#y devuelve las defscripciones en formato JSON
@app.route("/show_check", methods=['GET'])
def show_lista():
    tipo = request.args.get('tipo', type=str)
    description = request.args.get('description', type=str)
    hiba_id = request.args.get('id')
    try:
        if tipo=='check':
            if description not in descripciones:
                descripciones.append(description)
                hiba_ids.append(hiba_id)
        else:
            descripciones.remove(description)
            hiba_ids.remove(hiba_id)
    except:
        pass
    return Response(json.dumps(descripciones), mimetype='application/json')

#Ruta a pagina que muestra la cohorte que se va a verificar 
@app.route("/aceptar_cohorte", methods=['GET', 'POST'])
def create_cohorte():
    form=DescriptionForm(list="description-list")
    descripciones.sort()
    if request.method == 'POST' and form.validate_on_submit():
        return redirect(url_for('search_results', query=form.description.data))
    return render_template('select_cohorte.html', length=len(descripciones), lista=descripciones, form=form, listaid=hiba_ids)

#Ruta a pagina que aplica la funcion elimCohorte(), para limpiar el listado que se tiene
@app.route("/eliminar", methods=['Get'])
def eliminar():
    action = request.args.get('action', type=str)
    if action == "elim":
        elimCohorte()
    return Response(json.dumps(descripciones), mimetype='application/json')

#Ruta a pagina que agrega toda la descendencia de un concepto a la lista
@app.route("/descendance", methods=['Get'])
def descendance():
    concept = request.args.get('concept', type=str)
    action = request.args.get('action', type=str)
    result = connection.execute('SELECT DISTINCT termino_preferido, "concept_id_HIBA" FROM cas_hiba, hiba_snomed, (SELECT DISTINCT hijo FROM cas_hiba, hiba_snomed, transitiva WHERE termino_preferido=%s AND "concept_id_HIBA"="conceptid_HIBA" AND "conceptidSN"=padre) AS tabla_id_h WHERE hijo="conceptidSN" AND "concept_id_HIBA"="conceptid_HIBA" AND tipo_termino=%s', (concept, 'Preferido'))
    rowresult = []
    for row in result:
        for i in row:
            rowresult.append(i)
    if action == 'check':
        for i in range(1, len(rowresult), 2):
            if rowresult[i-1] not in descripciones:
                descripciones.append(rowresult[i-1])
                hiba_ids.append(rowresult[i])
    elif action == 'uncheck':
        for i in range(1, len(rowresult), 2):
            descripciones.remove(rowresult[i-1])
            hiba_ids.remove(rowresult[i])        
    return Response(json.dumps(descripciones), mimetype='application/json')

#Ruta a pagina que agrega toda la descendencia de un concepto a la lista
@app.route("/allDescendance", methods=['Get'])
def allDescendance():
    concept = request.args.get('concept', type=str)
    query = "(" + concept[:-2] + ")"
    action = request.args.get('action', type=str)
    result = connection.execute('SELECT DISTINCT termino_preferido, "concept_id_HIBA" FROM cas_hiba, hiba_snomed, (SELECT DISTINCT hijo FROM cas_hiba, hiba_snomed, transitiva WHERE termino_preferido IN ' + query + ' AND "concept_id_HIBA"="conceptid_HIBA" AND "conceptidSN"=padre) AS tabla_id_h WHERE hijo="conceptidSN" AND "concept_id_HIBA"="conceptid_HIBA" AND tipo_termino=%s', ('Preferido'))
    rowresult = []
    for row in result:
        for i in row:
            rowresult.append(i)
    if action == 'check':
        for i in range(1, len(rowresult), 2):
            if rowresult[i-1] not in descripciones:
                descripciones.append(rowresult[i-1])
                hiba_ids.append(rowresult[i])
    elif action == 'uncheck':
        for i in range(1, len(rowresult), 2):
            try:
                descripciones.remove(rowresult[i-1])
                hiba_ids.remove(rowresult[i])        
            except: pass
    return Response(json.dumps(descripciones), mimetype='application/json')

#Ruta a la pagina que selecciona todos lo padres o hijos directos
@app.route("/alldirect", methods=['GET'])
def allDirect():
    concept = request.args.get('concept', type=str)
    query = "(" + concept[:-2] + ")"
    action = request.args.get('action', type=str)
    result = connection.execute('SELECT DISTINCT termino_preferido, "concept_id_HIBA" FROM cas_hiba WHERE termino_preferido IN ' + query)
    rowresult = []
    for row in result:
        for i in row:
            rowresult.append(i)
    if action == 'check':
        for i in range(1, len(rowresult), 2):
            if rowresult[i-1] not in descripciones:
                descripciones.append(rowresult[i-1])
                hiba_ids.append(rowresult[i])
    elif action == 'uncheck':
        for i in range(1, len(rowresult), 2):
            try:
                descripciones.remove(rowresult[i-1])
                hiba_ids.remove(rowresult[i])        
            except: pass
    return Response(json.dumps(descripciones), mimetype='application/json')