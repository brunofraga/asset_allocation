import core.domain.common.interfaces.IAsset as ias
import core.domain.engines.AssetEngine as aa
import pandas as pd
import numpy as np


class GeneralAsset (ias.IAsset):
    
    def __init__(self, series_name, asset_hist : pd.DataFrame):
        # --- Properties -----------------------------------------
        self.series_name : str = series_name
        self.asset_df : pd.DataFrame = asset_hist   # columns: Date Price log_ret
        # --------------------------------------------------------
        

    def get_asset_name(self) -> str:
        return self.series_name
    
    def get_price(self, target_date):
        return self.asset_df[self.asset_df[ias.DATE] == target_date][ias.CLOSE_PRICE].iloc[0]

    def get_daily_log_return(self, target_date) -> float:
        return self.asset_df[self.asset_df[ias.DATE] == target_date][ias.LOG_RETURN].iloc[0]

    def get_daily_return(self, target_date):
        log_ret = self.get_daily_log_return(target_date)
        return np.exp(log_ret)

    def get_swap_accum_return(self, since_dt) -> pd.DataFrame:
        df = self.asset_df[self.asset_df[ias.DATE ] >= since_dt]
        return aa.get_accum_return(df, ias.LOG_RETURN)
    
    def get_asset_accum_return(self, since_dt) -> pd.DataFrame:
        df = self.asset_df[self.asset_df[ias.DATE] >= since_dt]
        return aa.get_accum_return(df, ias.LOG_RETURN)
    
    def get_daily_log_returns(self) -> pd.DataFrame:
        return self.asset_df[[ias.DATE,  ias.LOG_RETURN]]
    
    def has_data(self,target_date) -> bool:
        df = self.asset_df[self.asset_df[ias.DATE] < target_date]
        df = df.dropna()
        return (len(df) > 0)


