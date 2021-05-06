from sklearn.neighbors import kneighbors_graph
import plotly.express as px
from sklearn import cluster
from utils import file_manager, portfolio_manager
import pandas as pd

class Plotter():

    def __init__(self, r, pm, selected_resolution, group = None):

        self.r  = r
        self.pm = pm
        
        self.selected_resolution = selected_resolution
        self.fm = file_manager.FileManager(self.selected_resolution)


        if (group == 'portfolio'):

            self.ticker_list = self.get_portfolio_ticker(pm, group)
        
        if (group != 'portfolio') and (group != 'all'):

            self.ticker_list = self.get_watchlist_ticker(pm, group)

        if group == 'all':

            self.ticker_list = list(set(self.get_portfolio_ticker(pm, group) \
                                + self.get_watchlist_ticker(pm, group)))


    def get_portfolio_ticker(self, pm, group):

        if ('portfolio_df' not in pm.__dict__): 
            
            print('Loading portfolio')
            self.portfolio_df = pm.load_portfolio()
            ticker_list = list(self.portfolio_df.index)

        else:
            self.portfolio_df = pm.portfolio_df
            ticker_list = list(self.portfolio_df.index)

        return ticker_list


    def get_watchlist_ticker(self, pm, group):


        if ('watchlist_df' not in pm.__dict__): 
                
            self.watchlist_df = pm.load_watchlists()
            watchlists = list(self.watchlist_df['watchlist'].unique())
            
            if group in watchlists:
                ticker_list = list(self.watchlist_df[self.watchlist_df['watchlist'] == group]['symbol'].unique())

            elif group == 'all':
                ticker_list = list(self.watchlist_df['symbol'].unique())

            else:
                print(f'Unable to identify group. Specified group {group}\nWatchlist {watchlists}')

        else:
            self.watchlist_df = pm.watchlist_df
            ticker_list = list(self.watchlist_df[self.watchlist_df['watchlist'] == group]['symbol'].unique())

        return ticker_list

    def generate_time_heatmap(self, ohcl = 'open_price', n_clusters = 5):
        
        n_neighbors = n_clusters
        
        portfolio_open = self.fm.read_from_disk(self.ticker_list)[ohcl]
        
        portfolio_open_next = portfolio_open.shift(-1)
        portfolio_change = (portfolio_open_next - portfolio_open)/portfolio_open
        
        #n_neighbors = n_clusters = 5
        heat_data = portfolio_change.fillna(0).T
        
        heat_data.columns = heat_data.columns + '_'
        #heat_data = heat_data.sort_index

        knn_graph = kneighbors_graph(heat_data, n_neighbors, include_self=False, p = 1)

        #model = cluster.AgglomerativeClustering(linkage = 'ward', 
        #                                        connectivity = knn_graph,
        #                                        n_clusters = n_clusters)

        model = cluster.SpectralClustering(
                n_clusters=n_clusters, eigen_solver='arpack',
                affinity="nearest_neighbors")

        model.fit(heat_data)

        heat_data['clusters'] = model.labels_
        
        fig = px.imshow(heat_data.sort_values('clusters')[[i for i in heat_data.columns if i != 'clusters']].T,
                        color_continuous_midpoint = 0,
                        zmax = heat_data.values.mean() + (heat_data.values.std() * 0.5),
                       zmin = heat_data.values.mean() - (heat_data.values.std() * 0.5),
                       contrast_rescaling = 'minmax',
                       #color_continuous_scale = 'Viridis',
                       aspect = 'auto')
        fig.update_layout({'title': 'Clusters of Open Close Ratio', 'height': 1000, 'width': 1300})
        
        return fig, heat_data