from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


client = TestClient(app_module.app)
BASE_ACTIVITIES = deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset in-memory activity state between tests."""
    app_module.activities.clear()
    app_module.activities.update(deepcopy(BASE_ACTIVITIES))

def test_get_activities_returns_seeded_data():
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert "participants" in payload["Chess Club"]


def test_signup_adds_participant():
    # Arrange
    activity_path = "/activities/Chess%20Club/signup"
    query_params = {"email": "newstudent@mergington.edu"}

    # Act
    response = client.post(
        activity_path,
        params=query_params,
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == "Signed up newstudent@mergington.edu for Chess Club"
    assert "newstudent@mergington.edu" in app_module.activities["Chess Club"]["participants"]


def test_signup_rejects_duplicate_participant():
    # Arrange
    activity_path = "/activities/Chess%20Club/signup"
    query_params = {"email": "michael@mergington.edu"}

    # Act
    response = client.post(
        activity_path,
        params=query_params,
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_signup_rejects_unknown_activity():
    # Arrange
    activity_path = "/activities/Unknown%20Club/signup"
    query_params = {"email": "student@mergington.edu"}

    # Act
    response = client.post(
        activity_path,
        params=query_params,
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"

def test_unregister_removes_participant():
    # Arrange
    activity_path = "/activities/Chess%20Club/participants"
    query_params = {"email": "michael@mergington.edu"}

    # Act
    response = client.delete(
        activity_path,
        params=query_params,
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == "Unregistered michael@mergington.edu from Chess Club"
    assert "michael@mergington.edu" not in app_module.activities["Chess Club"]["participants"]


def test_unregister_rejects_unknown_participant():
    # Arrange
    activity_path = "/activities/Chess%20Club/participants"
    query_params = {"email": "ghost@mergington.edu"}

    # Act
    response = client.delete(
        activity_path,
        params=query_params,
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
