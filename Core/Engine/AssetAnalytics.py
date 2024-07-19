import pandas as pd
import numpy as np

def get_accum_return(df : pd.DataFrame, log_return_col: str) -> pd.DataFrame:
        df2 = df.reset_index()
        df2['accum_return_cumsum'] = df2[log_return_col].cumsum()
        df2['accum_return'] = np.exp(df2['accum_return_cumsum'])
        return df2[['Date', 'accum_return']]

def calculate_log_return(df : pd.DataFrame, price_col : str):
        return np.log(df[price_col]) - np.log(df[price_col].shift(1))


def transform_annual_rate_in_daily_rate(df : pd.DataFrame, annual_rate_col: str):
        df2 = df.reset_index()
        return (1 + df2[annual_rate_col])^(1/365) - 1


def transform_annual_rate_in_daily_log_raturn(df : pd.DataFrame, annual_rate_col: str):
        df2 = df.reset_index()
        return np.log((1 + df2[annual_rate_col])**(1/365))