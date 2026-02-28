import os


def pytest_configure():
    os.environ.setdefault("AUTH_JWKS_URL", "http://jwks.local")
    os.environ.setdefault("AUTH_ISSUER", "auth-service")
    os.environ.setdefault("AUTH_AUDIENCE", "user-children-service")
    os.environ.setdefault("AUTH_ALGORITHMS", "RS256")
