# Procedimiento
Para lograr correr la aplicación es necesario que se ejecute desde el docker-compose.
De no ser asi, se requiere de ciertos cambios en el codigo. 
Tanto en la configuracion de contrasenna, como en el engine se debe ingresar manualmente sus valores.
En el primer caso es una clave segura para el servidor. Y en el segundo se requiere la conexion a la base de datos,
de la forma '<Dialecto>://<Usuario>:<Clave>@<Host>:<Puerto>/<Base>'

Una vez se tenga esto se puede ejecutar el servidor con ```python app.py```