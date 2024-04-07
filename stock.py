import yfinance as yf
import os
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
import psycopg2
from pymongo import MongoClient
import tkinter.messagebox as tkMessageBox
import pandas as pd
from scipy.stats import pearsonr, spearmanr, kendalltau
from customtkinter import *
import quantstats as qs
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sklearn.linear_model import LogisticRegression
from lynch_val import StockAnalyzer

class StockApp(CTk):
    def __init__(self):
        super().__init__()
        self.geometry("1200x600")
        self.stock_frame = StockFrame(master=self,fg_color='#343a40',border_color='#A49E9E', border_width=3)
        self.stock_frame.pack(expand=True)
        self.stock_frame.place(x=5,y=5)
        self.options_frame = OptionsFrame(master=self,fg_color='#343a40',border_color='#A49E9E', border_width=3)
        self.options_frame.pack(expand=True)
        self.options_frame.place(x=5,y=110)
        self.lynch_val = LynchFrame(master=self,fg_color='#343a40',border_color='#A49E9E', border_width=3)
        self.lynch_val.pack(expand=True)
        self.lynch_val.place(x=340,y=110)
        self._set_appearance_mode("Dark")

class LynchFrame(CTkFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.create_widgets()

    def create_widgets(self):
        self.label_ticker = CTkLabel(self, text_color="white", text="Enter Yahoo Finance Ticker:")
        self.label_ticker.grid(row=1, column=1, padx=20, pady=10)
        self.entry_ticker = CTkEntry(self)
        self.entry_ticker.grid(row=1, column=2, padx=10, pady=10)
        self.button_lynch = CTkButton(self, text="Lynch Value", command=self.calculate_lynch_value)
        self.button_lynch.grid(row=2, column=2, padx=10, pady=10)

    def calculate_lynch_value(self):
        ticker = self.entry_ticker.get().upper()
        try:
            stock_analyzer = StockAnalyzer(ticker)
            earnings_estimate = stock_analyzer.fetch_earnings_estimate()
            current_price = stock_analyzer.fetch_current_price()
            forward_pe = stock_analyzer.calculate_forward_pe(current_price, earnings_estimate)
            print(f"Forward PE Ratio: {forward_pe}")
        except Exception as e:
            tkMessageBox.showerror("Error", f"Failed to calculate Lynch value: {str(e)}")

class OptionsFrame(CTkFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.create_widgets()   

    def create_widgets(self):
        self.button_predictions = CTkButton(self, text="Predictions", command=self.master.stock_frame.prediction_model)
        self.button_predictions.grid(row=5, column=2)
        self.button_plot = CTkButton(self, text="Show plot", command=self.master.stock_frame.display_plot)
        self.button_plot.grid(row=4, column=2, padx=10, pady=10)
        self.button_generate = CTkButton(self, text="Generate Report", command=self.master.stock_frame.generate_report)
        self.button_generate.grid(row=3, column=1, padx=10, pady=10)
        self.button_pg = CTkButton(self, text="Parse Data to PG", command=self.master.stock_frame.parse_data_pg)
        self.button_pg.grid(row=4, column=1, padx=10, pady=10)
        self.button_mongo = CTkButton(self, text="Parse Data to Mongo", command=self.master.stock_frame.parse_data_mongo)
        self.button_mongo.grid(row=5, column=1, padx=10, pady=10)
        self.button_data_correctness = CTkButton(self, text="Correctness", command=self.master.stock_frame.data_correctness)
        self.button_data_correctness.grid(row=3, column=2, padx=10, pady=10)
        

class StockFrame(CTkFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.create_widgets()
    
    def create_widgets(self):
        self.label_ticker = CTkLabel(self, text_color="white", text="Enter Yahoo Finance Ticker:")
        self.label_ticker.grid(row=1, column=1, padx=20, pady=10)
        self.label_date = CTkLabel(self, text_color="white", text="Insert Date:")
        self.label_date.grid(row=2, column=1, padx=20, pady=10)
        self.entry_ticker = CTkEntry(self)
        self.entry_ticker.grid(row=1, column=2, padx=10, pady=10)
        self.entry_second_ticker = CTkEntry(self)
        self.entry_second_ticker.grid(row=1, column=3, padx=10, pady=10)
        self.entry_date = CTkEntry(self)
        self.entry_date.grid(row=2, column=2, padx=10, pady=10)
        self.entry_correlation = CTkComboBox(self, values=["Pearson", "Spearman", "Tau-Kendall"])
        self.entry_correlation.grid(row=2, column=3, padx=10, pady=10)

    def add_ticker_to_history(self, ticker, date):
        self.ticker_history.append((ticker, date))


    def data_correctness(self):
        ticker = self.entry_ticker.get().upper()
        ticker_2 = self.entry_second_ticker.get().upper()
        start_date = self.entry_date.get()
        if not ticker or not ticker_2:
            tkMessageBox.showerror("Error", "Please enter a ticker symbol.")
            return

        try:
            yf.download(ticker, start=start_date, end=datetime.today().strftime('%Y-%m-%d'))
            yf.download(ticker_2, start=start_date, end=datetime.today().strftime('%Y-%m-%d'))
            tkMessageBox.showinfo("Correct", f"Correct ticker: {str(ticker)} and {str(ticker_2)}")
            self.add_ticker_to_history(ticker, start_date)
            self.add_ticker_to_history(ticker_2, start_date)
        except Exception as e:
            tkMessageBox.showerror("Error", f"Failed to generate report: {str(e)}")
    
        
    def display_plot(self):
        correlation = self.entry_correlation.get()
        ticker = self.entry_ticker.get().upper()
        ticker_2 = self.entry_second_ticker.get().upper()
        start_date = self.entry_date.get()
        try:
            data = yf.download(ticker, start=f"{start_date}", end=datetime.today().strftime('%Y-%m-%d'))
            data_2 = yf.download(ticker_2, start=f"{start_date}", end=datetime.today().strftime('%Y-%m-%d'))

            combined_data = pd.concat([data['Close'], data_2['Close']], axis=1).dropna()
            combined_data.columns = [ticker, ticker_2]

            for asset, asset_data in zip([ticker, ticker_2], [data, data_2]):
                daily_returns = (asset_data['Close'] - asset_data['Close'][0]) / asset_data['Close'][0]
                combined_data[f'{asset}_Returns'] = daily_returns
            if correlation == "Pearson":
                correlation_coefficient = pearsonr(combined_data[f'{ticker}_Returns'], combined_data[f'{ticker_2}_Returns'])[0]
            elif correlation == "Spearman":
                correlation_coefficient = spearmanr(combined_data[f'{ticker}_Returns'], combined_data[f'{ticker_2}_Returns'])[0]
            else:
                correlation_coefficient = kendalltau(combined_data[f'{ticker}_Returns'], combined_data[f'{ticker_2}_Returns'])[0]
            combined_data = combined_data.drop([f'{ticker}', f'{ticker_2}'], axis=1)

            plt.figure(figsize=(5, 4), dpi=100)
            plt.gcf().set_facecolor('none')
            sns.set_theme(style='darkgrid')
            sns.set_style(style="dark")
            sns.lineplot(data=combined_data, dashes=False)
            plt.title(f'{ticker} and {ticker_2} Close Price/n {correlation} correlation: {correlation_coefficient:.2f}')
            plt.xticks(rotation=45)
            plt.tight_layout()

            canvas = FigureCanvasTkAgg(plt.gcf(), master=self.master)
            canvas.draw()
            canvas.get_tk_widget().place(x=600,y=20)
            
        except Exception as e:
            tkMessageBox.showerror("Error", f"Failed to display plot: {str(e)}")

    def generate_report(self):
        ticker = self.entry_ticker.get().upper()
        ticker_2 = self.entry_second_ticker.get().upper()
        start_date = self.entry_date.get()
        try:
            data = yf.download(ticker, start=f"{start_date}", end=datetime.today().strftime('%Y-%m-%d'))
            data_2 = yf.download(ticker_2, start=f"{start_date}", end=datetime.today().strftime('%Y-%m-%d'))
            output_path = os.path.join(os.path.expanduser("~"), "Desktop", "Report", f"{ticker}_report.html")
            output_path = os.path.join(os.path.expanduser("~"), "Desktop", "Report", f"{ticker_2}_report.html")
            qs.reports.html(data, output=output_path, title=f"{ticker} Report")
            qs.reports.html(data_2, output=output_path, title=f"{ticker_2} Report")
            tkMessageBox.showinfo("Success", f"Report generated successfully for {ticker} and {ticker_2}.")
        except Exception as e:
            tkMessageBox.showerror("Error", f"Failed to generate report: {str(e)}")

    def save_to_database_pg(self, date, ticker, close):
        try:
            connection = psycopg2.connect(
                dbname="stockersi",
                user="postgres",
                password="postgres",
                host="localhost",
                port="5432"
            )
            cursor = connection.cursor()
            cursor.execute("INSERT INTO stockersi.stock_output (date, ticker, close) VALUES (%s, %s, %s)",
                           (date, ticker, close))
            connection.commit()
        except Exception as e:
            tkMessageBox.showerror("Error", f"Failed to save data to the database: {str(e)}")
        finally:
            if connection:
                connection.close()

    def save_to_database_mongo(self, date, ticker, close):
        try:
            connection = MongoClient("localhost", 27017)
            db = connection.stock
            collection = db.stockers
            data = {"date": date, "ticker": ticker, "close": close}
            collection.insert_one(data)
        except Exception as e:
            tkMessageBox.showerror("Error", f"Failed to save data to the database: {str(e)}")
        finally:
            if connection:
                connection.close()

    def parse_data_pg(self):
        ticker = self.entry_ticker.get().upper()
        start_date = self.entry_date.get()
        data = yf.download(ticker, start=f"{start_date}", end=datetime.today().strftime('%Y-%m-%d'))
        for index, row in data.iterrows():
            self.save_to_database_pg(index, ticker, row['Close'])

    def parse_data_mongo(self):
        ticker = self.entry_ticker.get().upper()
        start_date = self.entry_date.get()
        data = yf.download(ticker, start=f"{start_date}", end=datetime.today().strftime('%Y-%m-%d'))
        for index, row in data.iterrows():
            self.save_to_database_mongo(index, ticker, row['Close'])

    def prediction_model(self):
        ticker = self.entry_ticker.get().upper()
        ticker_2 = self.entry_second_ticker.get().upper()
        start_date = self.entry_date.get()
        try:
            data = yf.download(ticker, start=f"{start_date}", end=datetime.today().strftime('%Y-%m-%d'))
            data_2 = yf.download(ticker_2, start=f"{start_date}", end=datetime.today().strftime('%Y-%m-%d'))

            combined_data = pd.concat([data['Close'], data_2['Close']], axis=1)
            combined_data.columns = [ticker, ticker_2]

            for asset, asset_data in zip([ticker, ticker_2], [data, data_2]):
                daily_returns = (asset_data['Close'] - asset_data['Close'][0]) / asset_data['Close'][0]
                combined_data[f'{asset}_Returns'] = daily_returns

            combined_data.dropna(inplace=True)

            X = combined_data[[f'{ticker}_Returns', f'{ticker_2}_Returns']]
            y = combined_data.index
            X_train, X_test = X[:-5], X[-5:]  # Last 5 days for testing
            y_train, y_test = y[:-5], y[-5:]
            logmodel = LogisticRegression()
            logmodel.fit(X_train, y_train)

            predictions = logmodel.predict(y_test)
            print("Predicted closing prices for the next 5 days:")
            print(predictions)
        except Exception as e:
            tkMessageBox.showerror("Error", f"Failed to predict: {str(e)}")

if __name__ == "__main__":
    app = StockApp()
    app.mainloop()
