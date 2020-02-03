La aplicación utiliza una base de datos con tres tablas en ella cas_hiba, hiba_snomed y transitiva.
Flask al iniciarse crea una cuarta tabla token_table la cual ayuda al autocomplete.

La aplicación hace llamadas a las tablas para obtener la información de los familiares directos
los distintos terminos mediante queries. Estas son entregadas a las páginas html gracias al 
render de flask.

En base_template.html se encuentra el nav-bar utilizado en las distintas páginas, además de la
función de autocompletado para este. Como también funciones utilizadas tanto en desc_view.html
como en select_cohorte.html.

En desc_view.html tenemos la vista para los conceptos y el listado de sus hijos. A estas se
llega ingresando una descripción válida en el buscador y apretando enter. Cada uno de los 
conceptos familia es un hipervículo a la página de dicho concepto.
Marcando uno de los checkbox se realiza la función checkChenge(), la cual toma el checkbox
el concepto y su id, para mandarlos a la ruta show_lista(). Esta añade o quita a la lista 
descripciones e hiba_id, el concepto y su id para luego mandarlo en formato JSON de vuelta 
para la lectura de los conceptos agregados hasta ahora.

Una vez seleccionados los conceptos se puede generar esta agrupación apretando el botón 
verificar cohorte, el cual lleva al link de la página que se renderiza a partir de
select_cohorte.html en esta se cargan los conceptos e ids agregados, y se puede eliminar 
algunos de los conceptos agregados a la lista.