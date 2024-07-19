import core.domain.common.interfaces.IAsset as ias
import core.domain.engines.AssetEngine as aa
import pandas as pd
import numpy as np


class Swap (ias.IAsset):
    
    def __init__(self, series_name, long_index, short_index, long_price_hist, short_price_hist):
        # --- Properties -----------------------------------------
        self.series_name : str = "Swap - " + series_name
        self.long_index : str = long_index
        self.short_index : str = short_index
        self.long_price_hist : pd.DataFrame = long_price_hist   # columns: Date Price log_ret
        self.short_price_hist : pd.DataFrame = short_price_hist # columns: Date  log_ret_ + short_index
        self.swap_df : pd.DataFrame  = pd.merge(long_price_hist, short_price_hist, on=ias.DATE)
        # --------------------------------------------------------
        
        #Merging data:
        short_log_ret_col_name = "log_ret_" + short_index
        self.swap_df['swap_log_return'] = self.swap_df[ias.LOG_RETURN] - self.swap_df[short_log_ret_col_name]

    def get_asset_name(self) -> str:
        return self.series_name
    
    def get_price(self, target_date):
        return self.long_price_hist[self.long_price_hist[ias.DATE] == target_date][ias.CLOSE_PRICE].iloc[0]

    def get_daily_log_return(self, target_date) -> float:
        return self.swap_df[self.swap_df[ias.DATE] == target_date]['swap_log_return'].iloc[0]

    def get_daily_return(self, target_date):
        log_ret = self.get_daily_log_return(target_date)
        return np.exp(log_ret)

    def get_swap_accum_return(self, since_dt) -> pd.DataFrame:
        df = self.swap_df[self.swap_df[ias.DATE ] >= since_dt]
        return aa.get_accum_return(df, 'swap_log_return')
    
    def get_underlying_asset_accum_return(self, since_dt) -> pd.DataFrame:
        df = self.swap_df[self.swap_df['Date'] >= since_dt]
        return aa.get_accum_return(df, ias.LOG_RETURN)
    
    def get_daily_log_returns(self) -> pd.DataFrame:
        return self.swap_df[[ias.DATE,  'swap_log_return']].rename(columns={"swap_log_return" : ias.LOG_RETURN})
    
    def has_data(self,target_date) -> bool:
        df = self.swap_df[self.swap_df[ias.DATE] < target_date]
        df = df.dropna()
        return (len(df) > 0)


