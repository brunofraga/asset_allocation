from typing import List
import core.domain.models.asset.PortfolioAnalytics as p

# Just to clarify
class TradingOrder (dict):
    def __init__(self, portfolio :  p.Portfolio):
        for asset_name in portfolio.asset_names:
            self.add_trade(asset_name, 0)

    def add_trade(self, asset_name : str, trade_exposure : float):
        super().__setitem__(asset_name, trade_exposure)

    