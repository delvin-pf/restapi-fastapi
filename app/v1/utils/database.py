from contextvars import ContextVar
# noinspection PyProtectedMember
from peewee import PostgresqlDatabase, _ConnectionState
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_NAME = os.environ.get('DATABASE')
DATABASE_HOST = os.environ.get('HOST')
DATABASE_PORT = os.environ.get('PORT')
DATABASE_USER = os.environ.get('USER')
DATABASE_PASS = os.environ.get('PASSWORD')

db_state_default = {
    "closed": None,
    "conn": None,
    "ctx": None,
    "transactions": None
}
db_state = ContextVar("db_state", default=db_state_default.copy())


class PeeweeConnectionState(_ConnectionState):
    def __init__(self, **kwargs):
        super().__setattr__('_state', db_state)
        super().__init__(**kwargs)

    def __setattr__(self, name, value):
        self._state.get()[name] = value

    def __getattr__(self, name):
        return self._state.get()[name]


dbSql = PostgresqlDatabase(
    DATABASE_NAME,
    host=DATABASE_HOST,
    port=DATABASE_PORT,
    user=DATABASE_USER,
    password=DATABASE_PASS,
    autorollback=True
)
dbSql._state = PeeweeConnectionState()
