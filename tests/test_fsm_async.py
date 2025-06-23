"""FSM for running"""

from async_fsm.fsm_async import AsyncState, AsyncFSM
import pytest
from logger.null_logger import NullLogger


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
        ctx["timer"] = 0

    async def on_event(self, ctx, message):
        if isinstance(message, Timeout):
            logger = ctx.get("logger", NullLogger())
            logger.error(">>> Idle timeout, going to Error")
            return "Error"
        return self.name


class Running(AsyncState):
    async def on_enter_state(self, ctx):
        logger = ctx.get("logger", NullLogger())
        logger.info(">>> Entered Running state")
        ctx["task"] = "doing work"

    async def on_exit_state(self, ctx):
        logger = ctx.get("logger", NullLogger())
        logger.info("<<< Exiting Running state")
        ctx["task"] = None


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
