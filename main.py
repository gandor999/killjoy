from util import get_chart_dimensions
from chart.generate import generate_custom_index_chart

dims = get_chart_dimensions()

tickers = [
    "GS",
    "QBTS",
    "NVDA",
    "MU",
    "AAPL",
    "KO",
    "GOOG",
    "AMZN",
    "TSM",
    "SNDK",
    "DELL",
    "AMD",
]

generate_custom_index_chart(tickers, dims)
