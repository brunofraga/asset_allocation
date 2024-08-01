import core.application.strategies.base.TradingStrategy as ts
import core.domain.engines.AssetEngine as aa
import core.domain.models.trading.TradingResult as tr
import core.domain.models.asset.GeneralAsset as ga
import core.domain.models.asset.PortfolioAnalytics as p

from tqdm import tqdm
from typing import List, Dict
from datetime import date
import pandas as pd
import numpy as np

class TradingBook:

    def __init__(self, trading_book_name : str, strategies : List[ts.TradingStrategy], target_dates : List[date], target_vol : float, max_leverage=1):
        # --- Properties -----------------------------------------
        self.trading_book_name : str = trading_book_name
        self.strategies : Dict[str, ts.TradingStrategy] = {}
        self.strategies_ready_state : Dict[str, bool] = {}
        self.trading_results : tr.TradingResult = tr.TradingResult()
        self.target_dates = target_dates
        self.trading_positions = {}
        self.strategy_weights : Dict[str, float] = {}
        self.max_leverage = max_leverage

        self.target_vol : float = target_vol
        self.days_to_realocate : int = 90
        self.days_range_to_calc_vol : int = 90
        self.days_since_resizing : int = self.days_to_realocate
        self.all_strategies_ready : bool = False
        self.book_vol = 0
        # --------------------------------------------------------
        
        self.strategy_numb = len(strategies)
        # initiating trading positions and assets dictionary:
        for strategy in strategies:
            self.strategies[strategy.strategy_name] = strategy
            self.strategy_weights[strategy.strategy_name] = 1/self.strategy_numb

        self.__set_fixed_weights()

    
    # For a manual approach
    def set_strategy_weights(self, strategy_weights):
        self.strategy_weights = strategy_weights


    def get_consolidated_result(self) -> pd.DataFrame:
        r_df = self.trading_results.results[[tr.DATE,tr.PNL_CUMULATIVE, tr.STRATEGY]]
        pivot = r_df.pivot_table(index=tr.DATE, columns=tr.STRATEGY, values=[tr.PNL_CUMULATIVE, tr.PNL_DAILY] ,  aggfunc=np.sum)
        return pivot


    # Running trading book backtest:
    def run(self):
        self.days_running_all_strategies = 0
        
        
        print("")
        for target_date in tqdm(self.target_dates, f'Backtesting {self.trading_book_name.upper()}'):
        #for target_date in self.target_dates:
            self.__update_strategy_weights_by_vol_targeting(target_date)

            for strategy_name in self.strategies:
                strat = self.strategies[strategy_name]
                if (self.strategies_ready_state[strategy_name]):
                    strat_weight = self.strategy_weights[strategy_name]
                    trading_order = strat.get_trading_order(target_date)
                    daily_strategy_result = strat.update(target_date, trading_order, strat_weight)
                    self.trading_results.attach_strategy_result(strategy_name, strat_weight, daily_strategy_result)
            
            if (self.all_strategies_ready):
                self.days_running_all_strategies += 1
                
            if(not(self.trading_results.is_empty())):
                self.trading_results.attach_value(target_date, "Book Vol", self.book_vol)
                self.trading_results.attach_value(target_date, "all_strategies_ready", self.all_strategies_ready)

        return self.trading_results
    
    def __calculate_weights_with_volt_targeting(self, target_date):
        # is ok to do it?
        if (self.days_running_all_strategies > self.days_range_to_calc_vol):
            is_resizing_day = self.days_since_resizing >= self.days_to_realocate
            if (is_resizing_day):
                # pivoting:
                pivot = self.trading_results.results.pivot_table(index=tr.DATE, columns=tr.STRATEGY, values=tr.PNL_DAILY,  aggfunc=np.sum)
                pivot = pivot.dropna()

                self.days_since_resizing = 0
                asset_list = []
                pivot[ga.GeneralAsset.DATE] = pivot.index
                for strategy_name in self.strategies:
                    self.strategy_weights[strategy_name] = 0
                    #unpivoting:
                    if not(self.strategies[strategy_name].is_stopped):
                        asset_df =  pivot[[strategy_name]].unstack().reset_index(name=strategy_name)[[ga.GeneralAsset.DATE, strategy_name]].tail(self.days_range_to_calc_vol)
                        asset_df[ga.GeneralAsset.LOG_RETURN] = asset_df[strategy_name] - asset_df[strategy_name].mean() # pnl pode ser negativo, e ai nao podemos calcular o log retorno dele
                        gen_asset = ga.GeneralAsset(strategy_name,  asset_df)
                        asset_list.append(gen_asset)

                if (len(asset_list) == 0 ):
                    self.book_vol = 0
                else:
                    strat_portfolio = p.Portfolio("strategies", asset_list)
                    running_strategy_weights = strat_portfolio.get_vol_targeting_weights(target_date, self.days_range_to_calc_vol, self.target_vol, self.max_leverage)
                    for strategy_name, value in running_strategy_weights.items():
                        self.strategy_weights[strategy_name] = value



                    self.book_vol = strat_portfolio.calc_portfolio_volatility_with_weights(target_date, self.days_range_to_calc_vol, running_strategy_weights)


            else:
                self.days_since_resizing +=1


    def __set_fixed_weights(self):
        self.fixed_strategy_weights = {}
        for strategy_name in self.strategies:
            desired_weight = 0

            if ("Equity" in strategy_name):
                desired_weight = 0.4
            elif ("Credit" in strategy_name):
                desired_weight = 0.3
            elif ("Comdty" in strategy_name):
                desired_weight = 0.2
            elif ("FX" in strategy_name):
                desired_weight = 0.1

            self.fixed_strategy_weights[strategy_name] = desired_weight

    def __update_strategy_weights_by_vol_targeting(self, target_date):
        if (not(self.all_strategies_ready)):
            self.numb_strats_ready = 0
            for strategy_name in self.strategies:
                self.strategies_ready_state[strategy_name] = self.strategies[strategy_name].is_ready(target_date)
                self.numb_strats_ready += 1 if self.strategies_ready_state[strategy_name] else 0 

            for strategy_name in self.strategies:
                self.strategy_weights[strategy_name] = 1/self.numb_strats_ready if self.strategies_ready_state[strategy_name] else 0 
            
            if (self.numb_strats_ready == self.strategy_numb):
                self.all_strategies_ready = True
                
        
        else:
            # self.__calculate_weights_with_volt_targeting(target_date)
            
            if (len(self.strategies) == 4):
                self.strategy_weights = self.fixed_strategy_weights


            






