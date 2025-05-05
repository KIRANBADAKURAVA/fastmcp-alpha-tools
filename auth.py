# Modified auth.py to ensure session is valid

import ace_lib as ace
import pickle
import os
import time

SESSION_FILE = "session.pkl"
_session = None
CHECK_INTERVAL = 300  # seconds (5 minutes)


def save_session(session):
    try:
        with open(SESSION_FILE, "wb") as f:
            pickle.dump(session, f)
        print("Session saved.")
    except Exception as e:
        print(f"Failed to save session: {e}")


def load_session_from_file():
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "rb") as f:
                session = pickle.load(f)
            print("Loaded session from file.")
            return session
        except Exception as e:
            print(f"Failed to load session: {e}")
    return None


def create_new_session():
    print("Starting new session. Please complete biometric verification.")
    session = ace.start_session()
    save_session(session)
    return session


def get_session():
    global _session

    if _session and not ace.check_session_timeout(_session):
        # Check if session is actually valid with the API
        if ace.validate_session(_session):  # Add this function to ace_lib
            return _session
        else:
            print("Session invalid or expired despite local check passing.")
            _session = None

    session = load_session_from_file()
    if session and not ace.check_session_timeout(session):
        # Check if loaded session is actually valid with the API
        if ace.validate_session(session):  # Add this function to ace_lib
            _session = session
            return _session
        else:
            print("Loaded session invalid or expired despite local check passing.")

    _session = create_new_session()
    return _session


def session_monitor():
    print("Session monitor started. Checking every", CHECK_INTERVAL, "seconds.")
    while True:
        session = get_session()
        print("Session is valid.")
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    session_monitor()


# New function to add to ace_lib.py
