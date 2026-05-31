import datetime
import yfinance as yf
import matplotlib.pyplot as plt

from chart.calculation import calculate_ytd_roi
from chart.classes.BlittedCrosshairWithOverlay import BlittedCrosshairWithOverlay
from chart.classes.ComponentAssetFooter import ComponentAssetFooter
from chart.setup import (
    setup_crosshair_tool,
    setup_right_click_pan,
    setup_scroll_zoom,
    setup_status_bar_formatter,
)
from chart.theme import get_roi_theme
from constants.constants_strings import COMPONENT_ASSETS, INDEX_TITLE, YEAR
from constants.constants_theme import (
    CHART_INDEX_COLOR,
    COMPONENT_ASSET_FOOTER_EDGE_COLOR,
    COMPONENT_ASSET_FOOTER_FACE_COLOR,
    COMPONENT_ASSET_FOOTER_TEXT_COLOR,
    GENERAL_FONT_STYLE,
    GENERAL_FONT_WEIGHT,
    GENERAL_FONTNAME,
)


def generate_custom_index_chart(
    tickers, dims, start_date="2016-05-01", end_date="2026-05-31"
):
    # Package arguments cleanly into a dictionary parameter
    chart_arguments = {
        "dims": dims,
        "start_date": start_date,
        "end_date": end_date,
        "tickers": tickers,
    }

    # Pass the unified dictionary to the visualization layer
    ax = plot_custom_index(chart_arguments)

    # Activate interactive mouse tracking tools
    setup_crosshair_tool(ax)

    active_pan_state = setup_right_click_pan(ax)
    ax.crosshair = BlittedCrosshairWithOverlay(ax, pan_state=active_pan_state)
    setup_status_bar_formatter(ax)
    setup_scroll_zoom(ax)

    print("Displaying chart with updated layout...")
    plt.show()


def refresh_index_chart(ax, tickers, start_date, end_date):
    """
    Standalone global function managing the complete chart re-render pipeline.
    Re-downloads data, recalculates live index returns, shifts crosshair event maps,
    and redraws widget overlays.
    """
    fig = ax.figure
    ax.clear()

    # 1. Gracefully handle an empty asset pool scenario
    if not tickers:
        ax.set_title("No Assets Selected", color="red", fontsize=12, fontstyle="italic")
        ax.grid(True, linestyle="--", alpha=0.5)
        if hasattr(ax, "footer") and ax.footer:
            ax.footer.render_ui()
        fig.canvas.draw_idle()
        return

    try:
        # 2. Re-download and rebuild normalized index matrix
        print(f"Updating data matrix for tickers: {tickers}...")
        data = yf.download(tickers, start=start_date, end=end_date, progress=False)[
            "Close"
        ]
        data = data.dropna(how="all")

        normalized_data = data / data.bfill().iloc[0]
        current_index_data = normalized_data.mean(axis=1) * 100

        # 3. Calculate true up-to-date metrics and dynamic UI theme settings
        updated_ytd_roi = calculate_ytd_roi(current_index_data)
        live_theme = get_roi_theme(updated_ytd_roi)

        # 4. Render main historical line performance plot curve
        ax.plot(
            current_index_data,
            color=CHART_INDEX_COLOR,
            linewidth=2.5,
            label=f"{INDEX_TITLE} ({live_theme['text']})",
        )
        ax.set_xlim(current_index_data.index[0], current_index_data.index[-1])
        ax.set_autoscale_on(False)

        # 5. Stamp fresh multi-color metric tracking headers
        label_start = "YTD ROI: "
        label_value = f"{updated_ytd_roi:+.2f}%"

        ax.text(
            0.5,
            1.03,
            label_start,
            color="black",
            fontsize=12,
            fontweight=GENERAL_FONT_WEIGHT,
            fontstyle=GENERAL_FONT_STYLE,
            fontname=GENERAL_FONTNAME,
            ha="right",
            transform=ax.transAxes,
        )
        ax.text(
            0.5,
            1.03,
            label_value,
            color=live_theme["color"],
            fontsize=12,
            fontweight=GENERAL_FONT_WEIGHT,
            fontstyle=GENERAL_FONT_STYLE,
            fontname=GENERAL_FONTNAME,
            ha="left",
            transform=ax.transAxes,
        )

        # 6. Re-apply standardized structural padding layouts
        ax.set_xlabel(YEAR, fontsize=11, fontweight="bold", labelpad=8)
        ax.set_ylabel(
            "Index Value (Starts at 100)", fontsize=11, fontweight="bold", labelpad=10
        )
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.legend(loc="upper left", fontsize=11)

        # 7. Restore active tracking tools and blitted crosshair canvas bindings
        setup_crosshair_tool(ax)
        active_pan_state = setup_right_click_pan(ax)
        ax.crosshair = BlittedCrosshairWithOverlay(ax, pan_state=active_pan_state)
        setup_status_bar_formatter(ax)
        setup_scroll_zoom(ax)

    except Exception as e:
        ax.text(
            0.5,
            0.5,
            f"Data Error: {str(e)}",
            color="red",
            ha="center",
            transform=ax.transAxes,
        )

    # 8. Re-render control layout menu ribbons and flush active canvas pipeline
    if hasattr(ax, "footer") and ax.footer:
        ax.footer.render_ui()
    fig.canvas.draw_idle()


def plot_custom_index(plot_params):
    """
    Handles all figure creation, axis limits, grid styling,
    dynamic title strings, and multi-color subtitle rendering.
    Expects a dictionary containing: dims, start_date,
    end_date, and tickers.
    """
    dims = plot_params["dims"]
    start_date = plot_params["start_date"]
    end_date = plot_params["end_date"]
    tickers = plot_params.get("tickers", [])

    # Capture the figure reference directly when initializing
    fig = plt.figure(figsize=(dims["width"], dims["height"]))
    ax = plt.gca()

    # DYNAMIC TITLE CALCULATION (Rounds down to nearest full year)
    start_dt = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    num_years = (end_dt - start_dt).days // 365

    # 1. Main Title
    plt.figtext(
        0.5,
        0.93,
        f"{num_years}-{YEAR} {INDEX_TITLE} Growth",
        fontsize=15,
        fontweight=GENERAL_FONT_WEIGHT,
        fontname=GENERAL_FONTNAME,
        ha="center",
    )

    # 2. Adjust margins to create protected dead-zone at the bottom for footer elements
    plt.subplots_adjust(left=0.12, right=0.95, top=0.85, bottom=0.18)

    # 3. Instantiate footer widget referencing our clean separate function definition
    ax.footer = ComponentAssetFooter(
        fig=fig,
        tickers=tickers,
        on_refresh_callback=lambda: refresh_index_chart(
            ax, tickers, start_date, end_date
        ),
    )

    # 4. Trigger the first render loop immediately to generate the initial baseline view frame
    refresh_index_chart(ax, tickers, start_date, end_date)

    return ax
