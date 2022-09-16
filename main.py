from AgentBasedModel import *
from AgentBasedModel.events.states import *


exchange = ExchangeAgent(volume=2000)
simulator = Simulator(**{
    'exchange': exchange,
    'traders': [Chartist(exchange, 10**3) for _ in range(20)],
    # 'events': [MarketMakerIn(250)]
})
info = simulator.info

simulator.simulate(100)
plot_price(info)

print(trend(info, 10))
print(panic(info, 10, 5))
print(disaster(info, 10, 5))
print(mean_rev(info, 10, 5))
print()
print(general_states(info, 10, 5))
