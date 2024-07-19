# Lib para auxiliar na formatacao de plots
# Created at 2022-08-09

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, date
# import Libs.sql_module as sm

# Define color sequence
# btg_palette = ['#001E62', '#86B2EB', '#6F6F6F', '#FFC845', '#915ADC', '#F55F73', '#FFD2D2', '#00C389'];
btg_palette = ['#001E62', '#86B2EB', '#6F6F6F', '#357DFF', '#FFC845', '#915ADC', '#F55F73', '#FFD2D2', '#00C389',
               '#F0642D'];


# def btg_palette():
# return ['#001E62', '#86B2EB', '#6F6F6F', '#FFC845', '#915ADC', '#F55F73'];


def hex_to_rgb(hex_color_code, alpha=1):
    h = hex_color_code.lstrip('#')
    rgb_color_code = "rgba("
    for i in (0, 2, 4):
        rgb_color_code = rgb_color_code + str(int(h[i:i + 2], 16)) + ","

    rgb_color_code = rgb_color_code + str(alpha) + ")"
    return rgb_color_code


# Main Figure Format
def format_figure(fig, printable_size=False):
    # Create axis objects
    # fig.update_xaxes(title_text="Tempo")

    fig.update_layout(paper_bgcolor='#fff', plot_bgcolor='white')
    fig.update_layout(xaxis=dict(mirror=True, ticks='outside', showline=True, linecolor='black'))
    fig.update_layout(yaxis=dict(mirror=True, ticks='outside', showline=True, linecolor='black'))

    fig.update_xaxes(showline=True, linecolor='black')
    # fig.update_yaxes(showline=True,  linecolor='black', gridcolor='#BFBFBF')
    fig.update_yaxes(showline=True, linecolor='black')

    fig.update_layout(
        font_color="#1F1F1F",
        title_font_color="#1F1F1F",
        title_font_size=14)

    if (printable_size):
        fig.update_layout(autosize=False, width=700, height=450, )
        # fig.update_layout(autosize=False,width=700,height=250,)

    return fig


def format_dt(target_date, input_format="%Y-%m-%d"):
    if isinstance(target_date, str):
        date_time_obj = datetime.strptime(target_date, input_format)
        title_date = date_time_obj.strftime("%d/%b/%Y")

    else:
        title_date = target_date.strftime("%d/%b/%Y")

    return title_date


def min_max_range(df, column_name, factor=0):
    max_value = max(df[column_name])
    if (max_value > 0):
        max_value = max_value * (1 + factor)
    else:
        max_value = max_value * (1 - factor)

    min_value = min(df[column_name])
    if (min_value > 0):
        min_value = min_value * (1 - factor)
    else:
        min_value = min_value * (1 + factor)

    return [min_value, max_value]


def update_fig_axis(fig, date_range, rup_df, price_df=None, additional_exposures={}, additional_pnls={},
                    reset_pnls=False, use_log_price=True):
    # Obtendo sub-dataframes
    sampled_df = rup_df[(rup_df['Date'] >= date_range[0]) & (rup_df['Date'] <= date_range[1])]

    sampled_df = sampled_df.reset_index()

    if (reset_pnls):
        sampled_df['CumulativeAdjustedResult'] = sampled_df['CumulativeAdjustedResult'] - \
                                                 sampled_df['CumulativeAdjustedResult'][0]
        if (len(additional_pnls) > 0):
            for pnl_name in additional_pnls:
                sampled_df[pnl_name] = sampled_df[pnl_name] - sampled_df[pnl_name][0]

        pnl_plot_names = [list(additional_pnls.values())[i]['name'] for i in range(len(additional_pnls))]
        pnl_plot_names.append('P&L')

        for data_dic in fig['data']:
            if data_dic['name'] in pnl_plot_names:
                data_dic['x'] = sampled_df['Date']
                if data_dic['name'] == 'P&L':
                    data_dic['y'] = sampled_df['CumulativeAdjustedResult']

                else:
                    pnl_index = pnl_plot_names.index(data_dic['name'])
                    columns_name = list(additional_pnls.keys())[pnl_index]
                    data_dic['y'] = sampled_df[columns_name]

    if (price_df is not None):
        sampled_p_df = price_df[(price_df['Date'] >= date_range[0]) & (price_df['Date'] <= date_range[1])]

    # Obtendo valores máximos de exposição
    [min_exposure, max_expousure] = min_max_range(sampled_df, 'Exposure', 0.05)

    if "ShortExposure" in sampled_df.columns:
        min_exposure = min_max_range(sampled_df, 'ShortExposure', 0.05)[0]

    # Caso haja outras exposicoes para serem analisadas no periodo:
    if (len(additional_exposures) > 0):
        for exp_name in additional_exposures:
            max_expousure = max(max_expousure,
                                min_max_range(sampled_df, exp_name, additional_exposures[exp_name]['scale_factor'])[1])
            min_exposure = min(min_exposure,
                               min_max_range(sampled_df, exp_name, additional_exposures[exp_name]['scale_factor'])[0])

    # Atualizando eixos
    fig.update_layout(xaxis_range=date_range)  # Date

    [min_pnl, max_pnl] = min_max_range(sampled_df, 'CumulativeAdjustedResult', 0.005)
    # [min_pnl, max_pnl] = min_max_range(sampled_df, 'CumulativeAdjustedResult',1)
    # Caso haja outras exposicoes para serem analisadas no periodo:
    if (len(additional_pnls) > 0):
        for pnl_name in additional_pnls:
            max_pnl = max(max_pnl, min_max_range(sampled_df, pnl_name, additional_pnls[pnl_name]['scale_factor'])[1])
            min_pnl = min(min_pnl, min_max_range(sampled_df, pnl_name, additional_pnls[pnl_name]['scale_factor'])[0])

    fig.update_layout(yaxis_range=[min_pnl, max_pnl]);  # PnL

    if (use_log_price):
        price_column = 'LogPrice'
    else:
        price_column = 'Close'

    if (price_df is not None):
        fig.update_layout(yaxis2_range=min_max_range(sampled_p_df, price_column, 0.001));  # Log Price
    else:
        fig.update_layout(yaxis2_range=min_max_range(sampled_df, price_column, 0.001));  # Log Price

    fig.update_layout(yaxis3_range=[min_exposure, max_expousure]);  # Exposure

    return fig

#
# def build_daily_result_plot(dr_df, additional_exposures={}, price_series_id=0, additional_pnls={}, use_log_price=True):
#     min_date = min(dr_df['Date']).strftime("%Y-%m-%d")
#     max_date = max(dr_df['Date']).strftime("%Y-%m-%d")
#     max_date_title = max(dr_df['Date']).strftime("%d/%b")
#
#     # SM = sm.SQLManager()
#
#     # Obtendo Log Price Series List
#     if (price_series_id != 0):
#
#         # price_df = SM.get_price_history(price_series_id, min_date, max_date)
#         # price_df['LogPrice'] = np.log(price_df['Close'])
#         # price_code = SM.get_series_code(price_series_id)
#     else:
#         # price_code = SM.get_series_code(dr_df['SeriesID'][0])
#
#     fig = go.Figure()
#
#     # Add traces
#     # btg_palette = ['#001E62', '#86B2EB', '#6F6F6F', '#FFC845', '#915ADC', '#F55F73'];
#     fig.add_trace(go.Scatter(x=dr_df['Date'], y=dr_df['CumulativeAdjustedResult'], name="P&L", marker_color='#001E62'))
#
#     if (price_series_id != 0):
#         if (use_log_price):
#             fig.add_trace(
#                 go.Scatter(x=price_df['Date'], y=price_df['LogPrice'], name=price_code, marker_color='#86B2EB',
#                            yaxis="y2", opacity=0.5))
#         else:
#             fig.add_trace(
#                 go.Scatter(x=price_df['Date'], y=price_df['Close'], name=price_code, marker_color='#86B2EB', yaxis="y2",
#                            opacity=0.5))
#     else:
#         fig.add_trace(
#             go.Scatter(x=dr_df['Date'], y=dr_df['LogPrice'], name=price_code, marker_color='#86B2EB', yaxis="y2"))
#
#     # fig.add_trace(go.Scatter(x=dr_df['Date'], y=dr_df['Exposure'], name="Total Exposure",marker_color='#6F6F6F', yaxis="y3", opacity = 0.7))
#     fig.add_trace(
#         go.Scatter(x=dr_df['Date'], y=dr_df['Exposure'], name="Total Exposure", marker_color='#001E62', yaxis="y3",
#                    opacity=0.7))
#
#     if (len(additional_exposures) > 0):
#         i = 0
#         initial_shift = 3
#         for exp_col_name in additional_exposures:
#             exp_name = additional_exposures[exp_col_name]['name']
#             fig.add_trace(go.Scatter(x=dr_df['Date'], y=dr_df[exp_col_name], name=exp_name,
#                                      marker_color=btg_palette[initial_shift + i], yaxis="y3", opacity=0.7))
#             i = i + 1
#             if (i + 3 >= len(btg_palette)):
#                 i = 0
#                 initial_shift = 0
#
#     if (len(additional_pnls) > 0):
#         i = 0
#         initial_shift = 3
#         for pnl_col_name in additional_pnls:
#             pnl_name = additional_pnls[pnl_col_name]['name']
#             fig.add_trace(go.Scatter(x=dr_df['Date'], y=dr_df[pnl_col_name], name=pnl_name,
#                                      marker_color=btg_palette[initial_shift + i]))
#             i = i + 1
#             if (i + 3 >= len(btg_palette)):
#                 i = 0
#                 initial_shift = 0
#
#     if (dr_df['ShortExposure'].sum() != 0):
#         fig.add_trace(
#             go.Scatter(x=dr_df['Date'], y=dr_df['ShortExposure'], name="Short Exposure", marker_color='#F55F73',
#                        yaxis="y3"))
#
#     if (use_log_price):
#         price_title = "LogPrice"
#     else:
#         price_title = "Price"
#     fig.update_layout(
#         xaxis=dict(domain=[0.12, 0.95]),
#         yaxis=dict(title="P&L", title_font_size=14),
#         yaxis2=dict(title=price_title, anchor="x", overlaying="y", side="right", title_font_size=14),
#         yaxis3=dict(title="Expousure", anchor="free", overlaying="y", side="left", position=0, title_font_size=14)
#         #     yaxis3=dict(title="<b>Tempo Posicionado (dias)</b>",anchor="x",overlaying="y",side="right")
#     )
#
#     # ============================================================================================================
#
#     fig = format_figure(fig)
#
#     return fig