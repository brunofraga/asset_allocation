import core.domain.engines.AssetEngine as aa
import core.infra.SwapRepository as sr
import core.domain.common.enum.AssetClassType as ac
import presentation.charthelpers.Plotter as plt
import core.domain.models.trading.TradingResult as tr
import numpy as np
import pandas as pd
import plotly.graph_objects as go
# re.sub(r",(?=[^][]*\])", "", str)

file_suffix = "data/output/strat_tr"

def plot_images_from_dataframe(out_pah : str, results : pd.DataFrame, save_images : bool):
     # strat_pivot = results.groupby(by=[tr.DATE, tr.STRATEGY]).agg({tr.PNL_CUMULATIVE: np.sum, "Strategy Vol." : np.average , tr.PNL_DAILY : np.sum})
     figs_to_plot = []

     
     strat_pivot_pnl = results.pivot_table(index=tr.DATE, values=tr.PNL_CUMULATIVE,  columns=tr.STRATEGY, aggfunc=np.sum).reset_index().fillna(0)
     strat_pivot_expo = results.pivot_table(index=tr.DATE, values=tr.EXPOSURE_EOP,  columns=tr.STRATEGY, aggfunc=np.sum).reset_index().fillna(0)
     strat_pivot_weight = results.pivot_table(index=tr.DATE, values=tr.STRATEGY_WEIGHT,  columns=tr.STRATEGY, aggfunc=np.average).reset_index().fillna(0)
     strat_pivot_vol = results.pivot_table(index=tr.DATE, values="Strategy Vol.",  columns=tr.STRATEGY, aggfunc=np.average).reset_index().fillna(0)

     book_pivot_pnl = results.pivot_table(index=tr.DATE, values=tr.PNL_CUMULATIVE,  aggfunc=np.sum).reset_index().fillna(0)
     book_pivot_expo = results.pivot_table(index=tr.DATE, values=tr.EXPOSURE_EOP, aggfunc=np.sum).reset_index().fillna(0)
     book_pivot_vol = results.pivot_table(index=tr.DATE, values="Book Vol", aggfunc=np.average).reset_index().fillna(0)
     
     strategies_list= list(strat_pivot_weight.columns)
     strategies_list.remove(tr.DATE)


     book_pivot_weight = pd.DataFrame(data={tr.DATE : list(strat_pivot_weight[tr.DATE]), "Total Weight": list(strat_pivot_weight[strategies_list].sum(axis=1)) })
     book_pivot_weight = book_pivot_weight.fillna(0)

     figs_to_plot.append(specific_format(plt.plot_series(strat_pivot_pnl,"Strat Result: PnL")))
     figs_to_plot.append(specific_format(plt.plot_series(strat_pivot_expo,"Strat Result: Exposure")))
     figs_to_plot.append(specific_format(plt.plot_series(strat_pivot_weight,"Strat Result: Weight")))
     figs_to_plot.append(specific_format(plt.plot_series(strat_pivot_vol,"Strat Result: Vol")))

     figs_to_plot.append(specific_format(plt.plot_series(book_pivot_pnl,"Book Result: PnL")))
     figs_to_plot.append(specific_format(plt.plot_series(book_pivot_expo,"Book Result: Exposure")))
     figs_to_plot.append(specific_format(plt.plot_series(book_pivot_weight,"Book Result: Weight")))
     figs_to_plot.append(specific_format(plt.plot_series(book_pivot_vol,"Book Result: Vol")))

     if (save_images):
             for fig in figs_to_plot:
                  fig_name = fig.layout.title.text.replace("</", "<").replace(":", " ").replace("/","-").replace("<b>", "").replace("<i>", "")
                  fig.write_image(out_pah + "/" + fig_name + ".png")
     
     for fig in figs_to_plot:
          fig.show()


def run(path: str, save_plots : bool):
     results = pd.read_csv(path + "/book_result_full_book_max_leverage=1_with_vols.csv")
     plot_images_from_dataframe(path, results, save_plots)

def run_pre_defined(save_plots : bool):
     path = "data/output/BackTest Result - 2024-07-27 190153"
     results = pd.read_csv(path + "/book_result_full_book_max_leverage=1_with_vols.csv")
     plot_images_from_dataframe(path, results, save_plots)


def specific_format(fig : go.Figure):
     # Equity | Vol. Targeting
     # Credit | Vol. Targeting
     # FX | Trend-Following
     # Comdty | Trend-Following
     fig.for_each_trace(lambda trace: trace.update(line_width=3))
     fig.for_each_trace(lambda trace: trace.update(marker_color="#00C389", line_width=3) if "Equity" in trace.name else ())
     fig.for_each_trace(lambda trace: trace.update(marker_color="#86B2EB", line_width=3) if "Credit" in trace.name else ())
     fig.for_each_trace(lambda trace: trace.update(marker_color="#915ADC", line_width=3) if "FX" in trace.name else ())
     fig.for_each_trace(lambda trace: trace.update(marker_color="#000000", line_width=3) if "Comdty" in trace.name else ())
     return fig
     
     