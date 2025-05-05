# auth.py
import ace_lib as ace
import pickle
import os

SESSION_FILE = "session.pkl"
_session = None


def get_session():
    global _session
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, 'rb') as f:
            _session = pickle.load(f)
        print("Session loaded from file.")
    else:
        _session = ace.start_session()
        with open(SESSION_FILE, 'wb') as f:
            pickle.dump(_session, f)
        print("New session started and saved.")

    return _session


if __name__ == "__main__":
    print("Starting session manually...")
    get_session()
    print("Session initialized and ready.")
