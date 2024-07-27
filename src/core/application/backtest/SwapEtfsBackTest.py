

import core.application.trading.TradingBook as tb
import core.application.strategies.VolatilityTargetingStrategy as vst
import core.application.strategies.TrendFollowingStrategy as ts
import core.infra.SwapRepository as sr
import core.domain.common.enum.AssetClassType as ac
import core.domain.common.logger.LoggingUtilities as lu
import core.domain.helpers.dirhelper as dh

class SwapEtfsBackTest:
    def __init__(self, short_index : str):
        lu.log("Backtest: STARTING")
        self.book_target_vol = 0.2
        self.book_max_leverage = 1

        # ----------------------------------------------------------------------------------------------------------------
        # Initializing swap sets:
        # ----------------------------------------------------------------------------------------------------------------
        swap_dao = sr.SwapDao()
        self.short_index = short_index
        equity_swaps = swap_dao.get_swap_set(ac.AssetClassType.EQUITY, short_index)
        credit_swaps = swap_dao.get_swap_set(ac.AssetClassType.CREDIT, short_index)
        fx_swaps = swap_dao.get_swap_set(ac.AssetClassType.FX, short_index)
        comdty_swaps = swap_dao.get_swap_set(ac.AssetClassType.COMMODITY, short_index)

        self.dates = swap_dao.get_dates(ac.AssetClassType.EQUITY)

        self.short_df = swap_dao.get_short_index_cumulative_return(min(self.dates), short_index)
        lu.log("Asset data loaded!")


        # ----------------------------------------------------------------------------------------------------------------
        # Initializing Strategies:
        # ----------------------------------------------------------------------------------------------------------------
        self.book_strats = []
        self.book_strats.append(vst.VolatilityTargetingStrategy("Equity", equity_swaps, target_vol=0.20))
        self.book_strats.append(vst.VolatilityTargetingStrategy("Credit", credit_swaps, target_vol=0.20))
        self.book_strats.append(ts.TrendFollowingStrategy("FX",fx_swaps, target_vol=0.20, months_to_hold=1, months_to_lag=12, max_leverage=5))
        self.book_strats.append(ts.TrendFollowingStrategy("Comdty",comdty_swaps, target_vol=0.20, months_to_hold=1, months_to_lag=12, max_leverage=3))


        # Testamos, mas esse conjunto nao deu certo
        # book_strats.append(ts.TrendFollowingStrategy("Equity",equity_swaps, target_vol=0.20, months_to_hold=1, months_to_lag=12, max_leverage=3))
        # book_strats.append(ts.TrendFollowingStrategy("Credit",credit_swaps, target_vol=0.20, months_to_hold=1, months_to_lag=12, max_leverage=4))
        # book_strats.append(ts.TrendFollowingStrategy("FX",fx_swaps, target_vol=0.20, months_to_hold=1, months_to_lag=12, max_leverage=5))
        # book_strats.append(ts.TrendFollowingStrategy("Comdty",comdty_swaps, target_vol=0.20, months_to_hold=1, months_to_lag=12, max_leverage=3))

        lu.log("Strategies initialized!")

    def run(self):
        # ----------------------------------------------------------------------------------------------------------------
        # Initializing and running Trading Book
        # ----------------------------------------------------------------------------------------------------------------
        book = tb.TradingBook('Offshore Book', strategies=self.book_strats, target_dates=self.dates, target_vol=self.book_target_vol, max_leverage=self.book_max_leverage)
        lu.log("Running Book!")
        book.run()
        lu.log("Backtest: FINISHED") # book.trading_results.to_csv("_Output/book_result.csv")
        r = book.trading_results.results
        r = r.merge(self.short_df, on="Date")

        # Salvando resultados e configuracoes:
        result_folder = dh.getNewResultDirectory("data/output/") 
        back_test_data = self.get_backtest_config()
        dh.save_dictionary_as_json(back_test_data, result_folder +  "/back_test_config.json")
        r.to_csv(result_folder + "/book_result_full_book_max_leverage=1_with_vols.csv", index=False)
        # r.to_csv("_Output/book_result_comdty_one_port.csv", index=False)

        lu.log("Resultado salvo!")
        return result_folder



    def get_backtest_config(self):
        back_test_data = {}
        back_test_data["Max Date"] = max(self.dates)
        back_test_data["Min Date"] = min(self.dates)
        back_test_data["Short Index"] = max(self.dates)
        back_test_data["book_target_vol"] = self.book_target_vol
        back_test_data["book_max_leverage"] = self.book_max_leverage
        back_test_data["Stretegies"] = dh.get_serialized_parameters_from_list(self.book_strats)
        return back_test_data