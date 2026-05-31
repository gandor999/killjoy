import matplotlib.pyplot as plt

from chart.classes.BlittedCrosshairWithOverlay import BlittedCrosshairWithOverlay
from constants.constants_theme import DATE_FORMAT, GENERAL_FONT_WEIGHT


def setup_crosshair_tool(ax):
    """
    Creates and attaches an interactive crosshair and data box
    tracking system that directly tracks the mouse coordinates.
    """
    ax.crosshair = BlittedCrosshairWithOverlay(ax)


def setup_status_bar_formatter(ax):
    """
    Overrides the default Matplotlib bottom toolbar coordinates
    to display a clean date string in DD/MM/YY hh:mm:ss AM/PM format.
    """

    def format_coord(x, y):
        try:
            dt_obj = plt.matplotlib.dates.num2date(x)
            date_str = dt_obj.strftime(DATE_FORMAT)
            return f"x = {date_str}, y = {y:.2f}"
        except (ValueError, OverflowError):
            return f"x = {x:.2f}, y = {y:.2f}"

    ax.format_coord = format_coord


def setup_scroll_zoom(ax):
    """
    Enables dynamic zooming in and out using the mouse scroll wheel.
    Hides the blitted crosshair during updates to prevent clipping ghosts.
    """

    def zoom_on_scroll(event):
        if event.inaxes == ax:
            # 1. HIDE THE CROSSHAIR INSTANTLY BEFORE RESIZING
            # This wipes the overlay and lines off the old background canvas cache
            if hasattr(ax, "crosshair"):
                ax.crosshair.hide_crosshair()

            # Check zoom direction (up or down)
            base_scale = 1.2 if event.button == "down" else 0.8

            # Get current axis viewport boundaries
            cur_xlim = ax.get_xlim()
            cur_ylim = ax.get_ylim()

            x_mouse = event.xdata
            y_mouse = event.ydata

            # Calculate new range scale steps relative to cursor position
            new_width = (cur_xlim[1] - cur_xlim[0]) * base_scale
            new_height = (cur_ylim[1] - cur_ylim[0]) * base_scale

            rel_x = (cur_xlim[1] - x_mouse) / (cur_xlim[1] - cur_xlim[0])
            rel_y = (cur_ylim[1] - y_mouse) / (cur_ylim[1] - cur_ylim[0])

            # Set the new locked axis limits dynamically
            ax.set_xlim(
                [x_mouse - new_width * (1 - rel_x), x_mouse + new_width * rel_x]
            )
            ax.set_ylim(
                [y_mouse - new_height * (1 - rel_y), y_mouse + new_height * rel_y]
            )

            # Redraw window frame (this fires the crosshair's on_draw event,
            # updating its internal background cache to the newly zoomed view)
            plt.gcf().canvas.draw_idle()

    # Bind the wheel scrolling listener to the Matplotlib window framework
    plt.gcf().canvas.mpl_connect("scroll_event", zoom_on_scroll)


def setup_right_click_pan(ax):
    """
    Enables 100% smooth, pixel-perfect panning by dragging with the
    right mouse button. Eliminates all jitter. Returns the state dict.
    """
    pan_state = {
        "is_panning": False,
        "start_pixel_x": None,
        "start_pixel_y": None,
        "start_xlim": None,
        "start_ylim": None,
    }

    def on_press(event):
        if event.button == 3 and event.inaxes == ax:
            pan_state["is_panning"] = True
            pan_state["start_pixel_x"] = event.x
            pan_state["start_pixel_y"] = event.y
            pan_state["start_xlim"] = ax.get_xlim()
            pan_state["start_ylim"] = ax.get_ylim()

    def on_motion(event):
        if pan_state["is_panning"] and event.inaxes == ax:
            pixel_dx = event.x - pan_state["start_pixel_x"]
            pixel_dy = event.y - pan_state["start_pixel_y"]

            trans = ax.transData.inverted()
            start_data_coord = trans.transform(
                (pan_state["start_pixel_x"], pan_state["start_pixel_y"])
            )
            current_data_coord = trans.transform((event.x, event.y))

            dx = current_data_coord[0] - start_data_coord[0]
            dy = current_data_coord[1] - start_data_coord[1]

            new_xlim = [val - dx for val in pan_state["start_xlim"]]
            new_ylim = [val - dy for val in pan_state["start_ylim"]]

            ax.set_xlim(new_xlim)
            ax.set_ylim(new_ylim)
            plt.gcf().canvas.draw_idle()

    def on_release(event):
        if event.button == 3:
            pan_state["is_panning"] = False

    plt.gcf().canvas.mpl_connect("button_press_event", on_press)
    plt.gcf().canvas.mpl_connect("motion_notify_event", on_motion)
    plt.gcf().canvas.mpl_connect("button_release_event", on_release)

    return pan_state  # <--- CRITICAL: Pass the state dictionary out of the function


def setup_interactive_tools(ax):
    """
    Initializes both tracking crosshairs and right-click panning,
    sharing state so they cleanly toggle each other off when active.
    """
    # 1. Create a single master state dictionary
    shared_pan_state = {
        "is_panning": False,
        "start_pixel_x": None,
        "start_pixel_y": None,
        "start_xlim": None,
        "start_ylim": None,
    }

    # 2. Hook up right-click panning using the shared state
    setup_right_click_pan(ax, shared_pan_state)

    # 3. Hook up crosshairs, letting it watch the pan state directly
    ax.crosshair = BlittedCrosshairWithOverlay(ax, pan_state=shared_pan_state)
