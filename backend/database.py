import firebase_admin
from firebase_admin import credentials, firestore, auth
import os
import json

_db = None

def init_firebase():
    """Initialize Firebase Admin SDK."""
    global _db
    if firebase_admin._apps:
        _db = firestore.client()
        return

    # Load from env variable (JSON string) or file path
    firebase_cred_env = os.getenv("FIREBASE_CREDENTIALS")
    firebase_cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase_credentials.json")

    if firebase_cred_env:
        cred_dict = json.loads(firebase_cred_env)
        cred = credentials.Certificate(cred_dict)
    elif os.path.exists(firebase_cred_path):
        cred = credentials.Certificate(firebase_cred_path)
    else:
        # Demo mode — use emulator / mock
        print("⚠️  WARNING: No Firebase credentials found. Running in DEMO mode.")
        print("   Set FIREBASE_CREDENTIALS env var or provide firebase_credentials.json")
        _db = MockFirestore()
        return

    firebase_admin.initialize_app(cred)
    _db = firestore.client()
    print("✅ Firebase connected successfully")


def get_db():
    """Return Firestore client."""
    global _db
    if _db is None:
        init_firebase()
    return _db


def get_auth():
    """Return Firebase Auth client."""
    return auth


# ─────────────────────────────────────────────
# MOCK FIRESTORE  (for demo / local dev without
# real Firebase credentials)
# ─────────────────────────────────────────────
class MockDocument:
    def __init__(self, data=None):
        self._data = data or {}
        self.exists = data is not None

    def to_dict(self):
        return self._data

    @property
    def id(self):
        return self._data.get("id", "mock-id")


class MockCollection:
    def __init__(self, store, name):
        self._store = store
        self._name = name

    def document(self, doc_id=None):
        return MockDocRef(self._store, self._name, doc_id or "auto-id")

    def where(self, *args):
        return MockQuery(self._store, self._name, args)

    def add(self, data):
        import uuid
        doc_id = str(uuid.uuid4())
        key = f"{self._name}/{doc_id}"
        self._store[key] = {**data, "id": doc_id}
        return None, MockDocRef(self._store, self._name, doc_id)

    def order_by(self, *args):
        return MockQuery(self._store, self._name, [])

    def limit(self, n):
        return MockQuery(self._store, self._name, [])

    def stream(self):
        prefix = f"{self._name}/"
        for k, v in self._store.items():
            if k.startswith(prefix):
                yield MockDocument(v)


class MockDocRef:
    def __init__(self, store, collection, doc_id):
        self._store = store
        self._col = collection
        self._id = doc_id

    @property
    def id(self):
        return self._id

    def get(self):
        key = f"{self._col}/{self._id}"
        data = self._store.get(key)
        return MockDocument(data)

    def set(self, data, merge=False):
        key = f"{self._col}/{self._id}"
        if merge and key in self._store:
            self._store[key].update(data)
        else:
            self._store[key] = {**data, "id": self._id}

    def update(self, data):
        key = f"{self._col}/{self._id}"
        if key in self._store:
            self._store[key].update(data)
        else:
            self._store[key] = {**data, "id": self._id}

    def delete(self):
        key = f"{self._col}/{self._id}"
        self._store.pop(key, None)

    def collection(self, name):
        return MockCollection(self._store, f"{self._col}/{self._id}/{name}")


class MockQuery:
    def __init__(self, store, collection, filters):
        self._store = store
        self._col = collection

    def where(self, *args):
        return self

    def order_by(self, *args):
        return self

    def limit(self, n):
        return self

    def stream(self):
        prefix = f"{self._col}/"
        for k, v in self._store.items():
            if k.startswith(prefix) and k.count("/") == prefix.count("/"):
                yield MockDocument(v)

    def get(self):
        return list(self.stream())


class MockFirestore:
    def __init__(self):
        self._store = {}

    def collection(self, name):
        return MockCollection(self._store, name)
