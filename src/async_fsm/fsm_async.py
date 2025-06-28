try:
    import uasyncio as asyncio
except ImportError:
    # for testing purposes, use standard asyncio if uasyncio is not available
    import asyncio

_ = asyncio  # Silence Ruff F401: used for compatibility with uasyncio


class AsyncState:
    def __init__(self, name):
        self.name = name

    async def on_enter_state(self, ctx):
        pass

    async def on_exit_state(self, ctx):
        pass


class AsyncFSM:
    def __init__(self, initial_state, states=None, transition_table=None):
        self.state = initial_state
        self.states = states or {}
        self.transition_table = transition_table or {}  # key: (state_name, message_id)

    def add_state(self, state):
        self.states[state.name] = state

    def add_transition(self, from_state, message_id, to_state_name, guard=None, action=None):
        self.transition_table[(from_state, message_id)] = (to_state_name, guard, action)

    async def start(self, ctx):
        await self.state.on_enter_state(ctx)

    async def dispatch(self, ctx, message):
        key = (self.state.name, message.id)
        transition = self.transition_table.get(key)

        if transition:
            to_state_name, guard, action = transition
            if guard is None or guard(ctx, message):
                if action:
                    await action(ctx, message)
                await self.state.on_exit_state(ctx)
                self.state = self.states[to_state_name]
                await self.state.on_enter_state(ctx)

    def current_state(self):
        return self.state.name
