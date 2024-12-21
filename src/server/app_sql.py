import app_config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from db.model import Base
from aws.secret import get_aws_secret
import json


def setup_sql_engine():
    connection_string = get_sql_connection_string()
    engine = create_engine(
        connection_string,
        pool_size=5,
        max_overflow=5,
        pool_timeout=30,
        pool_recycle=600,
        echo=app_config.DEBUG_SQL,
    )
    Session = sessionmaker(bind=engine)

    Base.metadata.create_all(engine)
    return Session


def setup_async_sql_engine():
    connection_string = get_sql_connection_string(is_async=True)
    async_engine = create_async_engine(
        connection_string,
        pool_size=5,
        max_overflow=5,
        pool_timeout=30,
        pool_recycle=600,
        echo=app_config.DEBUG_SQL,
    )

    Session = async_sessionmaker(
        bind=async_engine, expire_on_commit=False
    )

    return Session


def get_sql_connection_string(is_async=False):
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

        if is_async:
            connection_string = (
                f"postgresql+asyncpg://{username}:{password}@{host}:{port}/{dbname}"
            )
        else:
            connection_string = (
                f"postgresql://{username}:{password}@{host}:{port}/{dbname}"
            )
    else:
        connection_string = app_config.SQL_DATABASE_URI

    return connection_string
