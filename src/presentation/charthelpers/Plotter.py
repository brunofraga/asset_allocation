import pandas as pd
import src.presentation.charthelpers.plot_formatter as pf
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


def plot_series(df_series, plot_title, convert_ln_accum_return=False):
    series_name_list = df_series.columns
    colors = pf.btg_palette[:]
    t10_colors = px.colors.qualitative.T10[:]
    colors  = colors + t10_colors
    # colors = t10_colors

    starting_period = min(df_series["Date"])
    end_period = max(df_series["Date"])

    fig = go.Figure()
    fig = pf.format_figure(fig)
    title_init_dt = pf.format_dt(starting_period, '%Y-%m-%d')
    title_end_dt = pf.format_dt(end_period, '%Y-%m-%d')
    title_dt_range = title_init_dt[3:] + " a " + title_end_dt

    i = 0
    for seriesId in series_name_list:
        if (seriesId != "Date"):
            # stock_code = series_name_list[int(seriesId)]
            yValues = df_series[seriesId]
            if (convert_ln_accum_return):
                initLogPrice = np.log(df_series[seriesId][0])
                yValues = np.log(df_series[seriesId]) - initLogPrice
            
            fig.add_trace(go.Scatter(x=df_series['Date'], y=yValues, name= seriesId, yaxis="y2",
                                      opacity=0.8, marker_color=colors[i]))
            i+=1

    if len(series_name_list) == 2:
        print("Serie: " + seriesId)

    fig_title = "<b>" + plot_title + "</b>: <i>" + title_dt_range + "</i>"
    fig.update_layout(title=fig_title, title_font_color='#1F1F1F', title_font_size=12)

    yaxis_font_size = 12
    fig.update_layout(xaxis=dict(tickfont_size=12))
    fig.update_layout(yaxis=dict(tickfont_size=yaxis_font_size))
    fig.update_layout(yaxis2=dict(tickfont_size=yaxis_font_size))
    fig.update_layout(yaxis3=dict(tickfont_size=yaxis_font_size))
    # fig.update_layout(xaxis=dict(domain=[0.14, 0.95]))
    fig.update_layout(height=600)

    return fig #fig.show()

# plot_series("", df)

# plot_series("", df)




def plot_list(df, x_name, y_name_list, plot_title):
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    for y_name in y_name_list:
        # Using graph_objects
        isSecondary = np.average(df[y_name]) < 2
        # fig = go.Figure([go.Scatter(x=df[x_name], y=df[y_name], name="yaxis data")])
        fig.add_trace(go.Scatter(x=df[x_name], y=df[y_name], name=y_name), secondary_y=isSecondary)
        # else:
            
        # i += 1

    fig.update_layout(
    title=plot_title,
        #     xaxis_title="X Axis Title",
        #     yaxis_title="Y Axis Title",
#     legend_title="Legend Title",
#     font=dict(
#         family="Courier New, monospace",
#         size=18,
#         color="RebeccaPurple"
    )
    
    fig.show(config= {'displaylogo': False})

# # Import the os module
# import os
# os.getcwd()