import datetime
import yfinance as yf
import matplotlib.pyplot as plt


def setup_status_bar_formatter(ax):
    """
    Overrides the default Matplotlib bottom toolbar coordinates
    to display a clean date string in DD/MM/YY hh:mm:ss AM/PM format.
    """

    def format_coord(x, y):
        try:
            # Convert the X-axis number back into a datetime object
            dt_obj = plt.matplotlib.dates.num2date(x)

            # Format using %I for 12-hour clock and %p for AM/PM
            date_str = dt_obj.strftime("%d/%m/%y %I:%M:%S %p")
            return f"x = {date_str}, y = {y:.2f}"
        except (ValueError, OverflowError):
            return f"x = {x:.2f}, y = {y:.2f}"

    ax.format_coord = format_coord


def calculate_ytd_roi(index_series):
    current_year = datetime.datetime.now().year
    ytd_start_str = f"{current_year}-01-01"

    current_year_data = index_series[index_series.index >= ytd_start_str]

    if not current_year_data.empty:
        ytd_start_value = current_year_data.iloc[0]
        current_value = current_year_data.iloc[-1]
        return ((current_value - ytd_start_value) / ytd_start_value) * 100

    return 0.00


def get_roi_theme(ytd_roi):
    if ytd_roi >= 0:
        return {"text": f"YTD ROI: {ytd_roi:+.2f}%", "color": "#90EE90"}  # Light Green
    else:
        return {"text": f"YTD ROI: {ytd_roi:+.2f}%", "color": "#FF7F7F"}  # Light Red


def generate_custom_index_chart(
    tickers, dims, start_date="2016-05-01", end_date="2026-05-31"
):
    print("Fetching stock data...")
    data = yf.download(tickers, start=start_date, end=end_date)["Close"]
    data = data.dropna(how="all")

    normalized_data = data / data.bfill().iloc[0]
    custom_index = normalized_data.mean(axis=1) * 100

    ytd_roi = calculate_ytd_roi(custom_index)
    theme = get_roi_theme(ytd_roi)

    plt.figure(figsize=(dims["width"], dims["height"]))
    plt.plot(
        custom_index,
        color="#ff9900",
        linewidth=2.5,
        label=f"Custom Basket Index ({theme['text']})",
    )

    # 1. Main Title (Large, bold, default font)
    plt.figtext(
        0.5,
        0.95,
        "10-Year Custom Basket Index Growth",
        fontsize=15,
        fontweight="bold",
        fontname="Arial",
        ha="center",
    )

    plt.figtext(
        0.5,
        0.90,
        f"({theme['text']})",
        fontsize=12,
        fontweight="bold",
        fontstyle="italic",
        fontname="Arial",
        color=theme["color"],
        ha="center",
    )

    # Adjust layout spacing to accommodate the figtext titles cleanly
    plt.subplots_adjust(top=0.85)

    plt.xlabel("Year", fontsize=12)
    plt.ylabel("Index Value (Starts at 100)", fontsize=12)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend(loc="upper left", fontsize=11)

    # Apply the toolbar coordinate fix to the current axes object
    setup_status_bar_formatter(plt.gca())

    print("Displaying chart with updated layout...")
    plt.show()
