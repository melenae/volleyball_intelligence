from app.core.config import Settings


def test_cors_origin_list_trims_empty_entries() -> None:
    settings = Settings(
        app_env="test",
        database_url="postgresql+psycopg://vi:vi@localhost:5433/volleyball_intelligence",
        cors_origins=" http://localhost:3000 , ,http://127.0.0.1:3000 ",
    )

    assert settings.cors_origin_list == [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
