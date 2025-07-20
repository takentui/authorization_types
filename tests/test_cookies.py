import datetime

from app.auth import active_sessions
from app.db import USERS


def test_protected_route_update_expired(client, session_token):
    """Test protected route with valid cookie."""
    now = datetime.datetime.now().timestamp()
    active_sessions[session_token].expired = now
    response = client.get("/protected", cookies={"session_token": session_token})
    assert response.status_code == 200
    assert response.json()["message"] == "This is a protected route"
    assert response.json()["authenticated_user"] == USERS[0].username
    # Verify session was created
    session_token = response.cookies["session_token"]
    assert session_token in active_sessions
    assert active_sessions[session_token].user_id == 0

    assert active_sessions[session_token].expired > now
