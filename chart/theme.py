def get_roi_theme(ytd_roi):
    if ytd_roi >= 0:
        return {"text": f"YTD ROI: {ytd_roi:+.2f}%", "color": "#45EF45"}  # Light Green
    else:
        return {"text": f"YTD ROI: {ytd_roi:+.2f}%", "color": "#EE5555"}  # Light Red
