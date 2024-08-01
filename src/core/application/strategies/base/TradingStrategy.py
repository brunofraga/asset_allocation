from typing import List, Dict
from datetime import date
import pandas as pd

import core.application.trading.TradingPosition as etp

import core.domain.common.interfaces.IAsset as ias
import core.domain.models.trading.TradingResult as tr
import core.domain.models.asset.PortfolioAnalytics as pan
import core.domain.models.trading.TradingOrder as tord
import numpy as np

# Cada estrategia contempla um Portfolio (<portfolio>), que carrega a lista de assets e consegue calcular sua vol., etc
# Para cada uma dessas assets, existe uma posicao de trading atual (trading position), listadas pelo dicionario trading_positions
# A estratégia também carrega o trading result

class TradingStrategy:
    
    # Constructor
    def __init__(self, strategy_name : str, assets : List[ias.IAsset], target_vol, stop_loss_limit : float = 0.2):
        # Properties ---------------------------------------------
        self.strategy_name : str = strategy_name
        self.trading_positions : Dict[str, etp.TradingPosistion] = {}
        self.hypothetical_trading_positions : Dict[str, etp.TradingPosistion] = {}
        self.strategy_result : tr.TradingResult = tr.TradingResult()
        self.portfolio : pan.Portfolio = pan.Portfolio("Portfolio: " + strategy_name, assets)
        self.portfolio_asset_names : List[str] = self.portfolio.asset_names
        self.strategy_vol: float = 0
        self.days_running : int = 0
        self.is_stopped = False
        self.is_loss_high = False
        self.is_vol_ok = True
        self.strat_pivot = pd.DataFrame()
        self.DAYS_ON_STOPLOSS = 42
        self.resume_trading_signal = False
        self.is_vol_high = False
        self.general_stop_function_active = (stop_loss_limit > 0)
        self.stop_loss_limit = -stop_loss_limit
        self.stop_trading_sign = False
        self.target_vol : float = target_vol
        # --------------------------------------------------------
        

        # initiating trading positions and assets dictionary:
        for asset in assets:
            asset_name = asset.get_asset_name()
            self.trading_positions[asset_name] = etp.TradingPosistion(asset)
            self.hypothetical_trading_positions[asset_name] = etp.TradingPosistion(asset)


    def update(self, target_dt : date, trading_order : tord.TradingOrder, trading_strategy_weight : float)  -> tr.TradingResult:
        self.strategy_daily_result = tr.TradingResult()

        self.set_strat_pivot()
        self.set_numb_of_vols_stds()
        self.is_vol_high = (self.number_of_vols_stds > 1.65) #& (self.get_loss_from_last_max() < -0.2)
        if (self.general_stop_function_active):
            self.stop_trading_sign = False
            self.resume_trading_signal = False

            self.check_stop_signs()
            # if (self.is_vol_high & (not(self.is_loss_high)) ):
            #     self.is_vol_ok = self.check_vol_ok()
            #     if (self.is_vol_ok):
            #         self.is_vol_high = False 
            #         self.resume_trading_signal = True
            # elif(self.is_loss_high):
            if(self.is_loss_high):
                self.days_to_resume_trading -= 1
                if (self.days_to_resume_trading == 0):
                    self.is_loss_high = False
                    self.resume_trading_signal = True
        
        # atualizando cada uma das trading_positions:
        if (self.is_loss_high):
            #stoping:
            for asset_name in self.trading_positions:
                tp = self.trading_positions[asset_name]
                hypo_tp = self.hypothetical_trading_positions[asset_name]
                trd_order = - hypo_tp.exposure_eop if self.stop_trading_sign or abs(hypo_tp.exposure_eop)>0.001  else 0

                # Atualizando posicao (real e hipotetica):
                # self.__update_position(hypo_tp, target_dt, trd_order, 1)
                # tp_result = self.__update_position(tp, target_dt, trd_order, trading_strategy_weight)

                self.__end_position(hypo_tp, target_dt, trd_order, 1)
                tp_result = self.__end_position(tp, target_dt, trd_order, trading_strategy_weight)

                
                
                # saving results:
                self.strategy_daily_result.attach_dataframe(tp_result)

            self.is_stopped = True
        
        
        elif (self.is_vol_ok):
            self.is_stopped = False
            for asset_name in self.trading_positions:
                tp = self.trading_positions[asset_name]
                hypo_tp = self.hypothetical_trading_positions[asset_name]
                trd_order = trading_order[asset_name]
                
                if (tp.asset.has_data(target_dt)):
                    # Atualizando posicao (real e hipotetica):
                    self.__update_position(hypo_tp, target_dt, trd_order, 1)
                    tp_result = self.__update_position(tp, target_dt, trd_order, trading_strategy_weight)

                    # saving results:
                    self.strategy_daily_result.attach_dataframe(tp_result)
                
        
        
        
        # --------
        self.strategy_vol = self.portfolio.get_portfolio_volatility(target_dt, 90)
        self.strategy_daily_result.results["Strategy Vol."] = self.strategy_vol
        self.strategy_daily_result.results["stop_trading_sign"] = self.stop_trading_sign
                
        #print("Daily Results:")
        #print(self.strategy_daily_result.results)

        self.strategy_result = tr.union(self.strategy_result, self.strategy_daily_result )
        #print("\n Strategy Results:")
        #print(self.strategy_result.results)
        self.days_since_trade +=1
        self.days_running += 1
        return self.strategy_daily_result
    
    
    def __update_position(self, trading_position : etp.TradingPosistion, target_date, 
                               asset_trading_order: float, trading_strategy_weight : float) -> pd.DataFrame:
        # Abrindo o dia
        trading_position.start_day(target_date)

        # Obtendo trade e controlando tamanho:
        trade = trading_strategy_weight * asset_trading_order
                
        # Executando trade caso necessario
        if (trade != 0):
            self.days_since_trade  = 0
            trading_position.execute_trade(target_date, trade)
            asset_exposure = trading_position.exposure_eop
            

        self.portfolio.current_asset_exposures[trading_position.asset_name] = trading_position.exposure_bop        
        # saving results:
        tp_result = trading_position.end_day()
        return tp_result
    

    def __end_position(self, trading_position : etp.TradingPosistion, target_date, 
                               asset_trading_order: float, trading_strategy_weight : float) -> pd.DataFrame:
        # Abrindo o dia
        trading_position.start_day(target_date)

        # Obtendo trade e controlando tamanho:
        trade = -trading_position.exposure_eop
                
        # Executando trade caso necessario
        if (trade != 0):
            self.days_since_trade  = 0
            trading_position.execute_trade(target_date, trade)
            asset_exposure = trading_position.exposure_eop
            

        self.portfolio.current_asset_exposures[trading_position.asset_name] = trading_position.exposure_bop                    
        # saving results:
        tp_result = trading_position.end_day()
        return tp_result

        

    def get_strategy_result(self) -> tr.TradingResult:
        pass

    def get_trading_order(self, target_date : date) -> tord.TradingOrder:
        #trading_order = tord.TradingOrder(self.portfolio)
        pass

    def is_ready(self, target_date: date) -> bool:
        pass
    
    def check_stop_signs(self):
        loss_from_last_max = self.get_loss_from_last_max()
        # is_vol_high = (self.number_of_vols_stds >= 3) &  (loss_from_last_max < self.stop_loss_limit /2)
        # if (not(self.is_vol_high)):
        #     self.is_vol_high = (self.number_of_vols_stds >= 3) &  (loss_from_last_max < -0.1)
        if (not(self.is_loss_high)):
            if (not(self.strat_pivot.empty)):
                avg_vol = self.strat_pivot.tail(5)["Strategy Vol."].mean()
                last3_daily_pnl = self.strat_pivot.tail(3)[tr.PNL_DAILY ]
                is_losing_last_3_days = ((last3_daily_pnl.iloc[0] < 0) &(last3_daily_pnl.iloc[1] < 0) & (last3_daily_pnl.iloc[2] < 0))
                self.is_loss_high = (loss_from_last_max <= self.stop_loss_limit ) # & (avg_vol >= 1.2*self.target_vol) #& (is_losing_last_3_days)
                # self.is_loss_high = (self.number_of_vols_stds > 3) &  (loss_from_last_max < -0.1) & (self.strategy_vol > 2*self.target_vol)
                
                if (self.is_loss_high):
                    self.days_to_resume_trading = self.DAYS_ON_STOPLOSS + 1
                    self.stop_trading_sign = True
        return 
    
    def check_vol_ok(self):
        return (self.number_of_vols_stds < 2) 
        
    def get_loss_from_last_max(self):
        loss_from_last_max = 0
        if (not(self.strat_pivot.empty)):
            last_max = self.strat_pivot[tr.PNL_CUMULATIVE].tail(10).max()

            currrent_pnl = self.strat_pivot[tr.PNL_CUMULATIVE].tail(1).iloc[0]
            
            if (last_max > 0):
                loss_from_last_max = (currrent_pnl)/ last_max - 1
            elif (last_max < 0):
                loss_from_last_max = 1-(currrent_pnl)/ last_max
            elif (last_max == 0):
                loss_from_last_max = currrent_pnl

        return loss_from_last_max 




    def set_strat_pivot(self):
        self.number_of_vols_stds = 0
        if (self.days_running >= 30):
            self.strat_pivot = self.strategy_result.results.groupby(tr.DATE).agg({tr.PNL_CUMULATIVE: np.sum, "Strategy Vol." : np.average , tr.PNL_DAILY : np.sum, tr.EXPOSURE_EOP : np.sum})
            self.strat_pivot = self.strat_pivot.dropna()
    
    def set_numb_of_vols_stds(self):
        self.number_of_vols_stds = 0
        if (self.days_running >= 30):
            avg_vol = self.strat_pivot.tail(30)["Strategy Vol."].mean()
            std_vol = self.strat_pivot.tail(30)["Strategy Vol."].std()

            last_vol = self.strat_pivot.tail(1)["Strategy Vol."].iloc[0]

            self.number_of_vols_stds = 0

            if (std_vol != 0):
                try:
                    self.number_of_vols_stds = (last_vol - avg_vol)/std_vol
                except:
                    print("Erro!" + " std_vol:"+ str(std_vol)  + " last_vol:"+ str(last_vol))