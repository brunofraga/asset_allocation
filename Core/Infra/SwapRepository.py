import pandas as pd
import numpy as np
import Core.Entity.Asset.Swap as es
import Core.Entity.Asset.Interfaces.IAsset as ias
import Core.Entity.Asset.AssetClass as ac
import Core.Engine.AssetAnalytics as aa


# ----------------------------------------------------------------------------------------------------------------
class SwapSetConfig:
    def __init__(self, min_dt, selected_series, asset_class : ac.AssetClass):
        self.min_dt = min_dt
        self.selected_series = selected_series
        self.asset_class : ac.AssetClass = asset_class


# ----------------------------------------------------------------------------------------------------------------


class SwapDao:
    def __init__(self):
        # --- Properties -----------------------------------------
        self.swap_set_configs = {}
        self.etf_df : pd.DataFrame = pd.DataFrame()
        # --------------------------------------------------------

        self.get_etf_data()

        #Equities
        asset_class = ac.AssetClass.EQUITY
        # min_dt = "2011-10-06"
        min_dt = "2013-07-18" 
        selected_series = ['VLUE US Equity', 'SIZE US Equity', 'USMV US Equity', 'MTUM US Equity', 'QUAL US Equity']
        self.swap_set_configs[asset_class] = SwapSetConfig(min_dt, selected_series, asset_class)


        #Credit
        asset_class = ac.AssetClass.CREDIT
        min_dt = "2014-01-01"
        selected_series = ['SLQD US Equity', 'LQD US Equity', 'EMHY US Equity', 'HYGH US Equity']
        self.swap_set_configs[asset_class] = SwapSetConfig(min_dt, selected_series, asset_class)

        #FX or Commodities
        min_dt = "2013-07-17"


        # FX
        asset_class = ac.AssetClass.FX
        selected_series = ['UUP US Equity', 'FXY US Equity', 'FXE US Equity', 'UDN US Equity', 'CEW US Equity']
        self.swap_set_configs[asset_class] = SwapSetConfig(min_dt, selected_series, asset_class)


        #Commodities
        asset_class = ac.AssetClass.COMMODITY
        selected_series = ['UCO US Equity', 'SCO US Equity', 'KOLD US Equity', 'ZSL US Equity', 'GLL US Equity', 'GLD US Equity',
                        'GDX US Equity', 'PDBC US Equity']
        self.swap_set_configs[asset_class] = SwapSetConfig(min_dt, selected_series, asset_class)

    def get_dates(self, asset_class : ac.AssetClass):
        return list(self.etf_df[self.etf_df["Date"] > self.swap_set_configs[asset_class].min_dt]["Date"])


    def get_etf_data(self):
        # ----------------------------------------------------------------------------------------------------------------
        # Carregando Arquivos:

        # reading files:
        self.etf_df = pd.read_csv("_Input/all_data_v2.csv")

        etf_series = list(self.etf_df.columns[1:])
        etf_series.remove("SOFR")
        etf_series.remove("Libor")

        # print(etf_series)
        short_index = "Libor"
        self.etf_df[short_index] = self.etf_df[short_index]/100
        self.etf_df["log_ret_" + short_index] = aa.transform_annual_rate_in_daily_log_raturn(self.etf_df, short_index)

        short_index = "SOFR"
        self.etf_df[short_index] = self.etf_df[short_index]/100
        self.etf_df["log_ret_" + short_index] = aa.transform_annual_rate_in_daily_log_raturn(self.etf_df, short_index)


        mask = pd.isna(self.etf_df["SOFR"])
        self.etf_df.loc[mask,"log_ret_SOFR"] = self.etf_df.loc[mask,"log_ret_Libor"]

        return self.etf_df


        # ----------------------------------------------------------------------------------------------------------------
    
    def get_swap_set(self, asset_class : ac.AssetClass, short_index : str):
        return self.__get_swap_set(self.swap_set_configs[asset_class].selected_series, self.etf_df, short_index)
    
    
    def get_etfs_cumulative_return(self, asset_class : ac.AssetClass, short_index):
        return self.__get_cumulative_return(asset_class, short_index, self.etf_df, False)

    def get_swaps_cumulative_return(self, asset_class : ac.AssetClass, short_index):
        return self.__get_cumulative_return(asset_class, short_index, self.etf_df, True)

    def __get_cumulative_return(self, asset_class : ac.AssetClass, short_index, etf_df, swap_mode : bool):
        swaps_accum_df = pd.DataFrame()
        assets_accum_df = pd.DataFrame()
        equity_swaps = []
        i = 0
        for series_name in self.swap_set_configs[asset_class].selected_series:
            etf_df["log_ret_" + series_name] = aa.calculate_log_return(etf_df, series_name)
            long_price_hist = etf_df[["Date", series_name, "log_ret_"  + series_name]].rename(columns={series_name: ias.CLOSE_PRICE, "log_ret_"  + series_name: ias.LOG_RETURN})
            short_price_hist = etf_df[["Date", "log_ret_" + short_index ]]

            swap = es.Swap(series_name, series_name, short_index, long_price_hist, short_price_hist)
            s_df = swap.get_swap_accum_return(self.swap_set_configs[asset_class].min_dt).rename(columns={"accum_return" : series_name})
            a_df = swap.get_underlying_asset_accum_return(self.swap_set_configs[asset_class].min_dt).rename(columns={"accum_return" : series_name})

            if (i == 0):
                swaps_accum_df = s_df
                assets_accum_df = a_df
            else:
                swaps_accum_df = swaps_accum_df.merge(s_df, on="Date")
                assets_accum_df = assets_accum_df.merge(a_df, on="Date")
            equity_swaps.append(swap)
            i += 1
        
        return swaps_accum_df if swap_mode else assets_accum_df

    
    def __get_swap_set(self, selected_series, etf_df, short_index):
        swap_list = []
        # Initializing Swaps:
        for series_name in selected_series:
            etf_df["log_ret_" + series_name] = aa.calculate_log_return(etf_df, series_name)
            long_price_hist = etf_df[["Date", series_name, "log_ret_"  + series_name]].rename(columns={series_name: ias.CLOSE_PRICE, "log_ret_"  + series_name: "log_ret"})
            short_price_hist = etf_df[["Date", "log_ret_" + short_index ]]

            series_swap = es.Swap(series_name, series_name, short_index, long_price_hist, short_price_hist)
            swap_list.append(series_swap)

        return swap_list

    def get_short_index_cumulative_return(self, target_date, short_index):
        df = self.etf_df[self.etf_df["Date"] >= target_date]
        return aa.get_accum_return(df, "log_ret_" + short_index).rename(columns={"accum_return" : "Cumulative_Return" + short_index})


# ----------------------------------------------------------------------------------------------------------------