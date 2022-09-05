from AgentBasedModel.simulator import SimulatorInfo
import AgentBasedModel.utils.math as math

from scipy.stats import kendalltau
import statsmodels.api as sm


def test_trend(values, category: bool = False, conf: float = .95) -> bool or dict:
    """
    Kendall’s Tau test.

    H0: No trend exists
    Ha: Some trend exists
    :return: True - trend exist, False - no trend
    """
    iterations = range(len(values))
    tau, p_value = kendalltau(iterations, values)
    if category:
        return p_value < (1 - conf)
    return {'tau': round(tau, 4), 'p-value': round(p_value, 4)}


def test_trend2(values, category: bool = False, conf: float = .95):
    """
    Linear regression on time.

    H0: No trend exists
    Ha: Some trend exists
    :return: True - trend exist, False - no trend
    """
    x = range(len(values))
    estimate = sm.OLS(values, sm.add_constant(x)).fit()
    if not category:
        return {'t-stat': round(estimate.tvalues[1], 4), 'p-value': round(estimate.pvalues[1], 4)}
    return estimate.pvalues[1] < (1 - conf)


def trend(info: SimulatorInfo, category: bool = False, size: int = None, rolling: int = 1):
    def cat(tau: float):
        if tau > .4:
            return 'bull'
        if tau < -.4:
            return 'bear'
        return 'stationary'

    prices = math.rolling(info.prices, rolling)
    if size is None:
        res = test_trend(prices)['tau']
        return res if not category else cat(res)

    res = [test_trend(prices[i*size:(i+1)*size])['tau'] for i in range(len(prices) // size)]
    return res if not category else [cat(v) for v in res]


def destruction(info: SimulatorInfo, category: bool = False, size: int = None, window: int = 5):
    def cat(tau: float):
        if tau > .6:
            return 'destructive'
        return 'stable'

    volatility = info.price_volatility(window)
    if size is None:
        res = test_trend(volatility)['tau']
        # res_cat = test_trend(volatility, True)
        return res if not category else cat(res)

    res = [test_trend(volatility[i*size:(i+1)*size])['tau'] for i in range(len(volatility) // size)]
    # res_cat = [test_trend(volatility[i * size:(i + 1) * size], True) for i in range(len(volatility) // size)]
    return res if not category else [cat(r) for r in res]


def efficiency(info: SimulatorInfo, category: bool = False, size: int = None, rolling: int = 1, access: int = 10):
    def cat(rel_dev):
        if rel_dev > .027:
            return 'inefficient'
        return 'efficient'

    market = math.rolling(info.prices, rolling)
    fundamental = math.rolling(info.fundamental_value(access), rolling)
    rel_d = [abs(market[i] - fundamental[i]) / fundamental[i] for i in range(len(market))]

    if size is None:
        res = round(math.mean(rel_d), 4)
        return res if not category else cat(res)

    res = [round(math.mean(rel_d[i*size:(i+1)*size]), 4) for i in range(len(rel_d) // size)]
    return res if not category else [cat(v) for v in res]


def general_states(info: SimulatorInfo, size: int = None, window: int = 5, access: int = 10) -> list:
    states_trend = trend(info, True, size, window)
    states_destruction = destruction(info, True, size, window)
    states_efficiency = efficiency(info, True, size, window, access)

    res = list()
    for t, d, e in zip(states_trend, states_destruction, states_efficiency):
        tmp = list()
        # if d == 'stable' and e == 'efficient':
        #     tmp.append('stable')
        if d == 'destructive':
            tmp.append('destructive')
        elif e == 'inefficient':
            tmp.append('speculative')
        elif t == 'bull':
            tmp.append('bullish')
        elif t == 'bear':
            tmp.append('bearish')
        elif t == 'stationary':  # todo надо ли
            tmp.append('stationary')

        res.append(tuple(tmp))
    return res
