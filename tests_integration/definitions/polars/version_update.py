from pathlib import Path

from fastapi import APIRouter

from tests_integration.lib.integration_test_helper import IntegrationTestHelper

router = APIRouter()


@router.get("/pypi.org/pypi/polars/json")
def handle():
    return {
        # rest omitted
        "info": {"name": "polars", "version": "1.20.0"}
    }


def prepare(helper: IntegrationTestHelper):
    feedstock_dir = Path(__file__).parent / "resources" / "feedstock"
    helper.overwrite_feedstock_contents("polars", feedstock_dir)


def validate(helper: IntegrationTestHelper):
    helper.assert_version_pr_present(
        "polars",
        new_version="1.20.0",
        new_hash="e8e9e3156fae02b58e276e5f2c16a5907a79b38617a9e2d731b533d87798f451",
        old_version="1.17.1",
        old_hash="5a3dac3cb7cbe174d1fa898cba9afbede0c08e8728feeeab515554d762127019",
    )
