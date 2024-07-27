import core.application.strategies.base.TradingStrategy as ts
import core.domain.common.interfaces.IAsset as ias
import core.domain.models.trading.TradingOrder as tord

from datetime import date
from typing import List

STRATEGY_TP_NAME = "Vol. Targeting"

class VolatilityTargetingStrategy (ts.TradingStrategy):

    def __init__(self, strategy_name : str, assets : List[ias.IAsset], target_vol,  max_leverage=3, general_stop_function_active : bool = True):
        ts.TradingStrategy.__init__(self, strategy_name + " | " + STRATEGY_TP_NAME, assets, general_stop_function_active)
        # --- Properties -----------------------------------------
        self.target_vol : float = target_vol
        self.days_to_realocate : int = 90
        self.days_range_to_calc_vol : int = 90
        self.days_since_trade : int = self.days_to_realocate
        self.max_leverage= max_leverage
        # --------------------------------------------------------
    
    def is_ready(self, target_date : date) -> tord.TradingOrder:
        return self.portfolio.has_enough_data(target_date, self.days_range_to_calc_vol)


    def get_trading_order(self, target_date : date) -> tord.TradingOrder:
        trading_order = tord.TradingOrder(self.portfolio)

        trading_day = ((self.days_since_trade >= self.days_to_realocate)) | self.resume_trading_signal
        if (trading_day):
            if (self.portfolio.has_enough_data(target_date, self.days_range_to_calc_vol)):
                weights = self.portfolio.get_vol_targeting_weights(target_date, self.days_range_to_calc_vol, self.target_vol, self.max_leverage)

                for asset_name in self.hypothetical_trading_positions:
                    hypo_tp = self.hypothetical_trading_positions[asset_name]
                    trade = weights[asset_name] - hypo_tp.exposure_eop
                    trading_order.add_trade(asset_name, trade)
        
        return trading_order