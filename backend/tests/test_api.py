from app.ai.adaptive_assessment import AdaptiveAssessmentIRT


def test_health(client):
    assert client.get("/health").json()["status"] == "ok"


def test_register_login_and_profile(client, auth_headers):
    r = client.get("/api/v1/users/me", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["email"] == "demo.patient@example.com"


def test_adaptive_score_reflects_answers():
    none = {i: 0 for i in range(1, 10)}
    severe = {i: 3 for i in range(1, 10)}
    mixed = {1: 1, 2: 2, 3: 0, 4: 1, 5: 3, 6: 0, 7: 2, 8: 1, 9: 0}
    for responses in (none, severe, mixed):
        theta = AdaptiveAssessmentIRT.estimate_theta(responses)
        assert AdaptiveAssessmentIRT.map_theta_to_score(theta) == sum(responses.values())


def test_adaptive_submit_twice_same_day(client, auth_headers):
    body = {"responses": {str(i): 1 for i in range(1, 10)}}
    r1 = client.post("/api/v1/assessments/adaptive/submit", json=body, headers=auth_headers)
    r2 = client.post("/api/v1/assessments/adaptive/submit", json=body, headers=auth_headers)
    assert r1.status_code == 200 and r2.status_code == 200, (r1.text, r2.text)
    assert r2.json()["score"] == 9
    assert r2.json()["severity"] == "mild"
    assert r2.json()["crisis_level"] == 1


def test_adaptive_rejects_unknown_item(client, auth_headers):
    r = client.post("/api/v1/assessments/adaptive/next-question",
                    json={"responses": {"42": 1}}, headers=auth_headers)
    assert r.status_code == 422


def test_progress_me_route(client, auth_headers):
    r = client.get("/api/v1/clinical/progress/me", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert "depression" in r.json()


def test_crisis_message_is_logged(client, auth_headers):
    r = client.post("/api/v1/chat/message", json={"message": "I want to hurt myself"}, headers=auth_headers)
    assert r.status_code == 200, r.text
    assert r.json()["intent"] == "CRISIS"
    assert "988" in r.json()["content"]


def test_chat_history_is_private(client, auth_headers):
    me = client.get("/api/v1/users/me", headers=auth_headers).json()["id"]
    assert client.get(f"/api/v1/chat/history/{me}", headers=auth_headers).status_code == 200
    assert client.get(f"/api/v1/chat/history/{me + 100}", headers=auth_headers).status_code == 403
    assert client.delete(f"/api/v1/chat/history/{me + 100}").status_code == 403


def test_rl_and_game_loop(client, auth_headers):
    me = client.get("/api/v1/users/me", headers=auth_headers).json()["id"]
    r = client.get(f"/api/v1/rl/predict-difficulty/{me}")
    assert r.status_code == 200, r.text
    assert r.json()["difficulty"] in ("EASY", "MEDIUM", "HARD")

    r = client.post(f"/api/v1/gan/generate-activity/{me}")
    assert r.status_code == 200, r.text
    activity_id = r.json()["id"]

    r = client.post("/api/v1/rl/submit-game-results", json={
        "activity_id": activity_id, "score": 120, "duration": 60, "completed": True,
        "mood_before": 4, "mood_after": 6, "engagement_rating": 8, "difficulty_level": "easy",
    }, headers=auth_headers)
    assert r.status_code == 200, r.text
    assert r.json()["xp_earned"] > 0

    assert client.get(f"/api/v1/rl/metrics/{me}").status_code == 200
    assert client.get(f"/api/v1/gan/metrics/{me}").status_code == 200


def test_activities_and_moods(client, auth_headers):
    r = client.get("/api/v1/activities/", headers=auth_headers)
    assert r.status_code == 200, r.text
    r = client.post("/api/v1/moods/", json={"mood_score": 7}, headers=auth_headers)
    assert r.status_code == 201, r.text
    r = client.get("/api/v1/moods/today", headers=auth_headers)
    assert r.status_code == 200 and len(r.json()) == 1
    assert client.get("/api/v1/moods/trend", headers=auth_headers).status_code == 200
