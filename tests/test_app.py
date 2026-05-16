import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the in-memory activities state after each test."""
    original_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original_activities))


def test_get_activities_returns_all_activities():
    # Arrange
    client = TestClient(app)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    json_data = response.json()
    assert isinstance(json_data, dict)
    assert "Chess Club" in json_data
    assert "Programming Class" in json_data


def test_signup_for_activity_success():
    # Arrange
    client = TestClient(app)
    activity_name = "Chess Club"
    new_email = "test.student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": new_email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {new_email} for {activity_name}"}
    assert new_email in activities[activity_name]["participants"]


def test_signup_for_unknown_activity_returns_404():
    # Arrange
    client = TestClient(app)
    unknown_activity = "Nonexistent Club"

    # Act
    response = client.post(
        f"/activities/{unknown_activity}/signup",
        params={"email": "student@mergington.edu"}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_duplicate_email_returns_400():
    # Arrange
    client = TestClient(app)
    activity_name = "Chess Club"
    duplicate_email = "michael@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": duplicate_email}
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_from_activity_success():
    # Arrange
    client = TestClient(app)
    activity_name = "Chess Club"
    registered_email = "michael@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": registered_email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {registered_email} from {activity_name}"}
    assert registered_email not in activities[activity_name]["participants"]


def test_unregister_not_registered_returns_404():
    # Arrange
    client = TestClient(app)
    activity_name = "Chess Club"
    missing_email = "unknown.student@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": missing_email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not registered for this activity"
