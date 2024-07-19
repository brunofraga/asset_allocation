#-------------------------------------------------------------------#
# ASSET ALLOCATION
#-------------------------------------------------------------------#


import core.application.backtest.SwapEtfsBackTest as sebt
import presentation.terminal.prompt_styler as prmt
import presentation.panels.simple_return_analyis as sra

prmt.show_header()
prmt.print_dash_line()

def run_bt():
    backtest = sebt.SwapEtfsBackTest(short_index="Libor")
    backtest.run()
    prmt.print_dash_line()

def plot_asset_returns():
    short_index = "Libor"
    sra.plot_images(short_index, False)


# plot_asset_returns()

run_bt()


