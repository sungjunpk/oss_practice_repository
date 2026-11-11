"""기술적 지표 — 모델 입력 피처용. 외부 의존성 없이 순수 파이썬."""


def sma(values: list[float], n: int) -> list[float]:
    """단순 이동평균. 길이는 len(values) - n + 1."""
    if n <= 0 or n > len(values):
        raise ValueError("n 은 1 이상, 데이터 길이 이하여야 한다")
    window = sum(values[:n])
    out = [window / n]
    for i in range(n, len(values)):
        window += values[i] - values[i - n]
        out.append(window / n)
    return out


def rsi(prices: list[float], n: int = 14) -> list[float]:
    """Wilder RSI (0~100). 길이는 len(prices) - n."""
    if n <= 0 or len(prices) <= n:
        raise ValueError("가격은 n+1 개 이상 필요하다")
    deltas = [b - a for a, b in zip(prices, prices[1:], strict=False)]
    gain = sum(max(d, 0) for d in deltas[:n]) / n
    loss = sum(max(-d, 0) for d in deltas[:n]) / n

    def value() -> float:
        if gain == loss == 0:
            return 50.0
        return 100.0 if loss == 0 else 100 - 100 / (1 + gain / loss)

    out = [value()]
    for d in deltas[n:]:
        gain = (gain * (n - 1) + max(d, 0)) / n
        loss = (loss * (n - 1) + max(-d, 0)) / n
        out.append(value())
    return out
