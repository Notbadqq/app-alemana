# **¿Cómo utilizar esta aplicación?**
## **Pasos a seguir:**

  Prerequisitos, tener docker y docker-compose descargados.
  
  1. Clone o descargue la aplicación en la carpeta deseada, ya sea con git clone o descargando el zip del repositorio.
  
  2. Desde la terminal ingrese al archivo descargado, e ingrese los comandos:
  
  ``` docker-compose build```
  
  Este se encargará de crear las imágenes que se utilizarán en esta aplicación.
  
  ``` docker-compose up -d ```
  
  Esto se encargará de iniciar los contenedores con las imágenes creadas anteriormente.
  
  ## **Resultado esperado**
  
  Ahora se debería poder acceder a la aplicación desde la url localhost:5000
  
  En esta se verá una barra buscadora y dos botones, ingrese la descripcion que se quiera buscar y presione enter
  
  Esto lo llevará a una página que muestra los padres e hijos del concepto seleccionado.
  
  Utilice los checkboxes para generar una agrupación de conceptos, luego verifiquela apretando el botón verificar cohorte.
