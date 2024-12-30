# Instalación del proyecto:
1. clonar
2. verificar las dependencias y funciones
3. crear un ambiente de Python para trabajar en el
4. instalar dependencias
5. Ejecutar Seed

### Verificar Dependencias
Para la verificación vamos a usar algunos comandos, primero debemos tener Python instalado y configurado en las "Variables de Entorno" para Windows, en el CMD ejecutamos:
- "python --version"
- "pip --version"

>Si alguna de estas no sale, habrá que configurar lo anterior dicho.
>
>PIP es una herramienta con la que instalación lo que necesitamos de Python, es como el NPM que se usa en Angular.

### Ambiente Python
Para crear el ambiente de Python, nos vamos a la raíz del proyecto "proyecto-django" en la consola de VS Code y colocamos “python -m venv venv”

Luego para usar este ambiente en VS Code damos tecla F1 y escribimos "python interpreter", seleccionamos la opción que se parezca y luego saldrán un entorno de Python base y el que nosotros creamos con el nombre "(venv) VersionActualPython".

Si teníamos la consola abierta, cerramos y volvemos a abrirla, si en la ruta no sale "(venv) RutaProyecto", pero se ve una alerta que dice que el entorno esta activado, pero no es visible, ya estará funcionando.

También nos podemos fijar en la barra inferior, esta debe tener un texto como "{} Python VersionPython ('env')", esto indicara que estamos usando el entorno correctamente.

### Instalar Dependencias
Con el ambiente configurado y seleccionado instalaremos las dependencias y librerías del proyecto con el comando "pip install -r requirements.txt" (debemos estar en la raíz para ejecutar ese comando), esto instalara Django, Rest_framework y demás dependencias o librerías que necesitemos.

Podemos ejecutar el comando "python manage.py runserver" para verificar que está funcionando correctamente.

### Ejecutar Seed
Para ejecutar las Seed usamos "python manage.py seed_all", esto ejecutara las semillas definidas y mostrata un 3 mensajes en consola (1 por cada seed, incluyendo a la que ejeucta a las demas).

Se crearan 3 usuarios, un superadmin, un admin y un usuario normal.

Para acceder con estos al sistema, podemos usar <ins>super</ins>, <ins>admin</ins> o <ins>user</ins> acompañado de '<ins>@gmail.com</ins>'; la contraseña de estos 3 usuarios es 1234.




