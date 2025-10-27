sessions = {}

def add_session(token, user):
    print(f"DEBUG: Adding session - Token: '{token}', User: {user}")
    sessions[token] = user
    print(f"DEBUG: Current sessions: {sessions}")

def remove_session(token):
    return sessions.pop(token, None)

def get_session(token):
    print(f"DEBUG: Looking up session for token: '{token}'")
    print(f"DEBUG: Available sessions: {list(sessions.keys())}")
    result = sessions.get(token)
    print(f"DEBUG: Session lookup result: {result}")
    return result