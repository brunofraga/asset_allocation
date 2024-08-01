import core.application.strategies.base.TradingStrategy as ts
import core.domain.common.interfaces.IAsset as ias
import core.domain.models.trading.TradingResult as tr
import core.domain.models.trading.TradingOrder as tord
import core.domain.models.asset.PortfolioAnalytics as p

from datetime import date
from typing import List
import math
import pandas as pd
import numpy as np

DAYS_IN_MONTH = 21
STRATEGY_TP_NAME = "Trend-Following"


class TrendFollowingStrategy (ts.TradingStrategy):

    def __init__(self, strategy_name : str, assets : List[ias.IAsset], target_vol, months_to_lag, months_to_hold, max_leverage, general_stop_function_active : bool = True):
        ts.TradingStrategy.__init__(self, strategy_name + " | " + STRATEGY_TP_NAME, assets, target_vol, general_stop_function_active)
        # --- Properties -----------------------------------------
        self.lag_period : float = months_to_lag * DAYS_IN_MONTH #months to days
        self.holding_period : float = months_to_hold * DAYS_IN_MONTH #months to days

        self.max_leverage : float = max_leverage
        self.days_to_realocate : int = 90
        self.days_range_to_calc_vol : int = 90
        self.days_since_trade : int = self.holding_period 
        # --------------------------------------------------------
    
    def is_ready(self, target_date : date) -> tord.TradingOrder:
        return self.portfolio.has_enough_data(target_date, self.lag_period)


    def get_trading_order(self, target_date : date) -> tord.TradingOrder:
        trading_order = tord.TradingOrder(self.portfolio)
        trading_day = (self.days_since_trade >= self.holding_period) | self.resume_trading_signal

        if (trading_day):

            self.__predict_next_return(target_date)

        
            if (self.portfolio.has_enough_data(target_date, self.days_range_to_calc_vol)):

                # Obtendo os novos pesos alvo de acordo com vol target:
                weights = self.portfolio.get_vol_targeting_weights(target_date, self.days_range_to_calc_vol, self.target_vol,self.max_leverage, self.allocation_sign)

                # Obtendo total gross exposure para calcular os pesos atuais:
                total_gross_exposure = sum([np.abs(self.hypothetical_trading_positions[asset_name].exposure_eop) for asset_name in self.hypothetical_trading_positions])
                
                # O trade sera peso*gross. Se o gross ==0, entao multiplicaremos por 1
                trade_mult  = 1.0


                for asset_name in self.hypothetical_trading_positions:
                    hypo_tp = self.hypothetical_trading_positions[asset_name]

                    current_weight = 0 if (total_gross_exposure == 0) else hypo_tp.exposure_eop/total_gross_exposure
                    desired_w = weights[asset_name] 

                    weight_delta = desired_w - current_weight
                    trade = weight_delta * trade_mult

                    if (abs(weight_delta) >= 0.01):
                        trading_order.add_trade(asset_name, trade)
                    else:
                        trading_order.add_trade(asset_name, 0)
        
        return trading_order
    

    def __predict_next_return(self, target_date : date) -> float:
        self.long_portfolio_assets = []
        self.short_portfolio_assets = []
        self.allocation_sign = {}
        for asset_name in self.portfolio.assets:
            s = self.portfolio.assets[asset_name]
            logrets = s.get_daily_log_returns()
            logrets = logrets[logrets[ias.DATE] < target_date].tail(self.lag_period).reset_index(drop=True)

            # calculating 'monthly' log retuns by grouping every [DAYS_IN_MONTH] days
            month_logrets = logrets.groupby(np.arange(len(logrets.index))// DAYS_IN_MONTH).sum()

            # Getting the sign of the lagged return
            lagged_return_sign = math.copysign(1, month_logrets[s.LOG_RETURN].iloc[0])
            self.allocation_sign[asset_name] = lagged_return_sign

            if (lagged_return_sign > 0):
                self.long_portfolio_assets.append(s)
            else:
                self.short_portfolio_assets.append(s)

        
        self.long_portfolio = p.Portfolio(self.strategy_name + ": Long", self.long_portfolio_assets)
        self.short_portfolio = p.Portfolio(self.strategy_name + ": Short", self.short_portfolio_assets)

        return 0
        