# Stock Market RSI Analytics App

This Streamlit application is designed to perform analytics based on the Relative Strength Index (RSI) of stocks. Users can enter the ticker symbol of any stock and analyze its RSI trends within a specified date range. The app aims to uncover potential investment strategies by exploring patterns in RSI movements and evaluating the expected returns following different RSI events.

## Features

- User-friendly sidebar to input settings such as ticker symbol, time range, and RSI parameters.
- Options to select RSI period lengths for daily and weekly data, and define the ROI window for potential return analysis.
- Calculation of daily and weekly RSI values and categorization into meaningful RSI events.
- Visual charts and statistics summarizing the RSI data and expected returns.
- Narrative analysis outlining frequent RSI patterns and suggesting possible trading strategies.

## Online Access

No download required! Access the RSI Analytics app directly in your browser at the following URL:

[https://rsi-analytics.streamlit.app/](https://rsi-analytics.streamlit.app/)

## Getting Started

To set up and run the app locally, follow these instructions:

1. Clone the repo to your local environment:
   ```sh
   git clone https://github.com/your-username/stock-rsi-analytics.git
   cd rsi-analytics
   
# Installation and Usage

To set up and run the app locally, follow these instructions:

1. **Install the necessary dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

2. **Run the application using Streamlit:**
    ```sh
    streamlit run app.py
    ```

## Dependencies

- `streamlit`
- `pandas`
- `seaborn`
- `matplotlib`
- Refer to `requirements.txt` for the complete list of required libraries.

## Project Structure

- `app.py` - The main script to launch the Streamlit app.
- `src/` - Contains Python modules with the backend logic.
  - `RSIAnalytics.py` - Handles data processing, RSI computation, and analysis.
- `requirements.txt` - Specifies the Python dependencies for the application.

## Contributions

Feel free to suggest improvements, report issues, or contribute to the codebase. You can do this by creating an issue or pull request on this repository.

## License

This application is available under the MIT License. See the LICENSE file for more details.

## Contact

If you have any questions or need help, feel free to reach out by creating an issue on this repository or contacting [Nate Belete](mailto:natebelete@gmail.com).
