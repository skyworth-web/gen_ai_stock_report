import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import io

def generate_stock_images(ticker_symbol="AAPL"):
    # Fetch stock data
    stock = yf.Ticker(ticker_symbol)

    # Get historical stock prices (daily, weekly, monthly)
    stock_data_daily = stock.history(period="3mo", interval="1d")  # 3 months daily
    stock_data_weekly = stock.history(period="6mo", interval="1wk")  # 6 months weekly
    stock_data_monthly = stock.history(period="1y", interval="1mo")  # 1 year monthly

    # Get earnings per quarter
    earnings_data = stock.get_earnings_history()['epsActual']

    # Dictionary to store image buffers
    image_buffers = {}

    # Function to save plots in memory
    def save_plot_to_memory(fig, name):
        img_buffer = io.BytesIO()
        fig.savefig(img_buffer, format='png', bbox_inches='tight')
        img_buffer.seek(0)
        image_buffers[name] = img_buffer
        plt.close(fig)  # Close the figure to free memory

    # Plot 1: Stock Price (Daily)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(stock_data_daily.index, stock_data_daily["Close"], '-o', label="Daily Price")
    ax.set_title(f"{ticker_symbol} Stock Price (Daily)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price (USD)")
    ax.grid()
    ax.legend()
    save_plot_to_memory(fig, "daily")

    # Plot 2: Stock Price (Weekly)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(stock_data_weekly.index, stock_data_weekly["Close"], '-o', label="Weekly Price")
    ax.set_title(f"{ticker_symbol} Stock Price (Weekly)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price (USD)")
    ax.grid()
    ax.legend()
    save_plot_to_memory(fig, "weekly")

    # Plot 3: Stock Price (Monthly)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(stock_data_monthly.index, stock_data_monthly["Close"], '-o', label="Monthly Price")
    ax.set_title(f"{ticker_symbol} Stock Price (Monthly)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price (USD)")
    ax.grid()
    ax.legend()
    save_plot_to_memory(fig, "monthly")

    # Plot 4: Earnings Per Quarter
    fig, ax = plt.subplots(figsize=(8, 5))
    earnings_data.plot(ax=ax, color='blue')
    ax.set_title(f"{ticker_symbol} Earnings Per Quarter")
    ax.set_xlabel("Quarter")
    ax.set_ylabel("Net Income (USD)")
    ax.grid()
    save_plot_to_memory(fig, "earnings")
    plt.show()
    return image_buffers  # Returns dictionary of images