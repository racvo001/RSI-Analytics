import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

from src.RSIAnalytics import RSIAnalytics

def sidebar_setup():
    st.sidebar.header('RSI Analytics Settings')
    ticker_symbol = st.sidebar.text_input("Enter the ticker symbol", value='AAPL')
    start_date = st.sidebar.date_input("Start date", pd.to_datetime('2000-01-01'))
    end_date = st.sidebar.date_input("End date", pd.to_datetime('today'))
    rsi_period_daily = st.sidebar.slider("Select Daily RSI period", min_value=1, max_value=30, value=14)
    rsi_period_weekly = st.sidebar.slider("Select Weekly RSI period", min_value=1, max_value=30, value=7)
    roi_window = st.sidebar.slider("Select ROI window (days)", min_value=0, max_value=100, value=21)
    min_count = st.sidebar.slider("Minimum count for summary statistics", min_value=1, max_value=100, value=30)
    return ticker_symbol, start_date, end_date, rsi_period_daily, rsi_period_weekly, roi_window, min_count

def perform_analysis(rsi_analytics, rsi_period_daily, rsi_period_weekly, roi_window, min_count):
    daily_data = rsi_analytics.prepare_data(
        interval='1d',
        rsi_period=rsi_period_daily,
        roi_window=roi_window,
        key_cols=['Year-Week_Number', 'Date', 'RSI', 'RSI_Category', 'ROI_Max', 'ROI_Min'],
        new_col_names=['Year-Week_Number', 'Date', 'RSI_Value', 'Daily_RSI_Category', 'ROI_Max', 'ROI_Min']
    )
    
    weekly_data = rsi_analytics.prepare_data(
        interval='1wk',
        rsi_period=rsi_period_weekly,
        roi_window=0,  # roi_window is ignored for weekly data
        key_cols=['Year-Week_Number', 'RSI', 'RSI_Category'],
        new_col_names=['Year-Week_Number', 'RSI_Value', 'Weekly_RSI_Category']
    )

    rsi_summary = rsi_analytics.compute_summary_stats(daily_data, weekly_data, min_count)
    rsi_summary['Label'] = rsi_summary.apply(lambda row: f"Weekly: {row['Weekly_RSI_Category']} & Daily: {row['Daily_RSI_Category']}", axis=1)
    rsi_summary['ROI_Diff'] = rsi_summary['ROI_Max'].abs() - rsi_summary['ROI_Min'].abs() 
    
    return daily_data, weekly_data, rsi_summary


def visualize_rsi_summary(rsi_summary):
    sns.set(style="whitegrid")
    plt.figure(figsize=(15, 6))

    min_bars = sns.barplot(x='Label', y='ROI_Min', data=rsi_summary, color='lightpink', label='ROI Min')
    max_bars = sns.barplot(x='Label', y='ROI_Max', data=rsi_summary, color='lightgreen', label='ROI Max')
    diff_bars = sns.barplot(x='Label', y='ROI_Diff', data=rsi_summary, color='lightgray', label='ROI Diff')

    annotate_bars(max_bars)
    annotate_bars(min_bars)
    annotate_bars(diff_bars)

    plt.xticks(rotation=45, ha='right')
    plt.xlabel("RSI Event")
    plt.ylabel("ROI")
    plt.title("Expected ROI Conditioned on RSI Event")
    plt.legend()
  
    format_axis_as_percent(plt.gca())

    st.pyplot(plt)
    plt.clf()

def format_axis_as_percent(ax):
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"{y:.1%}"))

def annotate_bars(bars):
    for bar in bars.patches:
        bars.annotate(format(bar.get_height(), '.1%'),
                      (bar.get_x() + bar.get_width() / 2, bar.get_height()), 
                      ha='center', va='bottom',
                      xytext=(0, 3), textcoords='offset points')

def perform_inference(rsi_analytics, rsi_period_daily, rsi_period_weekly):
    daily_inference_data = rsi_analytics.prepare_data(
        interval='1d',
        rsi_period=rsi_period_daily,
        roi_window=0,  # No ROI needed for inference
        key_cols=['Year-Week_Number', 'Date', 'RSI_Category'],
        new_col_names=['Year-Week_Number', 'Date', 'Daily_RSI_Category']
    )
    weekly_inference_data = rsi_analytics.prepare_data(
        interval='1wk',
        rsi_period=rsi_period_weekly,
        roi_window=0,  # No ROI needed for weekly inference
        key_cols=['Year-Week_Number', 'RSI_Category'],
        new_col_names=['Year-Week_Number', 'Weekly_RSI_Category']
    )
    inference_data = RSIAnalytics.get_inference_data(daily_inference_data, weekly_inference_data)
    return inference_data

def display_rsi_summary_table(rsi_summary):
    # Select only the desired columns
    rsi_summary_table = rsi_summary[['Weekly_RSI_Category', 'Daily_RSI_Category', 'Date', 'ROI_Max',  'ROI_Min','ROI_Diff']]
    
    # Apply formatting to the ROI columns to show them as percentages
    rsi_summary_styler = rsi_summary_table.style.format({
        'ROI_Max': "{:.2%}",
        'ROI_Min': "{:.2%}",
        'ROI_Diff': "{:.2%}",
        'Date': "{:,}"  # Add commas as thousands separators
    }).background_gradient(subset=['ROI_Max',  'ROI_Min','ROI_Diff'], cmap='Oranges') \
      .applymap(lambda v: 'color: darkred;', subset=['ROI_Max',  'ROI_Min','ROI_Diff']) \
      .set_properties(**{'color': 'black', 'background-color': 'linen'}) \
      .set_table_styles([{
          'selector': 'th',
          'props': [('background-color', 'peachpuff'), ('color', 'black')]
      }])

    # Display the styled DataFrame
    st.dataframe(rsi_summary_styler)



def create_label_date_barplot(rsi_summary):
    # Filter the DataFrame to get only the 'Label' and 'Date' columns
    label_date_df = rsi_summary[['Label', 'Date']]
    
    # Create a barplot using Seaborn
    plt.figure(figsize=(12, 4))
    barplot = sns.barplot(data=label_date_df, x='Label', y='Date', ci=None, palette='YlOrBr')

    # Annotating the barplot with the data values
    for p in barplot.patches:
        barplot.annotate(format(p.get_height(), '.0f'), 
                         (p.get_x() + p.get_width() / 2., p.get_height()), 
                         ha = 'center', va = 'center', 
                         xytext = (0, 10), 
                         textcoords = 'offset points')

    # Adding labels and title to the plot
    plt.xlabel('RSI Event')
    plt.ylabel('Count')
    plt.title('Count of RSI Events')
    plt.xticks(rotation=45, ha='right')  # Rotate the x labels for better readability

    # Show the plot within the Streamlit app
    st.pyplot(plt)
    
    # Clear the figure after rendering to avoid duplication when rerunning
    plt.clf()

def create_narrative(rsi_summary_table):
    # Calculate the ROI difference
    rsi_summary_table['ROI_Diff'] = rsi_summary_table['ROI_Max'].abs() - rsi_summary_table['ROI_Min'].abs()

    # Sort and identify the most common event
    most_common_event = rsi_summary_table.sort_values(by='Date', ascending=False).iloc[0]
    most_common_narrative = (
        f"The most frequent RSI event occurs when the Weekly RSI is '{most_common_event['Weekly_RSI_Category']}' "
        f"and the Daily RSI is '{most_common_event['Daily_RSI_Category']}', with a total occurrence of "
        f"{most_common_event['Date']} times.\n"
    )

    # Identify the events with the highest and lowest ROI
    highest_roi_event = rsi_summary_table.loc[rsi_summary_table['ROI_Max'].idxmax()]
    lowest_roi_event = rsi_summary_table.loc[rsi_summary_table['ROI_Min'].idxmin()]
    
    # Identify the event with the highest ROI difference
    highest_roi_diff_event = rsi_summary_table.loc[rsi_summary_table['ROI_Diff'].idxmax()]

    # Build the ROI narratives
    highest_roi_narrative = (
        f"The event best for long trades occurs with a Weekly RSI of '{highest_roi_event['Weekly_RSI_Category']}' "
        f"and a Daily RSI of '{highest_roi_event['Daily_RSI_Category']}', offering a return of "
        f"{highest_roi_event['ROI_Max']:.1%}.\n"
    )
    
    lowest_roi_narrative = (
        f"Conversely, the event best for short trades occurs with a Weekly RSI of '{lowest_roi_event['Weekly_RSI_Category']}' "
        f"and a Daily RSI of '{lowest_roi_event['Daily_RSI_Category']}', resulting in a return of "
        f"{lowest_roi_event['ROI_Min']:.1%}.\n"
    )
    
    highest_roi_diff_narrative = (
        f"Interestingly, the greatest spread between the highest and lowest returns "
        f"takes place when the Weekly RSI is '{highest_roi_diff_event['Weekly_RSI_Category']}' and the Daily "
        f"RSI is '{highest_roi_diff_event['Daily_RSI_Category']}'. This event has a net return of "
        f"{highest_roi_diff_event['ROI_Diff']:.1%}, indicating potential for low risk and high returns for longs.\n"
    )

    # Combine the narratives
    full_narrative = most_common_narrative + highest_roi_narrative + lowest_roi_narrative + highest_roi_diff_narrative
    
    st.write("###### Most Common")
    st.write(most_common_narrative)

    st.write("###### Best Long Pattern")
    st.write(highest_roi_narrative)

    st.write("###### Best Short Pattern")
    st.write(lowest_roi_narrative)

    st.write("###### Low Risk High ROI Long Pattern")
    st.write(highest_roi_diff_narrative)

    return full_narrative

def create_settings_narrative(ticker_symbol, start_date, end_date, rsi_period_daily, rsi_period_weekly, roi_window, min_count):
    # Building separate strings for each segment of the narrative
    introduction = (f"RSI Analytics Report for {ticker_symbol} from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}."
    )
    
    rsi_details = (
        f"The analysis uses a Daily RSI period of {rsi_period_daily} and a Weekly RSI period of {rsi_period_weekly}. "
        f"The ROI window is set at {roi_window} days to evaluate potential returns following RSI events. "
        f"A minimum of {min_count} events are required for an RSI event to be included in the summary statistics."
    )
    
    objective = (
        "The objective is to identify patterns in RSI trends and highlight "
        "investment opportunities for enhanced returns in the stock's performance."
    )
    
    # Writing each segment to the Streamlit app
    st.write(introduction)
    st.write(rsi_details)
    st.write(objective)


def display_results(rsi_analytics, daily_data, weekly_data, rsi_summary, rsi_period_daily, rsi_period_weekly):

    st.subheader("RSI Frequency")
    create_label_date_barplot(rsi_summary)

    st.subheader("Summary")
    create_narrative(rsi_summary)

    st.subheader("Expected Returns")
    visualize_rsi_summary(rsi_summary)

    st.subheader("Summary Statistics")
    display_rsi_summary_table(rsi_summary)

    # st.subheader("Inference Data")
    # inference_data = perform_inference(rsi_analytics, rsi_period_daily, rsi_period_weekly)
    # st.dataframe(inference_data)

def main():
    st.title("Stock Market RSI Analytics App")
    ticker_symbol, start_date, end_date, rsi_period_daily, rsi_period_weekly, roi_window, min_count = sidebar_setup()

    rsi_analytics = RSIAnalytics(ticker_symbol, start_date, end_date)
    
    if st.sidebar.button('Run Analysis'):
        with st.spinner("Downloading data and computing analytics..."):
            create_settings_narrative(ticker_symbol, start_date, end_date, rsi_period_daily, rsi_period_weekly, roi_window, min_count)
            daily_data, weekly_data, rsi_summary = perform_analysis(rsi_analytics, rsi_period_daily, rsi_period_weekly, roi_window, min_count)
            display_results(rsi_analytics, daily_data, weekly_data, rsi_summary, rsi_period_daily, rsi_period_weekly)


if __name__ == '__main__':
    main()
