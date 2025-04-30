# tests/test_models.py
import warnings

warnings.filterwarnings("ignore")


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
