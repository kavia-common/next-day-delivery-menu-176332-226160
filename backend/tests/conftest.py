"""
Pytest fixtures for the Flask backend.

How to run:
- From the backend folder:
    pip install -r requirements.txt
    pytest -q

These fixtures use the application defined in app.__init__.py and Flask's
built-in test_client for isolated request testing without starting a server.
"""

import os
import pytest

# Ensure Flask runs in testing mode for predictable behavior
os.environ.setdefault("FLASK_ENV", "testing")


@pytest.fixture(scope="session")
def app():
    """
    Provides the Flask app instance from the backend package.

    Note:
    - The app is created in app/__init__.py as a module-level singleton.
    - If a factory is introduced later, adjust this fixture accordingly to
      initialize with a testing config and any in-memory dependencies.
    """
    from app import app as flask_app  # import from backend/app/__init__.py
    # Make sure testing flags are set for Flask
    flask_app.config.update(
        TESTING=True,
    )
    return flask_app


@pytest.fixture
def client(app):
    """
    Provides a Flask test client for issuing requests to the app.
    """
    with app.test_client() as client:
        yield client
