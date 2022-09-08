from AgentBasedModel.simulator import Simulator


def aggToShock(sim: Simulator, window: int, funcs: list) -> dict:
    """
    Aggregate market statistics in respect to market shocks

    :param sim: Simulator object
    :param funcs: [('func_name', func), ...]. Function accepts SimulatorInfo object and roll or window variable
    :param window: 1 to n
    :return:
    """
    return {str(event): {f_name: {
        'start': f(sim.info, window)[0],
        'before': f(sim.info, window)[:event.it - window] if event.it - window > 0 else [],
        'right before': f(sim.info, window)[event.it - window - 1] if event.it - window - 1 >= 0 else [],
        'after': f(sim.info, window)[event.it - window:],
        'right after': f(sim.info, window)[event.it - window],
        'end': f(sim.info, window)[-1]
    } for f_name, f in funcs} for event in sim.events}
