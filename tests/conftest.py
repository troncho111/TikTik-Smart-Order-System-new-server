"""
Pytest fixtures for TikTik E2E tests.
Assumes Streamlit app is already running at BASE_URL (e.g. streamlit run app.py --server.port 8505).
Or set BASE_URL env var.
"""
import os

import pytest

BASE_URL = os.environ.get("TIKTIK_E2E_BASE_URL", "http://localhost:8505")


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL
