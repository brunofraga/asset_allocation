#-------------------------------------------------------------------#
#                             _                                     #
#      /\                    | |                                    #
#     /  \    ___  ___   ___ | |_                                   #
#    / /\ \  / __|/ __| / _ \| __|                                  # 
#   / ____ \ \__ \\__ \|  __/| |_                                   #
#  /_/    \_\|___/|___/ \___| \__|                                  #
#                                                                   #
#             _  _                     _    _                       #
#      /\    | || |                   | |  (_)                      #
#     /  \   | || |  ___    ___  __ _ | |_  _   ___   _ __          #
#    / /\ \  | || | / _ \  / __|/ _` || __|| | / _ \ | '_ \         #
#   / ____ \ | || || (_) || (__| (_| || |_ | || (_) || | | |        #
#  /_/    \_\|_||_| \___/  \___|\__,_| \__||_| \___/ |_| |_|        #
#                                                                   #
#-------------------------------------------------------------------#



import Core.Engine.Trading.TradingBook as tb
import Core.Engine.Strategy.VolatilityTargetingStrategy as vst
import Core.Engine.Strategy.TrendFollowingStrategy as ts
import Core.Infra.SwapRepository as sr
import Core.Entity.Asset.AssetClass as ac
import Common.LoggingUtilities as lu
import Presentation.prompt_styler as prmt


prmt.show_header()
prmt.print_dash_line()
lu.log("Backtest: STARTING")

# ----------------------------------------------------------------------------------------------------------------
# Initializing swap sets:
# ----------------------------------------------------------------------------------------------------------------
swap_dao = sr.SwapDao()
short_index = "Libor"
equity_swaps = swap_dao.get_swap_set(ac.AssetClass.EQUITY, short_index)
credit_swaps = swap_dao.get_swap_set(ac.AssetClass.CREDIT, short_index)
fx_swaps = swap_dao.get_swap_set(ac.AssetClass.FX, short_index)
comdty_swaps = swap_dao.get_swap_set(ac.AssetClass.COMMODITY, short_index)

dates = swap_dao.get_dates(ac.AssetClass.EQUITY)

short_df = swap_dao.get_short_index_cumulative_return(min(dates), short_index)
lu.log("Asset data loaded!")


# ----------------------------------------------------------------------------------------------------------------
# Initializing Strategies:
# ----------------------------------------------------------------------------------------------------------------
book_strats = []
book_strats.append(vst.VolatilityTargetingStrategy("Equity", equity_swaps, target_vol=0.20))
book_strats.append(vst.VolatilityTargetingStrategy("Credit", credit_swaps, target_vol=0.20))
# book_strats.append(vst.VolatilityTargetingStrategy("Comdty", comdty_swaps, target_vol=0.20))
# book_strats.append(vst.VolatilityTargetingStrategy("FX", fx_swaps, target_vol=0.20))
book_strats.append(ts.TrendFollowingStrategy("FX",fx_swaps, target_vol=0.20, months_to_hold=1, months_to_lag=12, max_leverage=5))
book_strats.append(ts.TrendFollowingStrategy("Comdty",comdty_swaps, target_vol=0.20, months_to_hold=1, months_to_lag=12, max_leverage=3))


# Testamos, mas esse conjunto nao deu certo
# book_strats.append(ts.TrendFollowingStrategy("Equity",equity_swaps, target_vol=0.20, months_to_hold=1, months_to_lag=12, max_leverage=3))
# book_strats.append(ts.TrendFollowingStrategy("Credit",credit_swaps, target_vol=0.20, months_to_hold=1, months_to_lag=12, max_leverage=4))
# book_strats.append(ts.TrendFollowingStrategy("FX",fx_swaps, target_vol=0.20, months_to_hold=1, months_to_lag=12, max_leverage=5))
# book_strats.append(ts.TrendFollowingStrategy("Comdty",comdty_swaps, target_vol=0.20, months_to_hold=1, months_to_lag=12, max_leverage=3))

lu.log("Strategies initialized!")


# ----------------------------------------------------------------------------------------------------------------
# Initializing and running Trading Book
# ----------------------------------------------------------------------------------------------------------------
book = tb.TradingBook('Offshore Book', strategies=book_strats, target_dates=dates, target_vol=0.2, max_leverage=1)
lu.log("Running Book!")
book.run()
lu.log("Backtest: FINISHED") # book.trading_results.to_csv("_Output/book_result.csv")
r = book.trading_results.results
r = r.merge(short_df, on="Date")
r.to_csv("_Output/book_result_full_book_max_leverage=1_with_vols.csv", index=False)
# r.to_csv("_Output/book_result_comdty_one_port.csv", index=False)

lu.log("Resultado salvo!")
prmt.print_dash_line()
