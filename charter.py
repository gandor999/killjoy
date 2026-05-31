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
            dt_obj = plt.matplotlib.dates.num2date(x)
            date_str = dt_obj.strftime('%d/%m/%y %I:%M:%S %p')
            return f"x = {date_str}, y = {y:.2f}"
        except (ValueError, OverflowError):
            return f"x = {x:.2f}, y = {y:.2f}"

    ax.format_coord = format_coord


def setup_crosshair_tool(ax):
    """
    Creates and attaches an interactive crosshair and data box 
    tracking system that directly tracks the mouse coordinates.
    """
    # Create the crosshair line elements (hidden by default)
    v_line = ax.axvline(color="gray", linestyle="--", linewidth=1, visible=False)
    h_line = ax.axhline(color="gray", linestyle="--", linewidth=1, visible=False)

    # Create a persistent text box in the upper-left corner of the plot area
    pointer_text = ax.text(
        0.125, 0.88, "",          # 0.125 aligns perfectly with the left edge of the chart
        transform=plt.gcf().transFigure, # <--- Change transAxes to transFigure
        fontsize=11, 
        fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.5", fc="black", alpha=0.75),
        color="white",
        verticalalignment="bottom",     # Aligns upward from the baseline coordinate
        zorder=5
    )

    def on_mouse_move(event):
        if event.inaxes == ax and event.xdata is not None and event.ydata is not None:
            x_mouse, y_mouse = event.xdata, event.ydata
            
            try:
                mouse_dt = plt.matplotlib.dates.num2date(x_mouse)
                date_str = mouse_dt.strftime('%d/%m/%y %I:%M:%S %p')
                val_str = f"{y_mouse:.2f}"
                
                # Position crosshair lines exactly at the mouse position
                v_line.set_xdata([x_mouse])
                h_line.set_ydata([y_mouse])
                v_line.set_visible(True)
                h_line.set_visible(True)
                
                # Update the overlay text content
                pointer_text.set_text(f"📍 Date: {date_str}\n📈 Index: {val_str}")
                pointer_text.set_visible(True)
                
            except (ValueError, OverflowError):
                v_line.set_visible(False)
                h_line.set_visible(False)
                pointer_text.set_visible(False)
                
            plt.gcf().canvas.draw_idle()
        else:
            if v_line.get_visible():
                v_line.set_visible(False)
                h_line.set_visible(False)
                pointer_text.set_visible(False)
                plt.gcf().canvas.draw_idle()

    plt.gcf().canvas.mpl_connect("motion_notify_event", on_mouse_move)


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

    # CRITICAL FIX: Lock down the limits using your real timeline data index bounds
    ax = plt.gca()
    ax.set_xlim(custom_index.index[0], custom_index.index[-1])
    ax.set_autoscale_on(False)  # Turn off auto-scale so 1970 never sneaks in

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

    # Activate interactive crosshair and status bar updates together
    setup_crosshair_tool(ax)
    setup_status_bar_formatter(ax)

    print("Displaying chart with updated layout...")
    plt.show()