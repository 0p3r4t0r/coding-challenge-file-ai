from dotenv import load_dotenv

import psycopg
import pytest
import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session


@pytest.fixture(scope="session", autouse=True)
def load_env():
    load_dotenv("./tests/.env.test")


@pytest.fixture(scope="session", autouse=True)
def postgres_up(load_env):
    dsn = (
        f"dbname={os.environ['POSTGRES_DB']} "
        f"user={os.environ['POSTGRES_USER']} "
        f"password={os.environ['POSTGRES_PASSWORD']} "
        f"host={os.environ['POSTGRES_HOST']} "
        f"port={os.environ['POSTGRES_PORT']}"
    )

    try:
        with psycopg.connect(dsn):
            return
    except psycopg.OperationalError:
        raise RuntimeError(
            "Postgres not ready. Did you run `docker-compose --profile test up -d`?"
        )


@pytest.fixture(scope="session")
def test_engine():
    """Connect to the existing test database (schema already initialized via Docker)."""
    engine = create_engine(
        f"postgresql+psycopg://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}@"
        f"{os.environ['POSTGRES_HOST']}:{os.environ.get('POSTGRES_PORT', 5433)}/"
        f"{os.environ['POSTGRES_DB']}"
    )
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(test_engine):
    connection = test_engine.connect()
    transaction = connection.begin()

    session = Session(bind=connection)

    # Start a SAVEPOINT
    session.begin_nested()

    # Restart SAVEPOINT after each rollback (IntegrityError, etc.)
    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(sess, trans):
        if trans.nested and not trans._parent.nested:
            sess.begin_nested()

    yield session

    session.close()
    transaction.rollback()
    connection.close()
