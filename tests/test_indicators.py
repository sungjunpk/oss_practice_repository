import pytest

from deeptrader.indicators import rsi, sma


def test_sma():
    assert sma([1, 2, 3, 4, 5], 3) == [2, 3, 4]


def test_sma_invalid_window():
    with pytest.raises(ValueError):
        sma([1, 2], 3)


def test_rsi_monotonic():
    assert rsi(list(range(1, 20)), 14)[-1] == 100.0
    assert rsi(list(range(20, 1, -1)), 14)[-1] == 0.0


def test_rsi_flat_is_neutral():
    assert rsi([10.0] * 20, 14) == [50.0] * 6


def test_rsi_bounds():
    prices = [44, 44.3, 44.1, 43.6, 44.3, 44.8, 45.1, 45.4, 45.8, 46.1, 45.9, 46.0, 45.6, 46.3,
              46.3, 46.0, 46.5, 46.2, 45.7]
    assert all(0 <= v <= 100 for v in rsi(prices, 14))
