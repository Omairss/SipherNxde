import pandas as pd
import numpy as np
from tqdm.auto import tqdm

class PortfolioManager():

	def __init__(self, r, load = False):

		self.r = r

		if load == True:
			load_portfolio()
			load_watchlists()


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

