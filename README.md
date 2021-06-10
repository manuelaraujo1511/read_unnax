# Read unnax site web 

# Lenguajes
- Python 3.7.2

# Bases de Datos
- Mongo DB 4.4.6
- Sqlite3
# Servicio de Colas
- Rabbit MQ 3.8.17

# Framwork:
- DjangoREST Framework
# Descripcion
### API REST y codigo en python para realizar scraping al sitio web destinado a pruebas de unnax

# Ejecucion en terminal
### Dentro de la carpeta script esta el codigo ( **read.py** ) junto con los paquetes que deben ser instalados para porderlo ejecutar ( **requirements.txt** )
`python read.py --username <username> --password <password>`

# Ejecucion del API REST
### Para la ejecuion del api se encuentra un archivo **.yml** que contiene la configuracion de docker-compose mediante el cual se levantaran los diferentes servicios