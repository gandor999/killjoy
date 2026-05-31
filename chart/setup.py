import matplotlib.pyplot as plt


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
        0.125,
        0.88,
        "",  # 0.125 aligns perfectly with the left edge of the chart
        transform=plt.gcf().transFigure,  # <--- Change transAxes to transFigure
        fontsize=11,
        fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.5", fc="black", alpha=0.75),
        color="white",
        verticalalignment="bottom",  # Aligns upward from the baseline coordinate
        zorder=5,
    )

    def on_mouse_move(event):
        if event.inaxes == ax and event.xdata is not None and event.ydata is not None:
            x_mouse, y_mouse = event.xdata, event.ydata

            try:
                mouse_dt = plt.matplotlib.dates.num2date(x_mouse)
                date_str = mouse_dt.strftime("%d/%m/%y %I:%M:%S %p")
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


def setup_status_bar_formatter(ax):
    """
    Overrides the default Matplotlib bottom toolbar coordinates
    to display a clean date string in DD/MM/YY hh:mm:ss AM/PM format.
    """

    def format_coord(x, y):
        try:
            dt_obj = plt.matplotlib.dates.num2date(x)
            date_str = dt_obj.strftime("%d/%m/%y %I:%M:%S %p")
            return f"x = {date_str}, y = {y:.2f}"
        except (ValueError, OverflowError):
            return f"x = {x:.2f}, y = {y:.2f}"

    ax.format_coord = format_coord


def setup_scroll_zoom(ax):
    """
    Enables dynamic zooming in and out using the mouse scroll wheel.
    """

    def zoom_on_scroll(event):
        if event.inaxes == ax:
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

            plt.gcf().canvas.draw_idle()

    # Bind the wheel scrolling listener to the Matplotlib window framework
    plt.gcf().canvas.mpl_connect("scroll_event", zoom_on_scroll)


def setup_right_click_pan(ax):
    """
    Enables 100% smooth, pixel-perfect panning by dragging with the
    right mouse button. Eliminates all jitter.
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
            # Store raw screen pixel locations
            pan_state["start_pixel_x"] = event.x
            pan_state["start_pixel_y"] = event.y
            pan_state["start_xlim"] = ax.get_xlim()
            pan_state["start_ylim"] = ax.get_ylim()

    def on_motion(event):
        if pan_state["is_panning"] and event.inaxes == ax:
            # Get the exact distance moved in raw pixels
            pixel_dx = event.x - pan_state["start_pixel_x"]
            pixel_dy = event.y - pan_state["start_pixel_y"]

            # Convert that pixel distance into exact chart scale equivalents
            # This stops the scaling values from fighting the cursor
            trans = ax.transData.inverted()
            start_data_coord = trans.transform(
                (pan_state["start_pixel_x"], pan_state["start_pixel_y"])
            )
            current_data_coord = trans.transform((event.x, event.y))

            dx = current_data_coord[0] - start_data_coord[0]
            dy = current_data_coord[1] - start_data_coord[1]

            # Apply the stable shifts
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
