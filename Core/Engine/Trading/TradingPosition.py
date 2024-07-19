from datetime import date
import pandas as pd

import Core.Entity.Asset.Interfaces.IAsset as ias
import Core.Entity.Trading.TradingResult as tr

class TradingPosistion:
    # --- Constants ------------------------------------------
    # the costs actually varies for each asset
    transaction_cost_percent : float = 0.000250

    # not being used:
    annual_borrow_cost_percent : float = 0.0035
    daily_borrow_cost_percent : float = annual_borrow_cost_percent / 252
    trade_efficiency_cost_percent : float = 0.000125


    def __init__(self, asset : ias.IAsset):
        # --- Properties -----------------------------------------
        self.asset : ias.IAsset = asset
        self.results : tr.TradingResult = tr.TradingResult()

        self.asset_name : str = asset.get_asset_name()

        # --- Daily results ---------------------------------------
        # self.self.target_date : date
        
        self.daily_return : float = 0
        self.exposure_bop : float = 0
        self.exposure_eop : float = 0

        self.trade_exposure : float = 0
        self.trade_cost : float = 0
        
        self.pnl_total_daily : float = 0
        self.pnl_cumulative : float = 0

        self.days_exposure : int = 0

        # self.qtt_bop : int
        # self.qtt_eop : int

        # self.d0_close_price : float
        # self.d1_close_price : float

        # self.trade_price : float
        # self.trade_qtt : float

        # self.pnl_trade: float # adicionar depois
        # self.pnl_position : float # adicionar depois
        # --------------------------------------------------------
         

    def start_day(self, target_date : date):
        self.target_date = target_date

        # -----------------------------------------
        # Updating d1 values:
        # -----------------------------------------
        self.trade_cost = 0
        self.trade_exposure = 0
        self.pnl_total_daily  = 0
        #self.d1_close_price = self.d0_close_price
        #self.qtt_bop = self.qtt_eop
        self.exposure_bop = self.exposure_eop
        

        # --------------------------------------------
        # Atualizando saldo e iniciando contabilizacao
        # do pnl
        # -----------------------------------------
        self.daily_return = self.asset.get_daily_return(target_date)

        if (self.exposure_bop != 0):
            self.days_exposure += 1
            self.exposure_eop = self.exposure_bop * (self.daily_return)
            self.pnl_total_daily = self.exposure_eop - self.exposure_bop
        else:
            self.days_exposure = 0

        


    def execute_trade(self, target_date : date, trade_exposure):
        if (self.exposure_bop == 0):
            self.days_exposure += 1


        self.trade_exposure = trade_exposure
        self.trade_cost = abs(trade_exposure) * self.transaction_cost_percent

        self.pnl_total_daily -= self.trade_cost
        self.exposure_eop += self.trade_exposure

    def end_day(self) -> pd.DataFrame:
        self.pnl_cumulative += self.pnl_total_daily

        return self.results.update(
            target_date=self.target_date, 
            asset_name=self.asset_name,
            daily_return=self.daily_return,
            exposure_bop=self.exposure_bop,
            exposure_eop=self.exposure_eop,
            trade_exposure=self.trade_exposure,
            trade_cost=self.trade_cost,
            pnl_daily=self.pnl_total_daily,
            pnl_cumulative=self.pnl_cumulative,
            days_exposure=self.days_exposure)