import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import yfinance as yf
import plotly.express as px
import pandas as pd
import talib  # Technical Analysis library
from datetime import datetime

# Initialize the Dash app
app = dash.Dash(__name__)

# App layout
app.layout = html.Div([
    html.Div([
        html.H4("Stock Code:"),
        dcc.Input(id="stock-code-input", value="AAPL", type="text", style={"width": "100%"}),
        dcc.DatePickerRange(
            id="date-picker",
            start_date=datetime(2021, 1, 1),
            end_date=datetime.now().date(),
            display_format="MM/DD/YYYY"
        ),
        dcc.Input(id="forecast-input", placeholder="Days to forecast", type="number"),
        html.Button("Get Stock Data", id="submit-button", n_clicks=0),
        html.Br(),
        html.Br(),
        html.Button("Get Price", id="price-button", n_clicks=0),
        html.Br(),
        html.Br(),
        html.Label("Indicators:"),
        dcc.Dropdown(
            id="indicators-dropdown",
            options=[
                {"label": "On-balance volume (OBV)", "value": "OBV"},
                {"label": "Accumulation/Distribution (A/D) line", "value": "AD"},
                {"label": "Average directional index (ADX)", "value": "ADX"},
                {"label": "Aroon oscillator", "value": "AROON"},
                {"label": "MACD", "value": "MACD"},
                {"label": "RSI", "value": "RSI"},
                {"label": "Stochastic oscillator", "value": "STOCH"}
            ],
            multi=True
        ),
        html.Button("Apply Indicator", id="indicator-button", n_clicks=0),
    ], style={"padding": "20px", "background-color": "#005F5F", "border-radius": "10px", "width": "25%", "float": "left"}),

    html.Div(id="graphs-content", children=[], style={"width": "70%", "float": "right"})
])

# Callback to update stock graph and apply indicators
@app.callback(
    Output("graphs-content", "children"),
    [Input("submit-button", "n_clicks"), Input("price-button", "n_clicks"), Input("indicator-button", "n_clicks")],
    [State("stock-code-input", "value"), State("date-picker", "start_date"), State("date-picker", "end_date"), State("indicators-dropdown", "value")]
)
def update_stock_graph(stock_clicks, price_clicks, indicator_clicks, stock_code, start_date, end_date, indicators):
    ctx = dash.callback_context

    if not ctx.triggered:
        return html.P("Submit a stock code and date range to see the stock data.")

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == "submit-button" or button_id == "price-button":
        try:
            # Ensure the stock code and date inputs are valid
            if not stock_code:
                return html.P("Error: Stock code is missing.")
            if not start_date or not end_date:
                return html.P("Error: Start date or end date is missing.")
            
            # Convert start_date and end_date to proper date format (YYYY-MM-DD)
            start_date = datetime.strptime(start_date.split("T")[0], "%Y-%m-%d").strftime("%Y-%m-%d")
            end_date = datetime.strptime(end_date.split("T")[0], "%Y-%m-%d").strftime("%Y-%m-%d")
            
            # Fetch stock data
            df = yf.download(stock_code, start=start_date, end=end_date)
            
            # Debugging
            print(df.head())  # Check if data is being fetched
            
            # Check if data is empty
            if df.empty:
                return html.P(f"No data available for {stock_code} from {start_date} to {end_date}.")
            
            # Create plotly graph
            fig = px.line(df, x=df.index, y=['Open', 'Close'], title=f"{stock_code} Stock Prices")
            return dcc.Graph(figure=fig)
        
        except Exception as e:
            print(f"Error: {e}")  # Debugging output
            return html.P(f"An error occurred: {str(e)}")
    
    elif button_id == "indicator-button":
        try:
            # Ensure the stock code and date inputs are valid
            if not stock_code:
                return html.P("Error: Stock code is missing.")
            if not start_date or not end_date:
                return html.P("Error: Start date or end date is missing.")
            
            # Convert start_date and end_date to proper date format (YYYY-MM-DD)
            start_date = datetime.strptime(start_date.split("T")[0], "%Y-%m-%d").strftime("%Y-%m-%d")
            end_date = datetime.strptime(end_date.split("T")[0], "%Y-%m-%d").strftime("%Y-%m-%d")
            
            # Fetch stock data
            df = yf.download(stock_code, start=start_date, end=end_date)
            
            # Check if data is empty
            if df.empty:
                return html.P(f"No data available for {stock_code} from {start_date} to {end_date}.")
            
            # Apply selected indicators
            indicator_figs = []
            if indicators:
                for indicator in indicators:
                    if indicator == "OBV":
                        df['OBV'] = talib.OBV(df['Close'], df['Volume'])
                        fig = px.line(df, x=df.index, y='OBV', title=f"{stock_code} On-Balance Volume (OBV)")
                        indicator_figs.append(dcc.Graph(figure=fig))
                    elif indicator == "AD":
                        df['AD'] = talib.AD(df['High'], df['Low'], df['Close'], df['Volume'])
                        fig = px.line(df, x=df.index, y='AD', title=f"{stock_code} Accumulation/Distribution (A/D) Line")
                        indicator_figs.append(dcc.Graph(figure=fig))
                    elif indicator == "ADX":
                        df['ADX'] = talib.ADX(df['High'], df['Low'], df['Close'])
                        fig = px.line(df, x=df.index, y='ADX', title=f"{stock_code} Average Directional Index (ADX)")
                        indicator_figs.append(dcc.Graph(figure=fig))
                    elif indicator == "AROON":
                        df['Aroon_Up'], df['Aroon_Down'] = talib.AROON(df['High'], df['Low'])
                        fig = px.line(df, x=df.index, y=['Aroon_Up', 'Aroon_Down'], title=f"{stock_code} Aroon Oscillator")
                        indicator_figs.append(dcc.Graph(figure=fig))
                    elif indicator == "MACD":
                        df['MACD'], df['MACD_Signal'], _ = talib.MACD(df['Close'])
                        fig = px.line(df, x=df.index, y=['MACD', 'MACD_Signal'], title=f"{stock_code} MACD")
                        indicator_figs.append(dcc.Graph(figure=fig))
                    elif indicator == "RSI":
                        df['RSI'] = talib.RSI(df['Close'])
                        fig = px.line(df, x=df.index, y='RSI', title=f"{stock_code} Relative Strength Index (RSI)")
                        indicator_figs.append(dcc.Graph(figure=fig))
                    elif indicator == "STOCH":
                        df['SlowK'], df['SlowD'] = talib.STOCH(df['High'], df['Low'], df['Close'])
                        fig = px.line(df, x=df.index, y=['SlowK', 'SlowD'], title=f"{stock_code} Stochastic Oscillator")
                        indicator_figs.append(dcc.Graph(figure=fig))
            
            return indicator_figs
        
        except Exception as e:
            print(f"Error: {e}")  # Debugging output
            return html.P(f"An error occurred: {str(e)}")

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
