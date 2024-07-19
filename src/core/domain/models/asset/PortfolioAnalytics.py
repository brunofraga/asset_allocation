from typing import List, Dict
import pandas as pd
import core.domain.common.interfaces.IAsset as ias
import numpy as np

# Cada Portfolio tem uma lista de assets para olhar: dicionario <assets>
# Contempla a tabela de log-retornos de cada asset: <log_returns>
#   - Usado para calculos gerais do portfolio (como vol, covariania, etc)
#   - As colunas são Date + asset_names (log retornos das assets)

class Portfolio (ias.IAsset):

    # Constructor
    def __init__(self, portfolio_name : str, assets : List[ias.IAsset]):
        
        # --- Properties -----------------------------------------
        self.portfolio_name : str = portfolio_name
        self.assets : Dict[str, ias.IAsset] = {}
        self.asset_names : List[str] = []
        self.log_returns : pd.DataFrame = pd.DataFrame()
        self.current_asset_weights  = {}
        self.asset_weights : pd.DataFrame = pd.DataFrame()
        # --------------------------------------------------------

        i = 0
        for asset in assets:
            asset_name = asset.get_asset_name()
            self.asset_names.append(asset_name)

            self.current_asset_weights[asset_name] = 0
            self.assets[asset_name] = asset
            a_df = asset.get_daily_log_returns().rename(columns={ias.LOG_RETURN : asset_name})

            if (i == 0):
                self.log_returns = a_df
            else:
                self.log_returns = self.log_returns.merge(a_df, on=ias.DATE)
            i += 1

    # --------------------------------------------------------
    # iAsset Implementation
    # --------------------------------------------------------
    def get_asset_name(self ) -> str:
        return self.portfolio_name

    def get_price(self, target_date : str) -> float:
        return 0

    def get_daily_return(self, target_date) -> float:
        raise ValueError('Portfolio:get_daily_return was not implememented!')
        df = self.log_returns[self.log_returns[ias.DATE] == target_date][self.asset_names]
        # log_ret =  self.current_asset_weights @ df
        return df

    def get_vol_daily_return(self, target_date) -> float:
        """Get return given a target date."""
        pass

    def get_daily_log_returns(self) -> pd.DataFrame:
        """Get DataFrame with Date and LogReurn """
        pass



    # --------------------------------------------------------
    # Portfolio fuctions
    # --------------------------------------------------------
    def has_enough_data(self,target_date, last_n_points):
        df = self.log_returns[self.log_returns[ias.DATE] < target_date]
        df = df.dropna()
        return (len(df) > last_n_points)

    def get_covariance_matrix(self, target_date, last_n_points):
        df = self.log_returns[self.log_returns[ias.DATE] < target_date].tail(last_n_points)
        covariance_matrix = df[self.asset_names].cov()
        return covariance_matrix
    
    def get_assets_volatility(self, target_date, last_n_points):
        df = self.log_returns[self.log_returns[ias.DATE] < target_date].tail(last_n_points)
        std = df[self.asset_names].std()
        return std
    
    def get_portfolio_volatility(self, target_date, last_n_points):
        covariance = self.get_covariance_matrix(target_date, last_n_points)

        # calculando vol do portfolio
        portfolio_var =  self.current_asset_weights @ covariance @ self.current_asset_weights.T
        portfolio_vol = np.sqrt(portfolio_var)
        
        return portfolio_vol
    
    def calc_portfolio_volatility_with_weights(self, target_date, last_n_points, current_asset_weights):
        covariance = self.get_covariance_matrix(target_date, last_n_points)

        # calculando vol do portfolio
        portfolio_var =  current_asset_weights @ covariance @ current_asset_weights.T
        portfolio_vol = np.sqrt(portfolio_var)
        
        return portfolio_vol

    def get_vol_targeting_weights(self, target_date, last_n_points, target_vol, max_leverage):
        # calculando covariancia e vol
        covariance = self.get_covariance_matrix(target_date, last_n_points)
        vols = self.get_assets_volatility(target_date, last_n_points)
        
        # calculando pesos iniciais (dado o std):
        inverse_vol = 1/vols
        total_inverse_vol = sum(inverse_vol)
        intial_w = inverse_vol / total_inverse_vol

        # calculando vol do portfolio
        portfolio_var =  intial_w @ covariance @ intial_w.T
        portfolio_vol = np.sqrt(portfolio_var)
        
        # calculando fator de ajuste:
        factor = min(target_vol/portfolio_vol, max_leverage)

        # calculando novos pesos:
        final_w = intial_w * factor
        
        return final_w
        
    


