from AgentBasedModel import *
import matplotlib.pyplot as plt


exchange = ExchangeAgent(volume=1000)
simulator = Simulator(**{
    'exchange': exchange,
    'traders': [Fundamentalist(exchange, 10**3) for _ in range(20)],
    'events': [MarketMakerIn(0)]
})
info = simulator.info

simulator.simulate(500)
plot_price_fundamental(info)
