import pandas as pd

DATE = "Date"
CLOSE_PRICE = "Close Price"
LOG_RETURN = "log_ret"

class IAsset:
    DATE = DATE
    CLOSE_PRICE = CLOSE_PRICE
    LOG_RETURN = LOG_RETURN


    def get_asset_name(self ) -> str:
        """Get assset name identifier ."""
        pass

    def get_price(self, target_date : str) -> float:
        """Get price, given a target date."""
        pass

    def get_daily_log_return(self, target_date) -> float:
        """Get return given a target date."""
        pass

    def get_daily_return(self, target_date) -> float:
        """Get return given a target date."""
        pass

    def get_vol_daily_return(self, target_date) -> float:
        """Get return given a target date."""
        pass

    def get_daily_log_returns(self) -> pd.DataFrame:
        """Get DataFrame with Date and LogReurn """
        pass

    def has_data(self,target_date) -> bool:
        """Get DataFrame with Date and LogReurn """
        pass