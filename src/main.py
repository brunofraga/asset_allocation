#-------------------------------------------------------------------#
# ASSET ALLOCATION
# requirements.txt gerado a partir de pipreqs src
#-------------------------------------------------------------------#



import core.application.backtest.SwapEtfsBackTest as sebt
import presentation.terminal.prompt_styler as prmt
import presentation.panels.simple_return_analyis as sra
import sys

# Function to run back test
def run_bt():
    print("Running BT...")
    prmt.print_dash_line()
    backtest = sebt.SwapEtfsBackTest(short_index="Libor")
    backtest.run()
    

# Function to plot asset returns
def plot_asset_returns():
    print("Plotting asset returns...")
    short_index = "Libor"
    sra.plot_images(short_index, False)


prmt.show_header()

def main(argv):
    # default mode:
    if (len(argv) == 1):
        run_bt()
    else:
        second_argument = argv[1]
        if (second_argument == "run_bt"):
            run_bt()
        elif (second_argument ==  "plot_asset_returns"):
            plot_asset_returns()
        else:
            print("Not a valid command: " + second_argument)



if __name__ == '__main__':
    main(sys.argv)
