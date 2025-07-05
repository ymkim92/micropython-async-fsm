try:
    import uasyncio as asyncio
    from ucollections import defaultdict
except ImportError:
    # for testing purposes, use standard asyncio if uasyncio is not available
    import asyncio
    from collections import defaultdict

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
        """Initialize the FSM with an initial state, a dictionary of states,
            and a transition table.
        Args:
            initial_state (AsyncState): The initial state of the FSM.
            states (dict, optional): A dictionary of states keyed by their names.
            transition_table (defaultdict, optional): A transition table mapping
            (state_name, message_id) to a list of (to_state_name, guard, action).
        Note: when it moves to a new state by different guards,
              it will execute the first guard that matches.
        """
        self.state = initial_state
        self.states = states or {}
        self.transition_table = transition_table or defaultdict(list)

    def add_state(self, state):
        self.states[state.name] = state

    def add_transition(self, from_state, message_id, to_state_name, guard=None, action=None):
        self.transition_table[(from_state, message_id)].append((to_state_name, guard, action))

    async def start(self, ctx):
        await self.state.on_enter_state(ctx)

    async def dispatch(self, ctx, message):
        key = (self.state.name, message.id)
        transition = self.transition_table.get(key)
        if transition is None:
            return  # No transition defined

        for to_state_name, guard, action in transition:
            if guard is None or guard(ctx, message):
                if action:
                    await action(ctx, message)
                await self.state.on_exit_state(ctx)
                self.state = self.states[to_state_name]
                await self.state.on_enter_state(ctx)
                break

    def current_state(self):
        return self.state.name
