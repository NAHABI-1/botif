from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from mt5_platform_db.db.base import Base, DATABASE_SCHEMA, validate_schema_identifier
from mt5_platform_db.models import __all__ as _loaded_models  # noqa: F401
from mt5_platform_db.settings import settings

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _get_database_url() -> str:
    return settings.database_url


def _configure_context(connection: object | None = None) -> None:
    config.set_main_option("sqlalchemy.url", _get_database_url())
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
        include_schemas=True,
        version_table_schema=DATABASE_SCHEMA,
    )


def run_migrations_offline() -> None:
    _configure_context()
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        schema_name = validate_schema_identifier(DATABASE_SCHEMA)
        connection.exec_driver_sql(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
        _configure_context(connection=connection)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
