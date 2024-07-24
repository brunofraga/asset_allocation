from typing import List, Dict
from datetime import date
import pandas as pd

import core.application.trading.TradingPosition as etp

import core.domain.common.interfaces.IAsset as ias
import core.domain.models.trading.TradingResult as tr
import core.domain.models.asset.PortfolioAnalytics as pan
import core.domain.models.trading.TradingOrder as tord


# Cada estrategia contempla um Portfolio (<portfolio>), que carrega a lista de assets e consegue calcular sua vol., etc
# Para cada uma dessas assets, existe uma posicao de trading atual (trading position), listadas pelo dicionario trading_positions
# A estratégia também carrega o trading result

class TradingStrategy:
    
    # Constructor
    def __init__(self, strategy_name : str, assets : List[ias.IAsset]):
        # Properties ---------------------------------------------
        self.strategy_name : str = strategy_name
        self.trading_positions : Dict[str, etp.TradingPosistion] = {}
        self.hypothetical_trading_positions : Dict[str, etp.TradingPosistion] = {}
        self.strategy_result : tr.TradingResult = tr.TradingResult()
        self.portfolio : pan.Portfolio = pan.Portfolio("Portfolio: " + strategy_name, assets)
        self.portfolio_asset_names : List[str] = self.portfolio.asset_names
        self.strategy_vol: float = 0
        # --------------------------------------------------------
        

        # initiating trading positions and assets dictionary:
        for asset in assets:
            asset_name = asset.get_asset_name()
            self.trading_positions[asset_name] = etp.TradingPosistion(asset)
            self.hypothetical_trading_positions[asset_name] = etp.TradingPosistion(asset)


    def update(self, target_dt : date, trading_order : tord.TradingOrder, trading_strategy_weight : float)  -> tr.TradingResult:
        self.strategy_daily_result = tr.TradingResult()
        
        # atualizando cada uma das trading_positions:
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
            
            self.strategy_vol = self.portfolio.get_portfolio_volatility(target_dt, 90)
            self.strategy_daily_result.results["Strategy Vol."] = self.strategy_vol
                
        #print("Daily Results:")
        #print(self.strategy_daily_result.results)

        self.strategy_result = tr.union(self.strategy_result, self.strategy_daily_result )
        #print("\n Strategy Results:")
        #print(self.strategy_result.results)
        self.days_since_trade +=1
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
            self.portfolio.current_asset_weights[trading_position.asset_name] = asset_exposure
                    
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
        