import app_config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.model import Base
from aws.secret import get_aws_secret
import json


def setup_sql_engine(app):
    connection_string = get_sql_connection_string()
    # app.config['SQLALCHEMY_DATABASE_URI'] = connection_string
    engine = create_engine(connection_string, echo=app_config.DEBUG_SQL)
    Session = sessionmaker(bind=engine)

    Base.metadata.create_all(engine)
    return Session


def get_sql_connection_string():
    print("USING ARN:" + app_config.DB_SQL_SECRET_ARN)
    if app_config.DB_SQL_SECRET_ARN:
        secretStr = get_aws_secret(app_config.DB_SQL_SECRET_ARN, app_config.AWS_REGION)

        secret = json.loads(secretStr)

        username = secret["username"]
        password = secret["password"]
        host = app_config.DB_HOST
        dbname = app_config.DB_NAME
        port = app_config.DB_PORT
        print(host)

        connection_string = f"postgresql://{username}:{password}@{host}:{port}/{dbname}"
    else:
        connection_string = app_config.SQL_DATABASE_URI

    return connection_string
