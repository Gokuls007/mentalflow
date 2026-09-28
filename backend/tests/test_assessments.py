import pytest

from app.config import settings

PHQ9 = "/api/v1/assessments/phq9"
GAD7 = "/api/v1/assessments/gad7"


def _phq9_with_total(total, item9=0):
    """9 item scores summing to `total`, with item 9 fixed."""
    items = [0] * 8
    remaining = total - item9
    for i in range(8):
        items[i] = min(3, remaining)
        remaining -= items[i]
    assert remaining == 0
    return items + [item9]


def _gad7_with_total(total):
    items = [0] * 7
    remaining = total
    for i in range(7):
        items[i] = min(3, remaining)
        remaining -= items[i]
    return items


@pytest.mark.parametrize("total,severity", [
    (0, "minimal"), (4, "minimal"), (5, "mild"), (9, "mild"), (10, "moderate"),
    (14, "moderate"), (15, "moderately severe"), (19, "moderately severe"),
    (20, "severe"), (24, "severe"),
])
def test_phq9_cutoffs(client, auth_headers, total, severity):
    r = client.post(PHQ9, json={"responses": _phq9_with_total(total)}, headers=auth_headers)
    assert r.status_code == 200, r.text
    assert r.json()["score"] == total
    assert r.json()["severity"] == severity
    assert r.json()["crisis_level"] == 0


def test_phq9_max_score(client, auth_headers):
    r = client.post(PHQ9, json={"responses": [3] * 9}, headers=auth_headers)
    assert r.json()["score"] == 27 and r.json()["severity"] == "severe"


@pytest.mark.parametrize("total,severity", [
    (0, "minimal"), (4, "minimal"), (5, "mild"), (9, "mild"),
    (10, "moderate"), (14, "moderate"), (15, "severe"), (21, "severe"),
])
def test_gad7_cutoffs(client, auth_headers, total, severity):
    r = client.post(GAD7, json={"responses": _gad7_with_total(total)}, headers=auth_headers)
    assert r.status_code == 200, r.text
    assert r.json()["score"] == total
    assert r.json()["severity"] == severity
    assert r.json()["crisis_level"] == 0


@pytest.mark.parametrize("url,responses", [
    (PHQ9, [0] * 8),            # too few items
    (PHQ9, [0] * 10),           # too many items
    (PHQ9, [0] * 8 + [4]),      # score above 3
    (PHQ9, [-1] + [0] * 8),     # negative score
    (GAD7, [0] * 9),            # PHQ-9 length sent to GAD-7
    (GAD7, [0] * 6 + [5]),
])
def test_invalid_submissions_rejected(client, auth_headers, url, responses):
    r = client.post(url, json={"responses": responses}, headers=auth_headers)
    assert r.status_code == 422


@pytest.mark.parametrize("item9", [1, 2, 3])
def test_phq9_item9_sets_crisis_flag(client, auth_headers, item9):
    r = client.post(PHQ9, json={"responses": [0] * 8 + [item9]}, headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["crisis_level"] == 1


def test_same_day_upsert_and_progress(client):
    creds = {"email": "upsert.check@example.com", "password": "password123"}
    assert client.post("/api/v1/users/register", json=creds).status_code == 201
    token = client.post("/api/v1/users/login", json=creds).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    first = client.post(PHQ9, json={"responses": [2] * 9}, headers=headers).json()
    second = client.post(PHQ9, json={"responses": [1] * 9}, headers=headers).json()
    assert first["id"] == second["id"]          # same record updated, not duplicated
    assert second["score"] == 9

    me = client.get("/api/v1/users/me", headers=headers).json()
    assert me["latest_phq9_score"] == 9

    progress = client.get("/api/v1/clinical/progress/me", headers=headers).json()
    # Only one PHQ-9 on record, so the corrected same-day result is the baseline
    assert progress["depression"]["baseline"] == 9
    assert progress["depression"]["current"] == 9


def test_demo_user_seeded_and_used_without_token(client):
    from app.db.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        demo = db.query(User).filter_by(email=settings.DEMO_USER_EMAIL).one()
    assert demo.id == 1

    r = client.post(GAD7, json={"responses": [1] * 7})
    assert r.status_code == 200
    assert client.get("/api/v1/clinical/progress/me").status_code == 200
    assert client.get(f"/api/v1/rl/predict-difficulty/{demo.id}").status_code == 200


def test_seed_is_idempotent():
    from app.db.database import SessionLocal
    from app.db.seed import seed_demo_user
    from app.models.user import User

    with SessionLocal() as db:
        before = db.query(User).count()
        seed_demo_user(db)
        assert db.query(User).count() == before


def test_invalid_token_is_not_treated_as_demo(client):
    r = client.post(PHQ9, json={"responses": [0] * 9}, headers={"Authorization": "Bearer nonsense"})
    assert r.status_code == 401
