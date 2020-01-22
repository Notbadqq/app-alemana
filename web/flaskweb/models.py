from werkzeug.security import generate_password_hash, check_password_hash
from flaskweb import db

from sqlalchemy import create_engine, MetaData, Table, select
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
    def __repr__(self):
        return "{'concepto_id':%s, 'description_nombre':%s, 'description_id':%s, 'concept_id_HIBA':%s, 'tipo_termino':%s, 'termino_preferido':%s}" % (self.concepto_id, self.description_nombre, self.description_id, self.concept_id_HIBA, self.tipo_termino, self.termino_preferido)
    
def loadSession():
    """"""
    metadata = Base.metadata
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

session = loadSession()