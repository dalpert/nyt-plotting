import numpy as np
import pandas as pd
import datetime
from datetime import date
from time import strftime
from time import gmtime
import matplotlib.pyplot as plt
import sys
import seaborn as sns
sns.set(style="darkgrid")

# Create table with additional date-related columns and columns for plot labels
def add_cols(df):
    df_copy = df.copy()
    # add additional columns
    df_copy['date_obj'] = df_copy['date'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d').date())
    df_copy['month'] = df_copy['date_obj'].apply(lambda x: x.month)
    df_copy['date_num'] = df_copy['date_obj'].apply(lambda x: x.day)
    df_copy['month_name'] = df_copy['date_obj'].apply(lambda x: x.strftime("%B"))
    df_copy['year'] = df_copy['date_obj'].apply(lambda x: x.year)
    df_copy['date_label'] = df_copy['date_obj'].apply(lambda x: x.strftime("%b") + ' ' + x.strftime("%y"))
    df_copy['time_label'] = df_copy['elapsed_seconds'].apply(lambda x: strftime("%M:%S", gmtime(x)))
    return(df_copy)

# Extract only rows for solved puzzles
def get_solved_df(df):
    xw_solved = df[(df.solved == 1) & (df.elapsed_seconds > 0)]
    return(xw_solved)

# Get rolling averages for solve time
def get_rolling_df(solved_df, roll_num):
    xw_rolling = solved_df.groupby('day')[['date', 'elapsed_seconds']].rolling(roll_num, closed='right', min_periods=int(roll_num/2)).mean().reset_index()
    xw_rolling.rename(columns={'level_1':'old_idx'}, inplace=True)
    return(xw_rolling)

# Merge rolling data with original table to retain plotting labels
def get_plotting_df(xw_rolling, xw_solved):
    # join rolling avg and solved dataset to get a table with both dates and rolling averages
    plotting_df = xw_rolling.merge(xw_solved[['date', 'date_label', 'date_obj']], left_on='old_idx', right_index=True)
    plotting_df.dropna(axis=0, inplace=True)
    plotting_df['time_label'] = plotting_df['elapsed_seconds'].apply(lambda x: strftime("%M:%S", gmtime(x)))
    plotting_df.rename(columns={'day':'Day'}, inplace=True)
    return(plotting_df.sort_values(by='date').reset_index())

# Create line plot
def make_lineplot(df, roll_num):
	# function to pass into yaxis formatter
    def ytick_format_func(value, tick_number):
        if value >= 3600:
            return(strftime("%H:%M:%S", gmtime(value)))
        return(strftime("%M:%S", gmtime(value)))
    
    sns.set(font_scale=1.3)
    g = sns.relplot(
        data=df, 
        x="date", y="elapsed_seconds", hue='Day',
        kind="line",
        height=6, aspect=3,
        linewidth=3,
        hue_order = ['Sun', 'Sat', 'Fri', 'Thu', 'Wed', 'Tue', 'Mon']
    )
    g.set(ylim = (0,max(df.elapsed_seconds)))
    g.set_axis_labels('Date', 'Solve time')
    g.set(title = 'NYT Crossword Solve Time Over Time (' + str(roll_num) + 'd rolling average)')
    g.set(xticks=df.date[::60])
    g.set_xticklabels(df.date_label[::60], rotation=45)
    #g.set(yticks=df.elapsed_seconds)
    for ax in g.axes.flat:
        ax.yaxis.set_major_formatter(plt.FuncFormatter(ytick_format_func))
    #g.set_yticklabels(rolling_df.time_label)
    #plt.tight_layout()
    plt.savefig('nytxw_lineplot.png', bbox_inches='tight', pad_inches = 0.6)

fname = sys.argv[1]
roll_num = int(sys.argv[2])
xw = pd.read_csv(fname)
xw_full = add_cols(xw)
#xw_full = xw_full[xw_full.date_obj > date(2021,7,1)]
xw_solved = get_solved_df(xw_full)
xw_rolling = get_rolling_df(xw_solved, roll_num)
xw_plotting = get_plotting_df(xw_rolling, xw_solved)
make_lineplot(xw_plotting, roll_num)
