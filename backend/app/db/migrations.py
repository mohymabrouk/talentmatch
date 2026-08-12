from pathlib import Path

from sqlalchemy import Engine, text


def _migration_statements(contents: str) -> list[str]:
    return [statement.strip() for statement in contents.split(";") if statement.strip()]


def run_migrations(engine: Engine, migration_dir: Path | None = None) -> None:
    directory = migration_dir or Path(__file__).resolve().parents[3] / "infra" / "sql"
    migration_files = sorted(directory.glob("*.sql"))
    if not migration_files:
        raise RuntimeError(f"No SQL migrations found in {directory}")

    with engine.begin() as connection:
        connection.execute(
            text(
                "CREATE TABLE IF NOT EXISTS schema_migrations "
                "(version VARCHAR(255) PRIMARY KEY, applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)"
            )
        )
        applied = {
            row[0]
            for row in connection.execute(text("SELECT version FROM schema_migrations")).fetchall()
        }
        for migration_file in migration_files:
            version = migration_file.name
            if version in applied:
                continue
            for statement in _migration_statements(migration_file.read_text(encoding="utf-8")):
                connection.exec_driver_sql(statement)
            connection.execute(
                text("INSERT INTO schema_migrations (version) VALUES (:version)"),
                {"version": version},
            )

