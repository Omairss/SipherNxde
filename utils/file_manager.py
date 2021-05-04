import pandas as pd
import os
from tqdm.auto import tqdm

class FileManager():

    def __init__(self, selected_resolution_key):

        self.ochl = ['open_price', 'close_price', 'high_price', 'low_price']
        self.resolutions = {
                            'daily_5year': {'directory': '../data/stock_data/daily_5year',
                                            'params':['day', '5year']},
                            '5min_weekly':{'directory': '../data/stock_data/5min_weekly',
                                           'params':['5minute', 'week']}
                            }

        self.selected_resolution = self.resolutions[selected_resolution_key]

        print('Initialized')



    def get_data(self, r, ticker):        

        stock_history_2 = r.stocks.get_stock_historicals([ticker],
                                                         interval=self.selected_resolution['params'][0],
                                                         span=self.selected_resolution['params'][1],
                                                         bounds='regular',
                                                         info=None)

        #print(stock_history_2)
            
        stock_history = pd.DataFrame(stock_history_2)
        stock_history['begins_at'] = stock_history['begins_at'] + '_'
        stock_history = stock_history.set_index('begins_at')
        
        #print(stock_history)

        for i in self.ochl:
            stock_history[i] = stock_history[i].astype(float)
            
        stock_history = stock_history.sort_index()
        return stock_history


    def write_to_disk(self,r,tickers):

        #TODO: Change to append instead of write

        all_data = []

        if type(tickers) == 'str':
            tickers = [tickers]
            

        for ticker in tqdm(tickers, desc = 'Writing Files..'):
            
            data = self.get_data(r,ticker)
            data.to_csv(os.path.join(self.selected_resolution['directory'], f'{ticker}.csv'))
            all_data.append(data)
        
        return all_data
        

    def read_from_disk(self,tickers):
        
        all_data = []

        if type(tickers) == 'str':
            tickers = [tickers]
            
        for ticker in tqdm(tickers, desc = 'Reading Files..'):
            all_data.append(pd.read_csv(os.path.join(self.selected_resolution['directory'], f'{ticker}.csv')).set_index('begins_at'))

        all_data = pd.concat(all_data).pivot(columns = 'symbol')

        return all_data
        