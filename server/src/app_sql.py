import app_config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.model import Base

def setup_sql_engine(app):
    if app_config.DB_HOSTNAME:
        connection_string = f"postgresql://{app_config.DB_USERNAME}:{app_config.DB_PASSWORD}@{app_config.DB_HOSTNAME}:5432/{app_config.DB_NAME}"
    else: connection_string = app_config.SQL_DATABASE_URI 
    
    
    app.config['SQLALCHEMY_DATABASE_URI'] = connection_string
    engine = create_engine(connection_string, echo=True)
    Session = sessionmaker(bind=engine)

    Base.metadata.create_all(engine)
    return Session