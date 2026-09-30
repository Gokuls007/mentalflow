from pydantic import TypeAdapter, EmailStr

from app.config import Settings


def test_default_demo_email_passes_login_validation():
    # Login/register use EmailStr; a reserved TLD like .local would make the demo account unusable
    TypeAdapter(EmailStr).validate_python(Settings.model_fields["DEMO_USER_EMAIL"].default)


def test_cors_origins_accepts_comma_separated_env(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:5173, http://localhost:5174")
    assert Settings(_env_file=None).CORS_ORIGINS == ["http://localhost:5173", "http://localhost:5174"]


def test_cors_origins_accepts_json_list_env(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", '["http://a.example", "http://b.example"]')
    assert Settings(_env_file=None).CORS_ORIGINS == ["http://a.example", "http://b.example"]
