import datetime
import yfinance as yf
import matplotlib.pyplot as plt

from chart.calculation import calculate_ytd_roi
from chart.setup import (
    setup_crosshair_tool,
    setup_right_click_pan,
    setup_scroll_zoom,
    setup_status_bar_formatter,
)
from chart.theme import get_roi_theme


def generate_custom_index_chart(
    tickers, dims, start_date="2016-05-01", end_date="2026-05-31"
):
    print("Fetching stock data...")
    data = yf.download(tickers, start=start_date, end=end_date)["Close"]
    data = data.dropna(how="all")

    # Core Data Calculations
    normalized_data = data / data.bfill().iloc[0]
    custom_index = normalized_data.mean(axis=1) * 100

    ytd_roi = calculate_ytd_roi(custom_index)
    theme = get_roi_theme(ytd_roi)

    # Package arguments cleanly into a dictionary parameter
    chart_arguments = {
        "custom_index": custom_index,
        "theme": theme,
        "ytd_roi": ytd_roi,
        "dims": dims,
        "start_date": start_date,
        "end_date": end_date,
        "tickers": tickers
    }

    # Pass the unified dictionary to the visualization layer
    ax = plot_custom_index(chart_arguments)

    # Activate interactive mouse tracking tools
    setup_crosshair_tool(ax)
    setup_status_bar_formatter(ax)
    setup_scroll_zoom(ax)
    setup_right_click_pan(ax)

    print("Displaying chart with updated layout...")
    plt.show()


def plot_custom_index(plot_params):
    """
    Handles all figure creation, axis limits, grid styling,
    dynamic title strings, and multi-color subtitle rendering.
    Expects a dictionary containing: custom_index, theme, ytd_roi,
    dims, start_date, and end_date.
    """
    # Unpack values from the dictionary parameter
    custom_index = plot_params["custom_index"]
    theme = plot_params["theme"]
    ytd_roi = plot_params["ytd_roi"]
    dims = plot_params["dims"]
    start_date = plot_params["start_date"]
    end_date = plot_params["end_date"]
    tickers = plot_params.get("tickers", [])

    plt.figure(figsize=(dims["width"], dims["height"]))
    plt.plot(
        custom_index,
        color="#ff9900",
        linewidth=2.5,
        label=f"Custom Basket Index ({theme['text']})",
    )

    # Lock down the limits using your real timeline data index bounds
    ax = plt.gca()
    ax.set_xlim(custom_index.index[0], custom_index.index[-1])
    ax.set_autoscale_on(False)  # Turn off auto-scale so 1970 never sneaks in

    # DYNAMIC TITLE CALCULATION (Rounds down to nearest full year)
    start_dt = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    num_years = (end_dt - start_dt).days // 365

    # 1. Main Title (Large, bold, default font)
    plt.figtext(
        0.5,
        0.95,
        f"{num_years}-Year Custom Basket Index Growth",
        fontsize=15,
        fontweight="bold",
        fontname="Arial",
        ha="center",
    )

    # 2. Subtitle: Multi-color text layout (Parentheses removed)
    label_start = "YTD ROI: "
    label_value = f"{ytd_roi:+.2f}%"

    # We plot each piece side-by-side inside the figure whitespace
    ax.text(
        0.5,
        1.03,
        label_start,
        color="black",
        fontsize=12,
        fontweight="bold",
        fontstyle="italic",
        fontname="Arial",
        ha="right",
        transform=ax.transAxes,
    )

    # Render the number piece using your dynamic theme color
    ax.text(
        0.5,
        1.03,
        label_value,
        color=theme["color"],
        fontsize=12,
        fontweight="bold",
        fontstyle="italic",
        fontname="Arial",
        ha="left",
        transform=ax.transAxes,
    )

    # Adjust layout spacing to accommodate titles cleanly without overlapping the box
    plt.subplots_adjust(top=0.85)
    
    plot_component_assets_footer(tickers)

    plt.xlabel("Year", fontsize=12)
    plt.ylabel("Index Value (Starts at 100)", fontsize=12)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend(loc="upper left", fontsize=11)

    return ax


def plot_component_assets_footer(tickers):
    """
    Renders a clean, horizontal component asset tracker box at the
    bottom of the chart figure window.
    """
    if not tickers:
        return

    # Format the tickers array cleanly: "Component Assets: AAPL  •  MSFT  •  GOOGL"
    ticker_string = "Component Assets:  " + "   •   ".join([str(t) for t in tickers])

    # Place it directly under the X-axis line using stable figure coordinates
    plt.figtext(
        0.5,
        0.02,
        ticker_string,
        fontsize=10,
        fontweight="bold",
        fontname="Arial",
        color="#555555",
        ha="center",
        bbox=dict(boxstyle="round,pad=0.4", fc="#f7f7f7", ec="#e0e0e0", alpha=0.9),
    )
