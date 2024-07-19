from datetime import date
import pandas as pd
import core.domain.common.interfaces.IAsset as ias


DATE = ias.DATE
ASSET = "Asset"
DAILY_RETURN = "Daily Return"
EXPOSURE_BOP = "Exposure BoP"
EXPOSURE_EOP = "Exposure EoP"
TRADE_EXPOSURE = "Trade Exposure"
TRADE_COST = "Trade Cost"
PNL_DAILY = "PnL - Daily"
PNL_CUMULATIVE = 'PnL'
DAYS_IN_EXPOSURE = 'Days in Exposure'
STRATEGY = "Strategy"
STRATEGY_WEIGHT = "Strategy Weight"

def get_clean_result_df() -> pd.DataFrame:
    return pd.DataFrame(columns=[DATE, ASSET, DAILY_RETURN,
                                 EXPOSURE_BOP, EXPOSURE_EOP, TRADE_EXPOSURE, TRADE_COST, PNL_DAILY,  PNL_CUMULATIVE, DAYS_IN_EXPOSURE])



class TradingResult:
    def __init__(self):
        self.results : pd.DataFrame = get_clean_result_df()
        pass

    def update(self, target_date : date, asset_name, daily_return, exposure_bop, exposure_eop, trade_exposure, trade_cost, pnl_daily, pnl_cumulative, days_exposure):
        new_result_row = pd.DataFrame(data={DATE: [target_date],
                                            ASSET: [asset_name],
                                            DAILY_RETURN: [daily_return], 
                                            EXPOSURE_BOP: [exposure_bop],
                                            EXPOSURE_EOP: [exposure_eop],
                                            TRADE_EXPOSURE: [trade_exposure],
                                            TRADE_COST: [trade_cost],
                                            PNL_DAILY: [pnl_daily],
                                            PNL_CUMULATIVE: [pnl_cumulative],
                                            DAYS_IN_EXPOSURE: [days_exposure]})
        
        self.results = pd.concat([self.results, new_result_row], ignore_index=True)
        return new_result_row
    
    def attach_dataframe(self, other_result : pd.DataFrame):
        self.results = pd.concat([self.results, other_result], ignore_index=True)
        return self
    
    def attach_strategy_result(self, strategy_name : str, strategy_weight : float, other_result : 'TradingResult'):
        other_result.results[STRATEGY] = strategy_name
        other_result.results[STRATEGY_WEIGHT] = strategy_weight
        self.results = pd.concat([self.results, other_result.results], ignore_index=True)
        return self
    
    def to_csv(self, file_path):
        self.results.to_csv(file_path, index=False)

    def attach_value(self, target_dt, col_name, col_value ):
        self.results.loc[self.results[DATE] == target_dt, col_name] = col_value


def union(result : TradingResult, other_result : TradingResult):
    tr = TradingResult()
    tr.results = pd.concat([result.results, other_result.results], ignore_index=True)
    
    return tr



def attach_dataframe(result : TradingResult, other_result : pd.DataFrame):
    tr = TradingResult()
    tr.results = pd.concat([result.results, other_result], ignore_index=True)
    
    return tr
    

