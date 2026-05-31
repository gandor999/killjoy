import matplotlib.dates as mdates

from constants.constants_theme import DATE_FORMAT, GENERAL_FONT_WEIGHT, GENERAL_FONTNAME


class BlittedCrosshairWithOverlay:
    def __init__(self, ax, pan_state=None):
        self.ax = ax
        self.canvas = ax.figure.canvas
        self.pan_state = pan_state  # Receives the state from the pan tool

        self.horizontal_line = ax.axhline(
            color="gray", linestyle="--", linewidth=0.8, visible=False
        )
        self.vertical_line = ax.axvline(
            color="gray", linestyle="--", linewidth=0.8, visible=False
        )

        # Left-aligned overlay text box in the upper left corner
        self.text_overlay = ax.text(
            0.02,
            0.9,
            "",
            transform=ax.transAxes,
            ha="left",
            va="top",
            fontsize=10,
            fontweight=GENERAL_FONT_WEIGHT,
            fontname=GENERAL_FONTNAME,
            color="#333333",
            bbox=dict(boxstyle="round,pad=0.4", fc="#ffffff", ec="#cccccc", alpha=0.85),
            visible=False,
        )

        self.background = None
        self.canvas.mpl_connect("draw_event", self.on_draw)
        self.canvas.mpl_connect("motion_notify_event", self.on_mouse_move)

    def on_draw(self, event):
        if event.canvas != self.canvas:
            return
        self.horizontal_line.set_visible(False)
        self.vertical_line.set_visible(False)
        self.text_overlay.set_visible(False)
        self.background = self.canvas.copy_from_bbox(self.ax.bbox)

    def on_mouse_move(self, event):
        # If the user is actively dragging to pan, hide the crosshair instantly
        if self.pan_state and self.pan_state.get("is_panning", False):
            self.hide_crosshair()
            return

        if event.inaxes != self.ax or self.background is None:
            self.hide_crosshair()
            return

        self.canvas.restore_region(self.background)
        self.horizontal_line.set_ydata([event.ydata, event.ydata])
        self.vertical_line.set_xdata([event.xdata, event.xdata])

        try:
            date_str = mdates.num2date(event.xdata).strftime(DATE_FORMAT)
        except Exception:
            date_str = f"{event.xdata:.2f}"

        self.text_overlay.set_text(f"Date: {date_str}\nIndex: {event.ydata:.2f}")

        self.horizontal_line.set_visible(True)
        self.vertical_line.set_visible(True)
        self.text_overlay.set_visible(True)

        self.ax.draw_artist(self.horizontal_line)
        self.ax.draw_artist(self.vertical_line)
        self.ax.draw_artist(self.text_overlay)
        self.canvas.blit(self.ax.bbox)

    def hide_crosshair(self):
        if self.horizontal_line.get_visible() and self.background is not None:
            self.horizontal_line.set_visible(False)
            self.vertical_line.set_visible(False)
            self.text_overlay.set_visible(False)
            self.canvas.restore_region(self.background)
            self.canvas.blit(self.ax.bbox)
