import pandas as pd
import numpy as np
from tqdm.auto import tqdm

class PortfolioManager():

	def __init__(self, r, load = False):

		self.r = r

		if load == True:
			self.load_portfolio()
			self.load_watchlists()


	def load_portfolio(self):

		portfolio = self.r.account.build_holdings()
		self.portfolio_df = pd.DataFrame(portfolio).T

		return self.portfolio_df

	def load_watchlists(self):

		watchlist = self.r.account.get_all_watchlists()
		watchlist_df = pd.DataFrame(watchlist).T
		watchlists = [i['display_name'] for i in watchlist['results']]

		all_watchlists = []

		for watchlist_name in tqdm(watchlists):

		    watchlist = self.r.account.get_watchlist_by_name(watchlist_name)
		    _watchlist_df = pd.DataFrame.from_records(watchlist['results'])
		    _watchlist_df['watchlist'] = watchlist_name
		    
		    all_watchlists.append(_watchlist_df)
		   
		self.all_watchlists = pd.concat(all_watchlists)

		return self.all_watchlists


	def create_name_dict(self):

		self.name_dict = {}
		self.name_dict.update(self.all_watchlists[['symbol', 'name']].set_index('symbol').to_dict()['name'])
		self.name_dict.update(self.portfolio_df[['name']].to_dict()['name'])
