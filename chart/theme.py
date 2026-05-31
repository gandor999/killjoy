from constants.constants_theme import NEGATIVE_COLOR, POSITIVE_COLOR


def get_roi_theme(ytd_roi):
    if ytd_roi >= 0:
        return {
            "text": f"YTD ROI: {ytd_roi:+.2f}%",
            "color": POSITIVE_COLOR,
        }  # Light Green
    else:
        return {
            "text": f"YTD ROI: {ytd_roi:+.2f}%",
            "color": NEGATIVE_COLOR,
        }  # Light Red
