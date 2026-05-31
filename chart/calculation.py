import datetime

def calculate_ytd_roi(index_series):
    current_year = datetime.datetime.now().year
    ytd_start_str = f"{current_year}-01-01"

    current_year_data = index_series[index_series.index >= ytd_start_str]

    if not current_year_data.empty:
        ytd_start_value = current_year_data.iloc[0]
        current_value = current_year_data.iloc[-1]
        return ((current_value - ytd_start_value) / ytd_start_value) * 100

    return 0.00