"""FSM for running"""

from async_fsm.fsm_async import AsyncState, AsyncFSM
import pytest
import pytest_asyncio
from logger.null_logger import NullLogger
from unittest.mock import AsyncMock, Mock


# Event
#
class Message:
    def __init__(self, id):
        self.id = id


class Start(Message):
    def __init__(self):
        super().__init__("Start")


class Stop(Message):
    def __init__(self):
        super().__init__("Stop")


class Timeout(Message):
    def __init__(self):
        super().__init__("Timeout")


# State
#
class Idle(AsyncState):
    async def on_enter_state(self, ctx):
        logger = ctx.get("logger", NullLogger())
        logger.info(">>> Entering Idle state")


class Running(AsyncState):
    async def on_enter_state(self, ctx):
        logger = ctx.get("logger", NullLogger())
        logger.info(">>> Entered Running state")

    async def on_exit_state(self, ctx):
        logger = ctx.get("logger", NullLogger())
        logger.info("<<< Exiting Running state")


class Error(AsyncState):
    async def on_enter_state(self, ctx):
        logger = ctx.get("logger", NullLogger())
        logger.error(">>> Entered Error")


@pytest.mark.asyncio
async def test_fsm_basic_transitions():
    ctx = {"enabled": True}

    idle = Idle("Idle")
    running = Running("Running")
    error = Error("Error")

    fsm = AsyncFSM(idle)
    fsm.add_state(idle)
    fsm.add_state(running)
    fsm.add_state(error)

    # Define the action for Start event
    async def on_start(ctx, message):
        logger = ctx.get("logger", NullLogger())
        logger.info("Executing Start action")
        ctx["started_at"] = "10:00"

    # Define transitions
    fsm.add_transition(
        "Idle", "Start", "Running", guard=lambda ctx, msg: ctx.get("enabled"), action=on_start
    )
    fsm.add_transition("Idle", "Timeout", "Error")
    fsm.add_transition("Running", "Stop", "Idle")
    fsm.add_transition("Running", "Timeout", "Error")

    await fsm.start(ctx)
    assert fsm.current_state() == "Idle"

    assert "started_at" not in ctx  # Ensure 'started_at' is set after Start action
    await fsm.dispatch(ctx, Start())
    assert "started_at" in ctx  # Ensure 'started_at' is set after Start action
    assert ctx["started_at"] == "10:00"
    assert fsm.current_state() == "Running"

    await fsm.dispatch(ctx, Stop())
    assert fsm.current_state() == "Idle"

    await fsm.dispatch(ctx, Timeout())
    assert fsm.current_state() == "Error"

    # Dispatching Stop in Error should not change state
    await fsm.dispatch(ctx, Stop())
    assert fsm.current_state() == "Error"


@pytest_asyncio.fixture
async def test_fsm_idle_fixture():
    mock_action = AsyncMock()

    # These should return different values
    mock_guard_enabled = Mock(return_value=True)
    mock_guard_disabled = Mock(return_value=False)

    mock_timeout_guard = Mock(return_value=False)

    idle = Idle("Idle")
    running = Running("Running")
    error = Error("Error")

    states = {"Idle": idle, "Running": running, "Error": error}
    transition_table = {
        ("Idle", "Start"): [
            ("Running", mock_guard_enabled, mock_action),
            ("Idle", mock_guard_disabled, mock_action),
        ],
        ("Idle", "Timeout"): [("Error", mock_timeout_guard, None)],
    }
    fsm = AsyncFSM(idle, states=states, transition_table=transition_table)
    ctx = {}
    await fsm.start(ctx)

    return fsm, ctx, mock_action, mock_guard_enabled, mock_guard_disabled, mock_timeout_guard


@pytest.mark.asyncio
async def test_fsm_idle_to_running(test_fsm_idle_fixture):
    fsm, ctx, mock_action, mock_guard_enabled, _, _ = test_fsm_idle_fixture

    assert isinstance(fsm.state, Idle)
    assert fsm.current_state() == "Idle"
    start_message = Start()
    await fsm.dispatch(ctx, start_message)

    assert fsm.current_state() == "Running"
    assert isinstance(fsm.state, Running)
    mock_action.assert_awaited_once_with(ctx, start_message)
    mock_guard_enabled.assert_called_once_with(ctx, start_message)


@pytest.mark.asyncio
async def test_fsm_idle_to_idle_when_disabled(test_fsm_idle_fixture):
    fsm, ctx, _, mock_guard_enabled, mock_guard_disabled, _ = test_fsm_idle_fixture

    mock_guard_enabled.return_value = False
    mock_guard_disabled.return_value = True

    assert isinstance(fsm.state, Idle)
    assert fsm.current_state() == "Idle"
    start_message = Start()
    await fsm.dispatch(ctx, start_message)

    assert fsm.current_state() == "Idle"
    assert isinstance(fsm.state, Idle)
    mock_guard_disabled.assert_called_once_with(ctx, start_message)


@pytest.mark.asyncio
async def test_fsm_idle_to_idle_no_timeout(test_fsm_idle_fixture):
    fsm, ctx, _, _, _, mock_timeout_guard = test_fsm_idle_fixture

    assert isinstance(fsm.state, Idle)
    assert fsm.current_state() == "Idle"
    timeout_message = Timeout()
    await fsm.dispatch(ctx, timeout_message)

    assert fsm.current_state() == "Idle"
    assert isinstance(fsm.state, Idle)
    mock_timeout_guard.assert_called_once_with(ctx, timeout_message)


@pytest.mark.asyncio
async def test_fsm_idle_to_error(test_fsm_idle_fixture):
    fsm, ctx, _, _, _, mock_timeout_guard = test_fsm_idle_fixture
    mock_timeout_guard.return_value = True

    assert isinstance(fsm.state, Idle)
    assert fsm.current_state() == "Idle"
    timeout_message = Timeout()
    await fsm.dispatch(ctx, timeout_message)

    assert fsm.current_state() == "Error"
    assert isinstance(fsm.state, Error)
    mock_timeout_guard.assert_called_once_with(ctx, timeout_message)
