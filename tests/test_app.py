import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture()
def test_activity():
    name = "Test Activity"
    activities[name] = {
        "description": "Testing",
        "schedule": "Now",
        "max_participants": 5,
        "participants": [],
    }
    try:
        yield name
    finally:
        activities.pop(name, None)


client = TestClient(app)


def test_get_activities_includes_test_activity(test_activity):
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert test_activity in data
    assert isinstance(data[test_activity]["participants"], list)


def test_signup_and_unregister_success(test_activity):
    email = "student@test.edu"
    # Sign up
    resp_signup = client.post(
        f"/activities/{test_activity}/signup", params={"email": email}
    )
    assert resp_signup.status_code == 200
    assert email in activities[test_activity]["participants"]

    # Unregister
    resp_unreg = client.delete(
        f"/activities/{test_activity}/signup", params={"email": email}
    )
    assert resp_unreg.status_code == 200
    assert email not in activities[test_activity]["participants"]


def test_duplicate_signup_error(test_activity):
    email = "dupe@test.edu"
    client.post(f"/activities/{test_activity}/signup", params={"email": email})
    resp = client.post(f"/activities/{test_activity}/signup", params={"email": email})
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Student already signed up for this activity"


def test_unregistered_delete_error(test_activity):
    email = "notregistered@test.edu"
    resp = client.delete(
        f"/activities/{test_activity}/signup", params={"email": email}
    )
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Student not registered for this activity"


def test_activity_not_found_errors():
    email = "someone@test.edu"
    resp_signup = client.post(
        "/activities/Nonexistent/signup", params={"email": email}
    )
    resp_unreg = client.delete(
        "/activities/Nonexistent/signup", params={"email": email}
    )
    assert resp_signup.status_code == 404
    assert resp_unreg.status_code == 404
