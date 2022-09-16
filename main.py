from AgentBasedModel import *
from AgentBasedModel.events.states import *


exchange = ExchangeAgent(volume=2000)
simulator = Simulator(**{
    'exchange': exchange,
    'traders': [
        *[Chartist(exchange, 10**3) for _ in range(20)],
    ],
    'events': [MarketMakerIn(200, softlimit=100)]
})
info = simulator.info

simulator.simulate(500)
plot_price(info, spread=False)
plot_liquidity(info)
