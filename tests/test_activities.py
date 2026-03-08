"""
Unit tests for FastAPI activities endpoints.

Tests use the Arrange-Act-Assert (AAA) pattern:
- Arrange: Set up test data and preconditions
- Act: Perform the action being tested
- Assert: Verify the results
"""

import pytest
from fastapi.testclient import TestClient


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client: TestClient):
        """Arrange: Prepare client with initialized app.
        Act: Call GET /activities.
        Assert: Verify all activities are returned."""
        # Arrange
        expected_activity_count = 9
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class", "Basketball Team",
            "Tennis Club", "Art Studio", "Drama Club", "Debate Team", "Science Club"
        ]

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == expected_activity_count
        for activity_name in expected_activities:
            assert activity_name in activities

    def test_get_activities_returns_correct_structure(self, client: TestClient):
        """Arrange: Prepare client.
        Act: Call GET /activities and check the structure.
        Assert: Verify each activity has required fields."""
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert response.status_code == 200
        for activity_name, activity_data in activities.items():
            for field in required_fields:
                assert field in activity_data, f"Missing field '{field}' in {activity_name}"

    def test_get_activities_participants_are_lists(self, client: TestClient):
        """Arrange: Prepare client.
        Act: Call GET /activities.
        Assert: Verify participants field is a list."""
        # Arrange

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert response.status_code == 200
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["participants"], list), \
                f"Participants in {activity_name} should be a list"


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_successful_for_existing_activity(self, client: TestClient):
        """Arrange: Prepare a new email not yet signed up.
        Act: Sign up the email for an existing activity.
        Assert: Verify signup succeeds and returns confirmation."""
        # Arrange
        activity_name = "Chess Club"
        new_email = "neustudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert new_email in data["message"]
        assert activity_name in data["message"]

    def test_signup_adds_participant_to_activity(self, client: TestClient):
        """Arrange: Get initial participant list and prepare new email.
        Act: Sign up for activity.
        Assert: Verify participant is added to the activity."""
        # Arrange
        activity_name = "Programming Class"
        new_email = "participant123@mergington.edu"
        get_response = client.get("/activities")
        initial_participants = get_response.json()[activity_name]["participants"].copy()

        # Act
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )

        # Assert - verify signup response
        assert signup_response.status_code == 200

        # Assert - verify participant was added
        get_response = client.get("/activities")
        updated_participants = get_response.json()[activity_name]["participants"]
        assert new_email in updated_participants
        assert len(updated_participants) == len(initial_participants) + 1

    def test_signup_fails_for_nonexistent_activity(self, client: TestClient):
        """Arrange: Prepare a non-existent activity name.
        Act: Attempt to sign up for it.
        Assert: Verify signup fails with 404."""
        # Arrange
        nonexistent_activity = "NonExistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_fails_for_duplicate_signup(self, client: TestClient):
        """Arrange: Find an activity with existing participants.
        Act: Try to sign up with an email already in that activity.
        Assert: Verify signup fails with 400 and appropriate message."""
        # Arrange
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_email}
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_multiple_different_emails_succeeds(self, client: TestClient):
        """Arrange: Prepare multiple different emails.
        Act: Sign up each email for the same activity.
        Assert: Verify all signups succeed."""
        # Arrange
        activity_name = "Tennis Club"
        emails = ["test1@mergington.edu", "test2@mergington.edu", "test3@mergington.edu"]

        # Act & Assert
        for email in emails:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200, f"Signup failed for {email}"


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/participants/{email} endpoint."""

    def test_remove_participant_successful(self, client: TestClient):
        """Arrange: Find an activity with participants.
        Act: Remove an existing participant.
        Assert: Verify removal succeeds and returns confirmation."""
        # Arrange
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email_to_remove}"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email_to_remove in data["message"]
        assert activity_name in data["message"]

    def test_remove_participant_actually_removes_from_activity(self, client: TestClient):
        """Arrange: Get initial participant list.
        Act: Remove a participant.
        Assert: Verify participant is no longer in activity."""
        # Arrange
        activity_name = "Science Club"
        email_to_remove = "benjamin@mergington.edu"
        get_response = client.get("/activities")
        initial_participants = get_response.json()[activity_name]["participants"].copy()

        # Act
        remove_response = client.delete(
            f"/activities/{activity_name}/participants/{email_to_remove}"
        )

        # Assert - verify removal response
        assert remove_response.status_code == 200

        # Assert - verify participant was removed
        get_response = client.get("/activities")
        updated_participants = get_response.json()[activity_name]["participants"]
        assert email_to_remove not in updated_participants
        assert len(updated_participants) == len(initial_participants) - 1

    def test_remove_participant_fails_for_nonexistent_activity(self, client: TestClient):
        """Arrange: Prepare a non-existent activity name.
        Act: Try to remove participant from it.
        Assert: Verify fails with 404."""
        # Arrange
        nonexistent_activity = "Fake Activity"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{nonexistent_activity}/participants/{email}"
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_remove_participant_fails_when_not_enrolled(self, client: TestClient):
        """Arrange: Prepare an email not enrolled in an activity.
        Act: Try to remove that email from the activity.
        Assert: Verify fails with 400 and appropriate message."""
        # Arrange
        activity_name = "Drama Club"
        non_enrolled_email = "notstudent@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{non_enrolled_email}"
        )

        # Assert
        assert response.status_code == 400
        assert "Participant not found" in response.json()["detail"]

    def test_remove_multiple_participants_succeeds(self, client: TestClient):
        """Arrange: Get all participants from an activity.
        Act: Remove each participant one by one.
        Assert: Verify all removals succeed."""
        # Arrange
        activity_name = "Science Club"
        get_response = client.get("/activities")
        initial_participants = get_response.json()[activity_name]["participants"].copy()

        # Act & Assert
        for email in initial_participants:
            response = client.delete(
                f"/activities/{activity_name}/participants/{email}"
            )
            assert response.status_code == 200, f"Removal failed for {email}"


class TestActivityIntegration:
    """Integration tests combining multiple endpoints."""

    def test_signup_and_remove_workflow(self, client: TestClient):
        """Arrange: Prepare new email.
        Act: Sign up and then remove the participant.
        Assert: Verify both operations succeed and state is correct."""
        # Arrange
        activity_name = "Art Studio"
        new_email = "workflow_test@mergington.edu"
        get_response = client.get("/activities")
        initial_count = len(get_response.json()[activity_name]["participants"])

        # Act - Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )

        # Assert - Sign up succeeded
        assert signup_response.status_code == 200
        get_response = client.get("/activities")
        after_signup_count = len(get_response.json()[activity_name]["participants"])
        assert after_signup_count == initial_count + 1

        # Act - Remove
        remove_response = client.delete(
            f"/activities/{activity_name}/participants/{new_email}"
        )

        # Assert - Remove succeeded
        assert remove_response.status_code == 200
        get_response = client.get("/activities")
        final_count = len(get_response.json()[activity_name]["participants"])
        assert final_count == initial_count
        assert new_email not in get_response.json()[activity_name]["participants"]

    def test_concurrent_signups_different_activities(self, client: TestClient):
        """Arrange: Prepare email for signing up to multiple activities.
        Act: Sign up for multiple different activities.
        Assert: Verify signup succeeds for all activities."""
        # Arrange
        email = "multi_signup@mergington.edu"
        activities_to_join = ["Debate Team", "Basketball Team", "Drama Club"]

        # Act & Assert
        for activity_name in activities_to_join:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200, f"Signup failed for {activity_name}"

        # Verify all signups are reflected
        get_response = client.get("/activities")
        activities_data = get_response.json()
        for activity_name in activities_to_join:
            assert email in activities_data[activity_name]["participants"]
