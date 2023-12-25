import yfinance as yf
import pandas as pd
import ta

class RSIAnalytics:
    def __init__(self, ticker_symbol, start_date, end_date):
        self.ticker_symbol = ticker_symbol
        self.start_date = start_date
        self.end_date = end_date

    def download_data(self, interval='1d'):
        """Download stock data using yfinance."""
        try:
            data = yf.download(self.ticker_symbol, start=self.start_date, end=self.end_date, interval=interval)
            if 'Date' not in data.columns:
                data.reset_index(inplace=True)
            data['Date'] = pd.to_datetime(data['Date'])
            data['Year-Week_Number'] = data['Date'].dt.strftime('%Y-%U')
            return data
        except Exception as e:
            print(f"An error occurred: {e}")
            return pd.DataFrame()

    def calculate_rsi(self, data, column='Close', period=14):
        """Calculate RSI and categorize it using the 'ta' library."""
        rsi_indicator = ta.momentum.RSIIndicator(close=data[column], window=period, fillna=False)
        data['RSI'] = rsi_indicator.rsi()
        data['RSI_Category'] = pd.cut(data['RSI'], bins=[-float('inf'), 30, 50, 70, float('inf')],
                                      labels=['<30', '30-50', '50-70', '>70'])
        return data
    
    def calculate_forward_rolling(self, data, column, window=5, min_periods=5, rolling_func='max'):
        """Calculate forward rolling maximum or minimum."""
        reversed_series = data[column][::-1]
        if rolling_func == 'max':
            result = reversed_series.rolling(window=window, min_periods=min_periods).max()
        elif rolling_func == 'min':
            result = reversed_series.rolling(window=window, min_periods=min_periods).min()
        else:
            raise ValueError("Invalid rolling_func. Use 'max' for maximum or 'min' for minimum.")
        data[column + '_Forward_Rolling_' + rolling_func.capitalize()] = result[::-1]
        return data
    
    def calculate_roi(self, data, roi_window=21):
        """Calculate forward rolling maximum and minimum ROI relative to the current price."""
        data = self.calculate_forward_rolling(data, 'High', window=roi_window, min_periods=roi_window, rolling_func='max')
        data = self.calculate_forward_rolling(data, 'Low', window=roi_window, min_periods=roi_window, rolling_func='min')
        data['ROI_Max'] = data['High_Forward_Rolling_Max'] / data['Close'] - 1
        data['ROI_Min'] = data['Low_Forward_Rolling_Min'] / data['Close'] - 1
        return data

    def prepare_data(self, interval, rsi_period, roi_window, key_cols, new_col_names):
        """Prepare final DataFrame with RSI categories and (if interval is '1d') forward rolling ROI."""
        df = self.download_data(interval)
        if df.empty:
            return pd.DataFrame()  # Return an empty DataFrame if the data download failed
        
        df = self.calculate_rsi(df, period=rsi_period)

        # Only calculate ROI if the interval is daily ('1d')
        if (interval == '1d') & (roi_window !=0):
            df = self.calculate_roi(df, roi_window=roi_window)
        
        df.dropna(inplace=True)
        
        # Ensure key columns are available in the DataFrame
        missing_cols = set(key_cols) - set(df.columns)
        if missing_cols:
            print(f"Missing columns in DataFrame: {missing_cols}")
            return pd.DataFrame()
        
        df_final = df[key_cols].copy()
        df_final.columns = new_col_names
        return df_final
    
    
    def compute_summary_stats(self, df_daily, df_weekly, min_count):
        """Compute summary statistics from daily and weekly RSI data."""
        df_merged = df_daily.merge(df_weekly, on='Year-Week_Number', how='left')

        groupby_cols = ['Weekly_RSI_Category', 'Daily_RSI_Category']
        summary_df = df_merged.groupby(groupby_cols).agg({
            'Date': 'count',
            'ROI_Max': 'mean',
            'ROI_Min': 'mean',
        }).reset_index()

        summary_df['ROI_Diff'] = abs(summary_df['ROI_Max']) - abs(summary_df['ROI_Min'])
        filtered_summary_df = summary_df[summary_df['Date'] >= min_count]

        return filtered_summary_df
    
   
    @staticmethod
    def get_inference_data(daily_inference_data, weekly_data):
        """Merge daily and weekly data."""
        df_merged = daily_inference_data.merge(weekly_data, how='left', on='Year-Week_Number')

        # Drop rows with missing data (resulting from the left merge)
        df_inference = df_merged.dropna()
        
        return df_inference.tail(1)