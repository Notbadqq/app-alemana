from werkzeug.security import generate_password_hash, check_password_hash
from flaskweb import db
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy import create_engine, MetaData, Table, select, Column, String, Integer
from sqlalchemy.orm import Query, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

#Startup para la lectura de la base de
engine = create_engine (os.environ["ENGINE"]) #Conexion a la base de datos
connection = engine.connect()
metadata = MetaData()
Base=declarative_base()

#Clase que modela la tabla cas_hiba de la base
class Cas_hiba(Base):
    """"""
    __table__ = Table('cas_hiba', Base.metadata,
                    autoload=True, autoload_with=engine)

#creacion de tabla token si es necesario y agregar elementos a esta
try:
    connection.execute('CREATE TABLE token_table(termino_preferido VARCHAR(300), token tsvector, concept_id_hiba BIGINT)')
except:
    pass
connection.execute('INSERT INTO token_table(termino_preferido, token, concept_id_hiba) SELECT termino_preferido, to_tsvector(termino_preferido) as token, "concept_id_HIBA" FROM cas_hiba ON CONFLICT (termino_preferido) DO NOTHING')

#Clase que modela tabla token_table de la base de datos
class Token_table(Base):
    """"""
    __table__ = Table('token_table', Base.metadata,
                    autoload=True, autoload_with=engine)

#Algo que saque de por ahi... Creo que no esta haciendo nada
def loadSession():
    """"""
    metadata = Base.metadata
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

session = loadSession()