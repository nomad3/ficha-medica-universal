from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Importaciones directas
import models
from database import SQLALCHEMY_DATABASE_URL

config = context.config
fileConfig(config.config_file_name)
target_metadata = models.Base.metadata

def run_migrations_online():
    connectable = engine_from_config(
        {"sqlalchemy.url": SQLALCHEMY_DATABASE_URL},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    print("Offline mode not supported")
else:
    run_migrations_online() 