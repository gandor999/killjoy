from util import get_chart_dimensions
from charter import generate_custom_index_chart

dims = get_chart_dimensions()

tickers = [
    "GS",    # Goldman Sachs
    "QBTS",  # D-Wave Quantum
    "NVDA",  # NVIDIA
    "MU",    # Micron Technology
    "AAPL",  # Apple
    "KO",    # Coca-Cola
    "GOOG",  # Alphabet (Class C)
    "AMZN",  # Amazon
    "TSM",   # Taiwan Semiconductor
    "SNDK",  # SanDisk (Delisted/Legacy data)
    "DELL"   # Dell Technologies
]

generate_custom_index_chart(tickers, dims)
