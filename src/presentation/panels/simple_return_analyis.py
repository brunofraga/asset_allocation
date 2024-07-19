import core.domain.engines.AssetEngine as aa
import core.infra.SwapRepository as sr
import core.domain.common.enum.AssetClassType as ac
import presentation.charthelpers.Plotter as plt


def plot_images(short_index : str, save_images : bool):
    swap_dao = sr.SwapDao()

    # Defining aux plot function
    def __plot_returns(asset_class : ac.AssetClass, save_images : bool):
        # Initializing Swaps:
        assets_accum_df = swap_dao.get_etfs_cumulative_return(asset_class, short_index)
        swaps_accum_df = swap_dao.get_swaps_cumulative_return(asset_class, short_index)

        swaps_accum_fig = plt.plot_series(swaps_accum_df, asset_class.name + " | ETF's Swap Accumulated Return - ShortIndex: " + short_index)
        assets_accum_fig = plt.plot_series(assets_accum_df, asset_class.name + " | ETFs Accumulated Return")

        file_suffix = "_Output/" + asset_class.name
        assets_accum_df.to_csv(file_suffix + "_assets_accum_df.csv", index=False)
        swaps_accum_df.to_csv(file_suffix + "_swaps_accum_df.csv", index=False)

        assets_accum_fig.show()
        swaps_accum_fig.show()

        if (save_images):
            assets_accum_fig.write_image(file_suffix + "_assets_accum_fig.png")
            swaps_accum_fig.write_image(file_suffix + "_swaps_accum_fig.png")

        

    def __main__():
        # Plotting ETFs and Swaps for each asset class:
        for asset_class in ac.AssetClass:
            __plot_returns(asset_class, save_images=save_images)


        # Plotting short index:
        short_df = aa.get_accum_return(swap_dao.etf_df, "log_ret_SOFR").rename(columns={"accum_return" : "Accum_Ret_SOFR"})
        short_df = short_df.merge(aa.get_accum_return(swap_dao.etf_df, "log_ret_Libor").rename(columns={"accum_return" : "Accum_Ret_Libor"}), on="Date")
        fig3 = plt.plot_series(short_df, "Libor and SOFR Accumulated Return")
        fig3.show()
