from screeninfo import get_monitors


def get_chart_dimensions(width_ratio=0.8, height_ratio=0.6):
    try:
        primary_monitor = get_monitors()[0]
        monitor_width = primary_monitor.width
        monitor_height = primary_monitor.height
        dimensions = {
            "width": (monitor_width * width_ratio) / 100,
            "height": (monitor_height * height_ratio) / 100,
        }
        print(f"Detected screen resolution: {monitor_width}x{monitor_height}")
        return dimensions
    except Exception:
        print("Could not detect screen resolution. Using default fallback sizes.")
        return {"width": 14, "height": 7}
