import core.domain.engines.AssetEngine as aa
import core.infra.SwapRepository as sr
import core.domain.common.enum.AssetClassType as ac
import presentation.charthelpers.Plotter as plt
import core.domain.models.trading.TradingResult as tr
import numpy as np
import pandas as pd


file_suffix = "data/output/strat_tr"

def plot_images_from_dataframe(results : pd.DataFrame, save_images : bool):
    # strat_pivot = results.groupby(by=[tr.DATE, tr.STRATEGY]).agg({tr.PNL_CUMULATIVE: np.sum, "Strategy Vol." : np.average , tr.PNL_DAILY : np.sum})
    strat_pivot_pnl = results.pivot_table(index=tr.DATE, values=tr.PNL_CUMULATIVE,  columns=tr.STRATEGY, aggfunc=np.sum).reset_index()
    strat_pivot_expo = results.pivot_table(index=tr.DATE, values=tr.EXPOSURE_EOP,  columns=tr.STRATEGY, aggfunc=np.sum).reset_index()
    strat_pivot_weight = results.pivot_table(index=tr.DATE, values=tr.STRATEGY_WEIGHT,  columns=tr.STRATEGY, aggfunc=np.average).reset_index()
    strat_pivot_vol = results.pivot_table(index=tr.DATE, values="Strategy Vol.",  columns=tr.STRATEGY, aggfunc=np.average).reset_index()


    

    strat_fig_pnl = plt.plot_series(strat_pivot_pnl,"Strat Result: PnL")
    strat_fig_expo = plt.plot_series(strat_pivot_expo,"Strat Result: Exposure")
    strat_fig_w = plt.plot_series(strat_pivot_weight,"Strat Result: Weight")
    strat_fig_vol = plt.plot_series(strat_pivot_vol,"Strat Result: Vol")
    if (save_images):
            strat_fig_pnl.write_image(file_suffix + "_assets_accum_fig.png")

    strat_fig_pnl.show()
    strat_fig_expo.show()
    strat_fig_w.show()
    strat_fig_vol.show()


def run(path: str):
     results = pd.read_csv(path + "/book_result_full_book_max_leverage=1_with_vols.csv")
     plot_images_from_dataframe(results, False)

def run_pre_defined():
     path = "data/output/BackTest Result - 2024-07-27 050938"
     results = pd.read_csv(path + "/book_result_full_book_max_leverage=1_with_vols.csv")
     plot_images_from_dataframe(results, False)