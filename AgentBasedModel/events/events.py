from AgentBasedModel.simulator import Simulator
from AgentBasedModel.agents import Trader, Universalist, Fundamentalist, MarketMaker
from AgentBasedModel.utils.orders import Order


class Event:
    def __init__(self, it: int):
        self.it = it  # Activation it
        self.simulator = None

    def call(self, it: int):
        if self.simulator is None:
            raise Exception('No simulator link found')
        if it != self.it:
            return True

    def link(self, simulator: Simulator):
        self.simulator = simulator
        return self


class FundamentalPriceShock(Event):
    def __init__(self, it: int, price_change: float):
        super().__init__(it)
        self.dp = price_change

    def __repr__(self):
        return f'Fundamental Price shock (it={self.it}, dp={self.dp})'

    def call(self, it: int):
        if super().call(it):
            return
        divs = self.simulator.exchange.dividend_book  # link to dividend book
        r = self.simulator.exchange.risk_free  # risk-free rate

        self.simulator.exchange.dividend_book = [div + self.dp * r for div in divs]


class MarketPriceShock(Event):
    def __init__(self, it: int, volume_change: float):
        super().__init__(it)
        self.volume = round(volume_change)

    def __repr__(self):
        return f'Market Price shock (it={self.it}, dp={self.volume})'

    def call(self, it: int):
        if super().call(it):
            return
        exchange = self.simulator.exchange
        pseudo_trader = Trader(exchange, 1e6, int(1e4))
        if self.volume < 0:  # buy
            order = Order(exchange.order_book['ask'].last.price, abs(self.volume), 'bid', pseudo_trader)
        else:  # sell
            order = Order(exchange.order_book['bid'].last.price, abs(self.volume), 'ask', pseudo_trader)
        exchange.market_order(order)


class InformationShock(Event):
    def __init__(self, it, access: int):
        super().__init__(it)
        self.access = access

    def __repr__(self):
        return f'Information shock (it={self.it}, access={self.access})'

    def call(self, it: int):
        if super().call(it):
            return
        for trader in self.simulator.traders:
            if type(trader) in (Universalist, Fundamentalist):
                trader.access = self.access


class MarketMakerIn(Event):
    def __init__(self, it, cash: float = 1e4):
        super().__init__(it)
        self.cash = cash

    def __repr__(self):
        return f'MarketMaker In (it={self.it}, cash={self.cash})'

    def call(self, it: int):
        if super().call(it):
            return

        maker = MarketMaker(self.simulator.exchange, self.cash)
        self.simulator.traders.append(maker)


class MarketMakerOut(Event):
    def __init__(self, it):
        super().__init__(it)

    def __repr__(self):
        return f'MarketMaker Out (it={self.it})'

    def call(self, it: int):
        if super().call(it):
            return

        self.simulator.traders = [tr for tr in self.simulator.traders if type(tr) != MarketMaker]


class TransactionCost(Event):
    def __init__(self, it, cost):
        super().__init__(it)
        self.cost = cost

    def __repr__(self):
        return f'Transaction cost (it={self.it}, cost={self.cost}%)'

    def call(self, it: int):
        if super().call(it):
            return

        self.simulator.exchange.transaction_cost = self.cost
