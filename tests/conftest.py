import os

import filelock
import pytest

import conda_forge_tick
from conda_forge_tick import global_sensitive_env


@pytest.fixture(scope="session")
def serial_lock(tmp_path_factory) -> filelock.BaseFileLock:
    """
    A lock that is used to ensure that tests that request the `serial` fixture do not run in parallel with each other.
    """
    # see https://github.com/pytest-dev/pytest-xdist/issues/84
    base_temp = tmp_path_factory.getbasetemp()
    lock_file = base_temp.parent / "serial.lock"
    yield filelock.FileLock(lock_file)
    lock_file.unlink(missing_ok=True)


@pytest.fixture()
def serial(serial_lock: filelock.BaseFileLock) -> None:
    """
    Tests that request this fixture do not run in parallel with each other.
    """
    with serial_lock.acquire():
        yield


@pytest.fixture(scope="session")
def mongodb_available() -> bool:
    return (
        "MONGODB_CONNECTION_STRING"
        in conda_forge_tick.global_sensitive_env.classified_info
        and conda_forge_tick.global_sensitive_env.classified_info[
            "MONGODB_CONNECTION_STRING"
        ]
        is not None
    )


@pytest.fixture(autouse=True)
def skip_requires_mongodb(request, mongodb_available):
    """
    Automatically skip all tests annotated with `@pytest.mark.mongodb` if MongoDB is not available.

    Also add the `serial` fixture to tests annotated with `@pytest.mark.mongodb` to ensure that they do not
    run in parallel with each other. In the future, MongoDB tests should be refactored to not require this.
    """
    if not request.node.get_closest_marker("mongodb"):
        return
    if not mongodb_available:
        pytest.skip("MongoDB not available")  # implicit return
    request.node.fixturenames.append("serial")


@pytest.fixture
def env_setup():
    if "TEST_BOT_TOKEN_VAL" not in os.environ:
        old_pwd = os.environ.pop("BOT_TOKEN", None)
        os.environ["BOT_TOKEN"] = "unpassword"
        global_sensitive_env.hide_env_vars()

    old_pwd2 = os.environ.pop("pwd", None)
    os.environ["pwd"] = "pwd"

    yield

    if "TEST_BOT_TOKEN_VAL" not in os.environ:
        global_sensitive_env.reveal_env_vars()
        if old_pwd:
            os.environ["BOT_TOKEN"] = old_pwd

    if old_pwd2:
        os.environ["pwd"] = old_pwd2


@pytest.fixture(autouse=True, scope="session")
def set_cf_tick_pytest_envvar():
    old_ci = os.environ.get("CF_TICK_PYTEST")
    if old_ci is None:
        os.environ["CF_TICK_PYTEST"] = "true"
    yield
    if old_ci is None:
        del os.environ["CF_TICK_PYTEST"]
    else:
        os.environ["CF_TICK_PYTEST"] = old_ci


@pytest.fixture(autouse=True, scope="session")
def turn_off_containers_by_default():
    old_in_container = os.environ.get("CF_TICK_IN_CONTAINER")

    # tell the code we are in a container so that it
    # doesn't try to run docker commands
    os.environ["CF_TICK_IN_CONTAINER"] = "true"

    yield

    if old_in_container is None:
        os.environ.pop("CF_TICK_IN_CONTAINER", None)
    else:
        os.environ["CF_TICK_IN_CONTAINER"] = old_in_container


@pytest.fixture
def use_containers():
    old_in_container = os.environ.get("CF_TICK_IN_CONTAINER")

    os.environ["CF_TICK_IN_CONTAINER"] = "false"

    yield

    if old_in_container is None:
        os.environ.pop("CF_TICK_IN_CONTAINER", None)
    else:
        os.environ["CF_TICK_IN_CONTAINER"] = old_in_container
