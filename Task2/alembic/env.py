import os
import sys
from logging.config import fileConfig
from app.models import *  # Импортируем все модели из пакета `models`
from sqlalchemy import engine_from_config, pool
from alembic import context

# Добавляем корневую директорию проекта в PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Импортируем Base из моделей
#from app.models import Base  # Убедитесь, что путь правильный
from app.database import Base
# Получаем объект конфигурации Alembic
config = context.config

# Настройка логирования на основе alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Устанавливаем метаданные для автогенерации миграций
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Запуск миграций в 'офлайн' режиме."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Запуск миграций в 'онлайн' режиме."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


# Определяем, в каком режиме запускать миграции
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
