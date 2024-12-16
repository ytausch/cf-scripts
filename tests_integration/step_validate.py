"""
Runs the validate() functions of all test cases of the current test scenario to make test assertions.

Expects the scenario ID to be present in the environment variable SCENARIO_ID.
"""

import logging
import os

from tests_integration.collect_test_scenarios import get_test_scenario
from tests_integration.lib.integration_test_helper import IntegrationTestHelper
from tests_integration.lib.shared import (
    ENV_TEST_SCENARIO_ID,
    get_test_case_modules,
    setup_logging,
)


def run_all_validate_functions(scenario: dict[str, str]):
    test_helper = IntegrationTestHelper()
    for test_module in get_test_case_modules(scenario):
        try:
            logging.info("Validating %s...", test_module.__name__)
            test_module.validate(test_helper)
        except AttributeError:
            raise AttributeError("The test case must define a validate() function.")


def main(scenario_id: int):
    scenario = get_test_scenario(scenario_id)
    run_all_validate_functions(scenario)


if __name__ == "__main__":
    setup_logging(logging.INFO)
    main(int(os.environ[ENV_TEST_SCENARIO_ID]))
