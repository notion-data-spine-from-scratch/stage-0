# tests/test_models.py
import warnings
import pytest

warnings.filterwarnings("ignore")

pytestmark = pytest.mark.db


def test_metadata_reflects_tables():
    from app.models import metadata

    expected = {
        "users",
        "workspaces",
        "blocks",
        "plans",
        "workspace_plans",
        "block_acl",
    }

    # Ensure all expected tables have been loaded
    assert expected.issubset(set(metadata.tables.keys()))
