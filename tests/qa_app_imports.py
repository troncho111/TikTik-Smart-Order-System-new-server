"""
QA: Verify app.py has all required top-level names (no NameError at runtime).
Run: python -m tests.qa_app_imports  or  pytest tests/qa_app_imports.py -v
"""
import sys
from pathlib import Path

# Project root
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_app_module_loads():
    """App module must load without NameError (all imports and names defined)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("app", ROOT / "app.py")
    app = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(app)
    return app


def test_critical_names_exist():
    """Names used in page_new_order (flights, passports, paste, airports, etc.) must exist."""
    app = test_app_module_loads()
    required = [
        "io",
        "json",
        "random",
        "requests",
        "paste_image_button",
        "get_team_map_path",
        "get_airport_options",
        "get_airport_code",
        "format_airport_display",
        "extract_flight_data",
        "extract_passport_data",
        "resolve_hotel_safe",
        "get_airline_from_flight",
        "page_new_order",
        "main",
    ]
    for name in required:
        assert hasattr(app, name), f"app.py missing required name: {name}"
