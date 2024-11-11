from sklearn.svm import SVR
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_squared_error, mean_absolute_error
import yfinance as yf
import pandas as pd
import plotly.express as px

# Function to train the SVR model
def train_model(stock_code, forecast_days):
    df = yf.download(stock_code, period='60d')
    X = df[['Open', 'High', 'Low', 'Volume']].values
    y = df['Close'].values
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1)
    
    # GridSearchCV to tune the model
    svr = SVR(kernel='rbf')
    grid_search = GridSearchCV(svr, {'C': [1, 10], 'epsilon': [0.01, 0.1], 'gamma': [0.001, 0.01]}, cv=5)
    grid_search.fit(X_train, y_train)
    
    # Predict and evaluate model
    predictions = grid_search.predict(X_test)
    mse = mean_squared_error(y_test, predictions)
    mae = mean_absolute_error(y_test, predictions)
    
    # Forecast future stock prices
    future_index = pd.date_range(df.index[-1], periods=forecast_days+1, freq='D')[1:]
    future_prices = grid_search.predict(X[-forecast_days:])
    
    # Create forecast plot
    forecast_df = pd.DataFrame({'Date': future_index, 'Predicted Close': future_prices})
    fig = px.line(forecast_df, x='Date', y='Predicted Close', title=f"{stock_code} Stock Price Forecast for {forecast_days} Days")
    
    return mse, mae, fig
