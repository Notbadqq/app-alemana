from werkzeug.security import generate_password_hash, check_password_hash
from flaskweb import db
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy import create_engine, MetaData, Table, select, Column, String, Integer
from sqlalchemy.orm import Query, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

engine = create_engine (os.environ["ENGINE"]) #Conexion a la base de datos
connection = engine.connect()
metadata = MetaData()
Base=declarative_base()
class Cas_hiba(Base):
    """"""
    __table__ = Table('cas_hiba', Base.metadata,
                    autoload=True, autoload_with=engine)

connection.execute('INSERT INTO token_table(termino_preferido, token, concept_id_hiba) SELECT termino_preferido, to_tsvector(termino_preferido) as token, "concept_id_HIBA" FROM cas_hiba ON CONFLICT (termino_preferido) DO NOTHING')

class Token_table(Base):
    """"""
    __table__ = Table('token_table', Base.metadata,
                    autoload=True, autoload_with=engine)

def loadSession():
    """"""
    metadata = Base.metadata
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

session = loadSession()