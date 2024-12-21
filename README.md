# Instalació n del proyecto:
1. clonar
2. verificar las dependencias y funciones
3. crear un ambiente de Python para trabajar en el
4. instalar dependencias y demás

### Verificar Dependencias
Para la verificación vamos a usar algunos comandos, primero debemos tener Python instalado y configurado en las "Variables de Entorno" para Windows, en el CMD ejecutamos:
- "python --version"
- "pip --version"

>Si alguna de estas no sale, habrá que configurar lo anterior dicho.
>
>PIP es una herramienta con la que instalación lo que necesitamos de Python, es como el NPM que se usa en Angular.

### Ambiente Python
Para crear el ambiente de Python, nos vamos a la raíz del proyecto "proyecto-django", colocamos “python -m venv venv”.

Luego para usar este ambiente en VS Code damos tecla F1 y escribirmos "python interpreter", seleccionamos la opción que se parezca y luego saldran un entorno de Python base y el que nosotros creamos con el nombre "(venv) VersionActualPython", si teniamos al consola abierta, cerramos y volvemos a abrirla, si en la ruta no sale "(venv) RutaProyecto", pero se ve una alerta que dice que el entorno esta activado, pero no es visible, ya estara funcionando.
Tambien nos podemos fijar en la barra inferior, esta debe tener un texto como "{} Python VersionPython ('env')", esto indicara que estamos usando el entorno correctamente.

### Instalar Dependencias
Con el ambiente configurado y seleccionado instalaremos las dependecias y librerias del proyecto con el comando "pip install -r requirements.txt" (debemos estar en la raíz para ejecutar ese comando), esto instalara Django, Rest_framework y demas depdencias o librerias que necesitemos.
Podemos ejecutar el comando "python manage.py runserver" para verificar que esta funcionando correctamente.


