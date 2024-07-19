#-------------------------------------------------------------------#
# ASSET ALLOCATION
#-------------------------------------------------------------------#

import core.application.backtest.SwapEtfsBackTest as sebt
import presentation.terminal.prompt_styler as prmt
import presentation.panels.simple_return_analyis as sra

# Function to run back test
def run_bt():
    print("Running BT...")
    backtest = sebt.SwapEtfsBackTest(short_index="Libor")
    backtest.run()
    prmt.print_dash_line()

# Function to plot asset returns
def plot_asset_returns():
    print("Plotting asset returns...")
    short_index = "Libor"
    sra.plot_images(short_index, False)


prmt.show_header()

plot_asset_returns()
# run_bt()

prmt.print_dash_line()


