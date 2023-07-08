from flask import Flask, render_template, request
import pandas as pd
import yfinance as yf
from patterns import candlestick_patterns
import talib, os, csv
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route('/')
def index():
    return {
        "code": "error",
        "message": "Please use the /api endpoint"
    }

@app.route('/api')
def api():
    pattern = request.args.get('pattern', None)
    stocks = {}

    with open('datasets/nifty100.csv') as f:
        for row in csv.reader(f):
            stocks[row[0]] = {'company': row[1]}

    if pattern:
        datafiles = os.listdir('datasets/daily')
        for filename in datafiles:
            df = pd.read_csv(f'datasets/daily/{filename}')
            pattern_function = getattr(talib, pattern)
            symbol = filename.split('.')[0]
            try:
                result = pattern_function(df['Open'], df['High'], df['Low'], df['Close'])
                last = result.tail(1).values[0]
                if last > 0:
                    stocks[symbol][pattern] = 'bullish'
                elif last < 0:
                    stocks[symbol][pattern] = 'bearish'
                else:
                    del stocks[symbol]
            except:
                pass
    return stocks

@app.route('/snapshot')
def snapshot():
    index = request.args.get('index', 'nifty100')
    key = request.args.get('key', 'company')
    if key == os.environ.get('KEY'):
        with open(f'data/indexes/{index}.csv') as f:
            companies = f.read().splitlines()
            for company in companies:
                symbol = company.split(',')[0]+'.NS'
                data = yf.download(symbol, period='1y', interval='1d')
                data.to_csv(f'data/daily/{symbol[:-3]}.csv')
        return {
            'code': 'success',
            'message': f'Downloaded {index} companies data'
        }
    else:
        return {
            'code': 'error',
            'message': 'Invalid key'
        }
    
if __name__ == '__main__':
    app.run(debug=True, port=5001)
