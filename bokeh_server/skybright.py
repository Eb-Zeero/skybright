import time
from datetime import datetime, timedelta
from math import pi

import numpy as np
import pandas as pd
from bokeh.io import curdoc
from bokeh.layouts import column, widgetbox, layout, gridplot
from bokeh.models import HoverTool, ColumnDataSource, Select, Button, BoxAnnotation, Label
from bokeh.models.callbacks import CustomJS
from bokeh.models.widgets import Slider, Div, CheckboxGroup, Tabs, Panel
from bokeh.plotting import figure
from dateutil.relativedelta import relativedelta
import pymysql
import os
import ephem


def empty_source(t, p, f):
    data_source[t][p][f].data['x'] = []
    data_source[t][p][f].data['h_date'] = []
    data_source[t][p][f].data['y'] = []
    data_source[t][p][f].data['error'] = []
    data_source[t][p][f].data['filter'] = []
    data_source[t][p][f].data['telescope'] = []


def empty_ext(t, f):
    ext_source[t][f].data['x'] = []
    ext_source[t][f].data['h_date'] = []
    ext_source[t][f].data['y'] = []
    ext_source[t][f].data['error'] = []
    ext_source[t][f].data['filter'] = []
    ext_source[t][f].data['telescope'] = []


def empty_range(t, p, f):
    range_source[t][p][f].data['x'] = []
    range_source[t][p][f].data['h_date'] = []
    range_source[t][p][f].data['y'] = []
    range_source[t][p][f].data['error'] = []
    range_source[t][p][f].data['filter'] = []
    range_source[t][p][f].data['position'] = []
    range_source[t][p][f].data['telescope'] = []


config = {
    'user': os.environ['SKY_DATABASE_USER'],
    'passwd': os.environ['SKY_DATABASE_PASSWORD'],
    'host': os.environ['SKY_DATABASE_HOST'],
    'db': os.environ['SKY_DATABASE_NAME']
}


def find_filter_number(char_):
    num_ = 0 if char_ == 'V' else 1 if char_ == 'B' else 2 if char_ == 'R' else 3
    return num_


def find_filter_name(num_):
    char_ = 'V' if num_ == 0 else 'B' if num_ == 1 else 'R' if num_ == 3 else 'I'
    return char_


def find_position(p):
    return 'Zenith' if p == 0 else 'North' if p == 1 else 'East' if p == 2 else 'West' if p == 3 else 'South'


def find_tittle(num_):
    return 'Zenith' if num_ == 0 else 'North' if num_ == 1 else 'East' if num_ == 2 else 'West' if num_ == 3 \
        else 'South'


def find_telescope_name(tel_):
    return 'Sunrise' if tel_ == 0 else 'Sunset'


def set_colour(tel_, fil_):
    col_ = 'black'
    if tel_ == 0:
        col_ = 'brown' if fil_ == 0 else 'blue' if fil_ == 1 else '#c615f2' if fil_ == 2 else 'green'
    if tel_ == 1:
        col_ = '#f2155f' if fil_ == 0 else '#07a9bf' if fil_ == 1 else '#f4ac02' if fil_ == 2 else '#02ce24'
    return col_


def set_colour_range(tel_, pos_, fil_):
    col_ = 'black'
    if tel_ == 0:
        if fil_ == 0:
            col_ = '#56412b' if pos_ == 0 else '#4d4960' if pos_ == 1 else '#f20000' if pos_ == 2 else \
                '#5df4d8' if pos_ == 3 else '#ff00fd'
        if fil_ == 1:
            col_ = '#8c745c' if pos_ == 0 else '#6f65a3' if pos_ == 1 else '#e07676' if pos_ == 2 else \
                '#076d05' if pos_ == 3 else '#dd6cdd'
        if fil_ == 2:
                col_ = '#dd9144' if pos_ == 0 else '#3c2f7f' if pos_ == 1 else '#8c2b2b' if pos_ == 2 else \
                    '#4a6d49' if pos_ == 3 else '#a041a0'
        if fil_ == 3:
            col_ = '#f47a00' if pos_ == 0 else '#290dba' if pos_ == 1 else '#ff9999' if pos_ == 2 else \
                '#4ed34c' if pos_ == 3 else '#590d59'
    if tel_ == 1:
        if fil_ == 0:
            col_ = 'gold' if pos_ == 0 else 'skyblue' if pos_ == 1 else 'Orange' if pos_ == 2 else \
                '#1ff14d' if pos_ == 3 else '#8000ff'
        if fil_ == 1:
            col_ = '#ff7199' if pos_ == 0 else '#1b8196' if pos_ == 1 else '#8e3d07' if pos_ == 2 else \
                '#000000' if pos_ == 3 else '#984be5'
        if fil_ == 2:
            col_ = '#e0ce59' if pos_ == 0 else '#74a8b2' if pos_ == 1 else '#d9bcff' if pos_ == 2 else \
                '#10967d' if pos_ == 3 else '#7b6096'
        if fil_ == 3:
            col_ = '#96861b' if pos_ == 0 else '#007fc4' if pos_ == 1 else '#9b368a' if pos_ == 2 else \
                '#961082' if pos_ == 3 else '#522160'
    return col_


def find_range_date(date_):
    if '00:00:00' <= str(date_)[11:] < '13:00:00':
        return (date_ - timedelta(days=1)).date()
    elif '13:00:00' <= str(date_)[11:] <= '23:59:59':
        return date_.date()
    else:
        return date_.date()


def find_date_index(date_, l_date):
    index_ = 0
    for d in l_date:
        if date_ == d:
            return index_
        index_ += 1
    return -1


def append_twice(val_):
    return [val_, val_]


def read_database(date_, num):
    global config
    data = []
    date_n = date_ + timedelta(days=1)
    if num == 7:
        date_ = date_n - timedelta(days=num)


    sql = (
                    "SELECT DATE_TIME, SKYBRIGHTNESS, CLOUD_COVERAGE, MOON, TELESCOPE, FILTER_BAND, POSX, SB_ERROR "
                    "FROM SkyBrightness "
                    "WHERE DATE_TIME > '%s-%s-%s 13:00:00' "
                    "AND DATE_TIME < '%s-%s-%s 13:00:00' "
                    "AND SKYBRIGHTNESS != 0 "
                ) % (str(date_)[0:4], str(date_)[5:7], str(date_)[8:10],
                     str(date_n)[0:4], str(date_n)[5:7], str(date_n)[8:10])

    cnx = pymysql.connect(**config)
    try:
        cursor = cnx.cursor()
        cursor.execute(sql)
        data = cursor.fetchall()

    except :
        if cnx:
            print("there was a problem with selecting")

    finally:
        if cnx:
            cnx.close()
        return data


def read_extinction_database(date_, num):
    ext_data = []
    date_n = date_ + timedelta(days=1)
    if num == 7:
        date_ = date_n - timedelta(days=num)

    select_ext = (
                     "SELECT DATE_TIME, EXT_ERROR, EXTINCTION, FILTER_BAND, TELESCOPE, CLOUD_COVERAGE "
                     "FROM Extinctions_Red WHERE DATE_TIME > '%s-%s-%s 13:00:00' AND DATE_TIME < '%s-%s-%s 13:00:00' "
                 ) % (str(date_)[0:4], str(date_)[5:7], str(date_)[8:10],
                      str(date_n)[0:4], str(date_n)[5:7], str(date_n)[8:10])
    cnx = pymysql.connect(**config)
    try:
        cursor = cnx.cursor()
        cursor.execute(select_ext)
        ext_data = cursor.fetchall()
        print("yeahh")

    except:
        if cnx:
            print("there was a problem with selecting")

    finally:
        if cnx:
            cnx.close()
            return ext_data


def read_range_database(min_date, max_date):
    range_data = []
    select_sb = (
                    "SELECT DATE_TIME, SKYBRIGHTNESS, CLOUD_COVERAGE, MOON, TELESCOPE, FILTER_BAND, POSX, SB_ERROR  "
                    "FROM SkyBrightness "
                    "WHERE DATE_TIME > '%s-%s-%s 13:00:00' "
                    "AND DATE_TIME < '%s-%s-%s 13:00:00' "
                    "AND SKYBRIGHTNESS != 0 "
                ) % (min_date[0], min_date[1], min_date[2],
                      max_date[0], max_date[1], max_date[2])

    cnx = pymysql.connect(**config)
    try:
        cursor = cnx.cursor()
        cursor.execute(select_sb)
        range_data = cursor.fetchall()
    except:
        if cnx:
            print("there was a problem with selecting")

    finally:
        if cnx:
            cnx.close()
            return range_data


def selector_to_date(year_, month_, day_):
    date_ = datetime(int(year_), int(month_), int(day_))
    return date_


def find_moon_rise_set(date_):
    suth = ephem.Observer()

    suth.date = date_

    suth.lon = str(20.810694444444444)
    suth.lat = str(-32.37686111111111)
    suth.elev = 1460
    beg_twilight = suth.next_rising(ephem.Moon(), use_center=True)  # Begin civil twilight
    end_twilight = suth.next_setting(ephem.Moon(), use_center=True)  # End civil twilight
    if end_twilight < beg_twilight:
        beg_twilight = suth.previous_rising(ephem.Moon(), use_center=True)
    rise_set = [beg_twilight, end_twilight]
    return rise_set


'''
    Ckeckbox List
'''
checkbox_list = [[0, 1], [0, 1, 2, 3, 4], [0]]
range_checkbox_list = [[0, 1], [0], [0]]
# ========================= Checkbox List End ====================================

'''
    Selectors
'''
dat = datetime.now() - timedelta(days=1)
dat_ = dat - timedelta(days=30)
y = ['2015', '2016']
m = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
day31 = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12',
             '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24',
             '25', '26', '27', '28', '29', '30', '31']
day30 = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12',
             '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24',
             '25', '26', '27', '28', '29', '30']
day29 = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12',
             '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24',
             '25', '26', '27', '28', '29']
day28 = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12',
             '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24',
             '25', '26', '27', '28']
fail = False
if str(dat)[:4] not in y:
    y.append(str(dat)[:4])

year_ = Select(title="Year:", value=str(dat)[:4], options=y, width=15)
month_ = Select(title="Month:", value=str(dat)[5:7], options=m, width=10)
day_ = Select(title="Day:", value=str(dat)[8:10], width=10)

range_year_min = Select(title="Year:", value=str(dat_)[:4], options=y, width=15)
range_month_min = Select(title="Month:", value=str(dat_)[5:7], width=10, options=m)
range_day_min = Select(title="Day:", value=str(dat_)[8:10], width=10)
range_year_max = Select(title="Year:", value=str(dat)[:4], options=y, width=15)
range_month_max = Select(title="Month:", value=str(dat)[5:7], width=10, options=m)
range_day_max = Select(title="Day:", value=str(dat)[8:10], width=10)


# ===================== Selectors End ==============================
'''
    Buttons
'''
# Buttons ========================================================================================================
submit_btn = Button(label="Submit", width=15)
week_btn = Button(label="Week", width=15)
range_submit_btn = Button(label="Submit", width=15)

# checkbox ========================================================================================================
telescope_group = CheckboxGroup(labels=["Sunrise", "Sunset"], active=[0, 1])
filter_group = CheckboxGroup(labels=["V", "B", "R", "I", "Exclude moon"], active=[0])

range_telescope_group = CheckboxGroup(labels=['Sunrise', 'Sunset'], active=[0, 1])
range_position_group = CheckboxGroup(labels=["Zenith", "North", "East", "West", "South"], active=[0])
range_filter_group = CheckboxGroup(labels=["V", "B", "R", "I", "Exclude moon"], active=[0])

# sliders =========================================================================================================
cloud_coverage = Slider(name='slider', start=0, end=100, value=30, step=1, title="Cloud coverage",
                        callback_policy='mouseup')
range_cloud_coverage = Slider(name='range_slider', start=0, end=100, value=30, step=1, title="Cloud coverage",
                              callback_policy='mouseup')

# Dev =============================================================================================================
telescope_div = Div(text=""" <div class="head-text" ><span >Telescope </span></div>""",  width=60, height=30)
filter_div = Div(text=""" <div class="head-text" ><span >Filter </span></div>""", width=60, height=30)

range_telescope_div = Div(text="""<div class="head-text" ><span >Telescope </span></div>""", width=60, height=30)
range_position_div = Div(text="""<div class="head-text" ><span >Position </span></div>""", width=60, height=30)
range_filter_div = Div(text="""<div class="head-text" ><span >Filter </span></div>""", width=60, height=30)

start_div = Div(text="""<div class="lead-text" ><span >Night Of: </span></div>""", width=140, height=40)

range_start_div = Div(text="""<div class = "lead-text-rng"><span>Start Date: </span></div>""", width=150, height=40)
range_end_div = Div(text=""" <div class = "lead-text-rng"><span>End Date: </span></div>""", width=150, height=50)
# ===================== Selectors End ==============================
'''
    DATA SOURCE
'''
data_source = [[[], [], [], [], []], [[], [], [], [], []]]
span_source = [[[], [], [], [], []], [[], [], [], [], []]]
for t in range(2):
    for p in range(5):
        for f in range(4):
            data_source[t][p].append(ColumnDataSource(data=dict(x=[], y=[], alpha=[], h_date=[], error=[],
                                                                telescope=[], filter=[])))
            span_source[t][p].append(ColumnDataSource(data=dict(x=[], h_date=[], y=[], coverage=[], telescope=[],
                                                                filter=[])))

ext_source = [[], []]
ext_span_source = [[], []]
for et in range(2):
    for ef in range(4):
        ext_source[et].append(ColumnDataSource(data=dict(x=[], y=[], alpha=[], h_date=[], error=[],
                                                         telescope=[], filter=[])))
        ext_span_source[et].append(ColumnDataSource(data=dict(x=[], h_date=[], y=[], coverage=[],
                                                              telescope=[], filter=[])))

range_source = [[[], [], [], [], []], [[], [], [], [], []]]
range_span_source = [[[], [], [], [], []], [[], [], [], [], []]]


for t in range(2):
    for p in range(5):
        for fr in range(4):
            range_source[t][p].append(ColumnDataSource(data=dict(x=[], y=[], h_date=[], telescope=[], filter=[],
                                                                 error=[], position=[])))
            range_span_source[t][p].append(ColumnDataSource(data=dict(x=[], h_date=[], y=[], telescope=[],
                                                                      filter=[], error=[], position=[])))

source = ColumnDataSource(data=dict(value=[30]))
d_source = ColumnDataSource(data=dict(value=[30]))
# ===================== Data Source End ==============================

'''
    Plots
'''

ext_hover = HoverTool(
    tooltips="""
            <div>
                <div>
                    <span style="font-size: 17px; font-weight: bold;">@h_date</span>
                </div>
                <div>
                    <span style="font-size: 17px;">EXT: </span>
                    <span style="font-size: 17px; font-weight: bold;">@y </span>
                    <span style="font-size: 17px; color: #966;">  [error: </span>
                    <span style="font-size: 17px; color: #966;"> @error]</span>
                </div>
                <div>
                    <span style="font-size: 18px; font-weight: bold;">@telescope</span>
                    <span style="font-size: 17px; color: #669; font-weight: bold;"> @filter </span>
                </div>
            </div>
            """
)

tool_list = "pan,reset,save,wheel_zoom, box_zoom"
range_hover = HoverTool(
    tooltips="""
        <div>
            <div>
                <span style="font-size: 15px; font-weight: bold;">@h_date</span>
            </div>
            <div>
                <span style="font-size: 15px; font-weight: bold;">SB: </span>
                <span style="font-size: 15px;">@y </span>
            </div>
            <div>
                <span style="font-size: 15px; font-weight: bold;">Average Error: </span>
                <span style="font-size: 15px; color: #966;">@error</span>
            </div>
            <div>
                <span style="font-size: 15px; color: #969;">@telescope</span>
                <span style="font-size: 15px; color: #696;">@filter</span>
            </div>
            <div>
                <span style="font-size: 15px; font-weight: bold;">Position: </span>
                <span style="font-size: 15px; color: #669;">@position</span>
            </div>

        </div>
        """
)
plot = []
hover = [0, 1, 2, 3, 4]
annotations = [[], [], [], [], [], [], []]

for i in range(5):
    hover[i] = HoverTool(
        tooltips="""
            <div>
                <div>
                    <span style="font-size: 17px; font-weight: bold;">@h_date</span>
                </div>
                <div>
                    <span style="font-size: 17px;">SB: </span>
                    <span style="font-size: 17px; font-weight: bold;">@y </span>
                    <span style="font-size: 17px; color: #966;">  [error: </span>
                    <span style="font-size: 17px; color: #966;"> @error]</span>
                </div>
                <div>
                    <span style="font-size: 18px; font-weight: bold;">@telescope</span>
                    <span style="font-size: 17px; color: #669; font-weight: bold;"> @filter </span>
                </div>
            </div>
            """
    )
    tit_ = find_tittle(i)
    plt = figure(title=tit_,
                 toolbar_location='above',
                 tools=[tool_list],
                 x_axis_type="datetime",
                 background_fill_alpha=0.09)
    plot.append(plt)
    plot[i].xaxis.major_label_orientation = pi / 4
    plot[i].ygrid.grid_line_color = None
    plot[i].add_tools(hover[i])
    plot[i].title.text_font_size = "25px"
    plot[i].title.align = "center"
    plot[i].title.text_color = "navy"
    plot[i].border_fill_color = "#f4f4f4"
    plot[i].min_border = 30

ext_plot = figure(title="Extinctions",
                  tools=[tool_list, ext_hover],
                  x_axis_type="datetime",
                  background_fill_alpha=0.09)
ext_plot.xaxis.major_label_orientation = pi / 4
ext_plot.ygrid.grid_line_color = None
ext_plot.title.text_font_size = "25px"
ext_plot.title.align = "center"
ext_plot.title.text_color = "navy"
ext_plot.border_fill_color = '#f4f4f4'
ext_plot.min_border = 30


range_plot = figure(plot_height=500, plot_width=1100,
                    title="Range",
                    tools=[tool_list, range_hover],
                    x_axis_type="datetime",
                    background_fill_alpha=0.09)
range_plot.xgrid.grid_line_color = None
range_plot.title.text_font_size = "25px"
range_plot.title.align = "center"
range_plot.title.text_color = "navy"
range_plot.border_fill_color = "#f4f4f4"
range_plot.min_border = 30
range_plot.toolbar_location = 'above'
range_plot.xaxis.major_label_orientation = pi / 4

for i in range(6):
    for d in range(10):
        annotations[i].append(BoxAnnotation(fill_color='yellow'))
        if i != 5:
            plot[i].renderers.extend([annotations[i][d]])
        else:
            ext_plot.renderers.extend([annotations[i][d]])


def msg_plot():
    global d_label, r_label, r_message_plot, message_plot
    r_message_plot = figure(plot_width=450, plot_height=50, title=None)
    r_message_plot.axis.visible = False
    r_message_plot.grid.grid_line_color = None
    r_message_plot.toolbar_location = None
    r_label = Label(x=1, y=1, y_units='screen', x_offset=10, y_offset=10, text=' ', text_font_size='30px')
    r_message_plot.add_layout(r_label)
    r_message_plot.circle(x=[1, 5], y=[1, 5], line_width=3, alpha=0)
    r_message_plot.border_fill_color = "#fafafa"
    r_message_plot.background_fill_color = "#fafafa"

    message_plot = figure(plot_width=450, plot_height=50, title=None)
    message_plot.axis.visible = False
    message_plot.grid.grid_line_color = None
    message_plot.toolbar_location = None
    d_label = Label(x=1, y=1, y_units='screen', x_offset=10, y_offset=10, text=' ', text_font_size='30px')
    message_plot.add_layout(d_label)
    message_plot.circle(x=[1, 5], y=[1, 5], line_width=3, alpha=0)
    message_plot.border_fill_color = "#fafafa"
    message_plot.background_fill_color = "#fafafa"


msg_plot()
# ===================== Plots End ==============================

'''
    Initial load of DATA
'''
date_ = selector_to_date(year_.value, month_.value, day_.value)

data = read_database(date_, 1)
ext_data = read_extinction_database(date_, 1)
range_data = read_range_database([range_year_min.value, range_month_min.value, range_day_min.value],
                                    [range_year_max.value, range_month_max.value, range_day_max.value])

# ===================== Data Load End ===================================


def set_data_source(date_, sb_, cc_, h_date, err_, tele_, fil_, t, p, f):
    global data_source
    data_source[t][p][f].data['x'] = date_
    data_source[t][p][f].data['y'] = sb_
    data_source[t][p][f].data['coverage'] = cc_
    data_source[t][p][f].data['h_date'] = h_date
    data_source[t][p][f].data['error'] = err_
    data_source[t][p][f].data['telescope'] = tele_
    data_source[t][p][f].data['filter'] = fil_


def set_ext_source(date_, ext_, err_, cc_, h_date, tele_, fil_, t, f):
    global ext_source
    ext_source[t][f].data['x'] = date_
    ext_source[t][f].data['y'] = ext_
    ext_source[t][f].data['error'] = err_
    ext_source[t][f].data['coverage'] = cc_
    ext_source[t][f].data['h_date'] = h_date
    ext_source[t][f].data['telescope'] = tele_
    ext_source[t][f].data['filter'] = fil_


def set_range_data_source(med_days, med_list, med_err, med_tel, med_pos, med_fil):
    global range_data, range_source, range_span_source

    for t in range(2):
        for p in range(5):
            for f in range(4):
                range_source[t][p][f].data['x'] = med_days[t][p][f]
                range_source[t][p][f].data['h_date'] = [str(d_)[:10] for d_ in med_days[t][p][f]]
                range_source[t][p][f].data['y'] = med_list[t][p][f]
                range_source[t][p][f].data['error'] = med_err[t][p][f]
                range_source[t][p][f].data['telescope'] = med_tel[t][p][f]
                range_source[t][p][f].data['position'] = med_pos[t][p][f]
                range_source[t][p][f].data['filter'] = med_fil[t][p][f]

                if t not in range_checkbox_list[0]:
                    empty_range(t, p, f)
                elif p not in range_checkbox_list[1]:
                    empty_range(t, p, f)
                elif f not in range_checkbox_list[2]:
                    empty_range(t, p, f)

                if len(med_days[t][p][f]) > 0 and len(med_list[t][p][f]) > 0:
                    range_span_source[t][p][f].data['x'] = [min(med_days[t][p][f]) - relativedelta(hours=1),
                                                            max(med_days[t][p][f]) - relativedelta(hours=1)]
                    range_span_source[t][p][f].data['h_date'] = append_twice("Median Line Statistics")

                    range_span_source[t][p][f].data['y'] = append_twice(np.median(med_list[t][p][f]))
                    range_span_source[t][p][f].data['error'] = append_twice(np.average(med_err[t][p][f]))
                    range_span_source[t][p][f].data['coverage'] = append_twice('Average: ' +
                                                                                  str(np.average(med_list[t][p][f])))
                    range_span_source[t][p][f].data['telescope'] = append_twice(
                        'Min: ' + str(min(med_list[t][p][f])))
                    range_span_source[t][p][f].data['filter'] = append_twice('Max: ' + str(max(med_list[t][p][f])))
                    range_span_source[t][p][f].data['position'] = append_twice(med_pos[t][p][f][0])
                else:
                    range_span_source[t][p][f].data['x'] = []
                    range_span_source[t][p][f].data['h_date'] = []

                    range_span_source[t][p][f].data['y'] = []
                    range_span_source[t][p][f].data['error'] = []
                    range_span_source[t][p][f].data['coverage'] = []
                    range_span_source[t][p][f].data['telescope'] = []
                    range_span_source[t][p][f].data['filter'] = []


def update_line_span():
    global data_source, ext_source
    for t in range(2):
        for p in range(5):
            for f in range(4):
                temp_list = []
                temp_err = []
                for y, a, e in zip(data_source[t][p][f].data['y'], data_source[t][p][f].data['alpha'],
                                   data_source[t][p][f].data['error']):
                    if a == 1:
                        temp_list.append(y)
                        temp_err.append(e)

                sday = [min(date_list[t][p][f]) - relativedelta(hours=1),
                        max(date_list[t][p][f]) + relativedelta(hours=1)] if len(date_list[t][p][f]) > 0 else []
                shd = append_twice("Median line statistics") if len(temp_list) > 0 else []
                smed = append_twice(np.median(temp_list)) if len(temp_list) > 0 else []
                savg = append_twice(np.average(temp_err)) if len(temp_list) > 0 else []
                scov = append_twice('Avg: ' + str(np.average(temp_list))) if len(temp_list) > 0 else []
                smin = append_twice('Min: ' + str(min(temp_list))) if len(temp_list) > 0 else []
                smax = append_twice('Max: ' + str(max(temp_list))) if len(temp_list) > 0 else []

                span_source[t][p][f].data['x'] = sday
                span_source[t][p][f].data['h_date'] = shd
                span_source[t][p][f].data['y'] = smed
                span_source[t][p][f].data['error'] = savg
                span_source[t][p][f].data['coverage'] = scov
                span_source[t][p][f].data['telescope'] = smin
                span_source[t][p][f].data['filter'] = smax

    for t in range(2):
        for f in range(4):
            temp_list = []
            temp_err = []
            for y, a, e, in zip(ext_source[t][f].data['y'], ext_source[t][f].data['alpha'],
                                ext_source[t][f].data['error']):
                if a == 1:
                    temp_list.append(y)
                    temp_err.append(e)

            sday = [min(date_list[t][p][f]) - relativedelta(hours=1),
                    max(date_list[t][p][f]) + relativedelta(hours=1)] if len(date_list[t][p][f]) > 0 else []
            shd = append_twice("Median line statistics") if len(temp_list) > 0 else []
            smed = append_twice(np.median(temp_list)) if len(temp_list) > 0 else []
            savg = append_twice(np.average(temp_err)) if len(temp_list) > 0 else []
            scov = append_twice('Avg: ' + str(np.average(temp_list))) if len(temp_list) > 0 else []
            smin = append_twice('Min: ' + str(min(temp_list))) if len(temp_list) > 0 else []
            smax = append_twice('Max: ' + str(max(temp_list))) if len(temp_list) > 0 else []

            ext_span_source[t][f].data['x'] = sday
            ext_span_source[t][f].data['h_date'] = shd
            ext_span_source[t][f].data['y'] = smed
            ext_span_source[t][f].data['error'] = savg
            ext_span_source[t][f].data['coverage'] = scov
            ext_span_source[t][f].data['telescope'] = smin
            ext_span_source[t][f].data['filter'] = smax


def slider_moved(attr, old, new):
    cc = d_source.data['value'][0]
    for t in range(2):
        for p in range(5):
            for f in range(4):
                if len(coverage_list[t][p][f]) > 0:
                    data_source[t][p][f].data['alpha'] = [1 if c <= cc else 0.1 for c in cc_list[t][p][f]]

    for et in range(2):
        for ef in range(4):
            if len(ext_coverage_list[et][ef]) > 0:
                ext_source[et][ef].data['alpha'] = [1 if c <= cc else 0.1 for c in ext_coverage_list[et][ef]]

    update_line_span()


def range_slider_moved(attr, old, new):
    global temp_sb
    cc = source.data['value'][0]
    temp_sb = [[[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]],
               [[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]]]
    temp_days = [[[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]],
                 [[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]]]
    temp_err = [[[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]],
                [[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]]]
    temp_tel = [[[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]],
                [[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]]]
    temp_pos = [[[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]],
                [[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]]]
    temp_fil = [[[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]],
                [[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]]]
    for y in range(len(range_data_list)):
        for t in range_checkbox_list[0]:
            for p in range_checkbox_list[1]:
                for f in range_checkbox_list[2]:
                    d = []
                    l = []
                    e = []
                    if f != 4:
                        for d_, s_, c_, m_, e_ in zip(range_days[y][t][p][f], range_data_list[y][t][p][f],
                                                      range_coverage_list[y][t][p][f], range_moon_list[y][t][p][f],
                                                      range_error_list[y][t][p][f]):
                            if 4 in range_checkbox_list[2]:
                                if m_ == 0:
                                    if c_ <= cc:
                                        d.append(d_)
                                        l.append(s_)
                                        e.append(e_)
                            else:
                                if c_ <= cc:
                                    d.append(d_)
                                    l.append(s_)
                                    e.append(e_)
                        if len(l) > 0:
                            temp_days[t][p][f].append(pd.to_datetime(d[0]))
                            temp_sb[t][p][f].append(np.median(l))
                            temp_err[t][p][f].append(np.average(e))
                            temp_tel[t][p][f].append(find_telescope_name(t))
                            temp_pos[t][p][f].append(find_position(p))
                            temp_fil[t][p][f].append(find_filter_name(f))

    r_label.set(text='Loading . . . .')
    set_range_data_source(temp_days, temp_sb, temp_err, temp_tel, temp_pos, temp_fil)
    r_label.set(text='Done ')
    time.sleep(1)
    r_label.set(text=' ')


def update_data_source():
    global data_source, ext_source, date_list, h_list, data_list, error_list, telescope_list, filter_list,\
        ext_date_list, ext_data_list, ext_error_list, ext_filter_list, ext_telescope_list, ext_h_list, checkbox_list,\
        coverage_list
    for t in range(2):
        for p in range(5):
            for f in range(4):
                if f != 4:
                    if t not in checkbox_list[0] or f not in checkbox_list[2]:
                        empty_source(t, p, f)
                    else:
                        cc_list[t][p][f] = coverage_list[t][p][f]
                        set_data_source(date_list[t][p][f], data_list[t][p][f], coverage_list[t][p][f], h_list[t][p][f],
                                   error_list[t][p][f], telescope_list[t][p][f], filter_list[t][p][f],
                                   t, p, f)

    for t in checkbox_list[0]:
        for f in checkbox_list[2]:
            if f != 4:
                set_ext_source(ext_date_list[t][f], ext_data_list[t][f], ext_error_list[t][f], ext_coverage_list[t][f],
                               ext_h_list[t][f], ext_telescope_list[t][f], ext_filter_list[t][f],
                               t, f)


def button_clicked():
    global data, ext_data
    is_data = False
    d_label.set(text='Loading . ')
    date_ = selector_to_date(year_.value, month_.value, day_.value)
    data = read_database(date_, 1)
    d_label.set(text='Loading . . ')
    ext_data = read_extinction_database(date_, 1)
    d_label.set(text='Loading . . .')
    create_list()
    d_label.set(text='Loading . . . .')
    update_data_source()
    d_label.set(text='Loading . . . . .')
    slider_moved(cloud_coverage, 0, 30)
    d_label.set(text='Done ')

    for t in range(2):
        for p in range(5):
            for f in range(4):
                if len(data_list[t][p][f]) > 0:
                    is_data = True
    if is_data:
        time.sleep(2)
        d_label.set(text=' ')
    else:
        d_label.set(text='Date has no data to display')


def week_button_clicked():
    global data, ext_data, data_list
    is_data = False
    d_label.set(text='Loading . ')
    date_ = selector_to_date(year_.value, month_.value, day_.value)
    data = read_database(date_, 7)
    d_label.set(text='Loading . . ')
    ext_data = read_extinction_database(date_, 7)
    d_label.set(text='Loading . . . ')
    create_list()
    update_data_source()
    d_label.set(text='Loading . ')
    slider_moved(cloud_coverage, 0, 30)
    d_label.set(text='Done ')

    for t in range(2):
        for p in range(5):
            for f in range(4):
                if len(data_list[t][p][f]) > 0:
                    is_data = True
    if is_data:
        time.sleep(2)
        d_label.set(text=' ')
    else:
        d_label.set(text='Date has no data to display')
    if fail:
        d_label.set(text=' Error on creating moon annotation', text_font_size='22px')


def range_button_clicked():
    global range_data, temp_sb
    is_data = False
    r_label.set(text='Loading . ', text_font_size='30px')
    if selector_to_date(range_year_min.value, range_month_min.value, range_day_min.value) > \
        selector_to_date(range_year_max.value, range_month_max.value, range_day_max.value):
        range_data = []
        create_range_list()
        r_label.set(text='Loading . . ')
        range_slider_moved(range_cloud_coverage, 0, 30)
        r_label.set(text='Fail')
        time.sleep(2)
        r_label.set(text_font_size='20px', text='Start date is larger than end date')
    else:
        range_data = read_range_database([range_year_min.value, range_month_min.value, range_day_min.value],
                                            [range_year_max.value, range_month_max.value, range_day_max.value])
        r_label.set(text='Loading . . ')
        create_range_list()
        r_label.set(text='Loading . . . ')
        range_slider_moved(range_cloud_coverage, 0, 30)
        r_label.set(text='Done')
        for t in range(2):
            for p in range(5):
                for f in range(4):
                    if len(temp_sb[t][p][f]) > 0:
                        is_data = True
        if is_data:
            time.sleep(2)
            r_label.set(text=' ')
        else:
            r_label.set(text_font_size='22px', text='Range has no data to display')


def month_changed(attr, old, new):
    global day31, day30, day29, day28

    if int(year_.value) % 4 == 0 and month_.value == '02':
        if int(day_.value) > 29:
            day_.set(options=day29, value='29')
        else:
            day_.set(options=day29)
    elif int(year_.value) % 4 != 0 and month_.value == '02':
        if int(day_.value) > 28:
            day_.set(options=day28, value='28')
        else:
            day_.set(options=day28)
    elif month_.value in ['04', '06', '09', '11']:
        if int(day_.value) > 30:
            day_.set(options=day30, value='30')
        else:
            day_.set(options=day30)
    else:
        day_.set(options=day31)


def range_month_min_changed(attr, old, new):
    global day31, day30, day29, day28

    if int(range_year_min.value) % 4 == 0 and range_month_min.value == '02':
        if int(range_day_min.value) > 29:
            range_day_min.set(options=day29, value='29')
        else:
            range_day_min.set(options=day29)
    elif int(range_year_min.value) % 4 != 0 and range_month_min.value == '02':
        if int(range_day_min.value) > 28:
            range_day_min.set(options=day28, value='28')
        else:
            range_day_min.set(options=day28)
    elif range_month_min.value in ['04', '06', '09', '11']:
        if int(range_day_min.value) > 30:
            range_day_min.set(options=day30, value='30')
        else:
            range_day_min.set(options=day30)
    else:
        range_day_min.set(options=day31)


def range_month_max_changed(attr, old, new):
    global day31, day30, day29, day28

    if int(range_year_max.value) % 4 == 0 and range_month_max.value == '02':
        if int(range_day_max.value) > 29:
            range_day_max.set(options=day29, value='29')
        else:
            range_day_max.set(options=day29)
    elif int(range_year_max.value) % 4 != 0 and range_month_max.value == '02':
        if int(range_day_max.value) > 28:
            range_day_max.set(options=day28, value='28')
        else:
            range_day_max.set(options=day28)
    elif range_month_max.value in ['04', '06', '09', '11']:
        if int(range_day_max.value) > 30:
            range_day_max.set(options=day30, value='30')
        else:
            range_day_max.set(options=day30)
    else:
        range_day_max.set(options=day31)


def create_and_set_annotations(min_day):
    global annotations, fail
    moon_up_date = [min_day + timedelta(d) for d in range(10)]

    for i in range(6):
        for d in range(8):
            annotations[i][d].fill_alpha = 0
    d = 0
    for day in moon_up_date:
        for i in range(6):
            r_and_s = find_moon_rise_set(str(day))
            annotations[i][d].set(left=((r_and_s[0]).datetime() + timedelta(hours=2, minutes=5)).timestamp() * 1000,
                                   right=((r_and_s[1]).datetime() + timedelta(hours=2, minutes=5)).timestamp() * 1000)
            annotations[i][d].fill_alpha = 0.1
        d += 1


def create_list():
    global date_list, h_list, data_list, error_list, coverage_list, moon_list,  telescope_list, filter_list, cc_list,\
        data

    date_list = [[[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]],
                 [[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]]]

    h_list = [[[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]],
              [[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]]]

    data_list = [[[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]],
                 [[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]]]
    error_list = [[[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]],
                  [[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]]]
    coverage_list = [[[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]],
                     [[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]]]
    cc_list = [[[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]],
                     [[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]]]
    moon_list = [[[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]],
                 [[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]]]
    telescope_list = [[[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]],
                 [[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]]]
    filter_list = [[[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]],
                 [[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]]]

    '''
    date_list = append_twice([[[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]],
                     [[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]]])

    h_list = append_twice([[[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]],
                  [[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]]])

    data_list = append_twice([[[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]],
                     [[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]]])
    error_list = append_twice([[[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]],
                      [[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]]])
    coverage_list = append_twice([[[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]],
                         [[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]]])
    cc_list = append_twice([[[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]],
                   [[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]]])
    moon_list = append_twice([[[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]],
                     [[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]]])
    telescope_list = append_twice([[[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]],
                          [[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]]])
    filter_list = append_twice([[[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]],
                       [[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]]])
    '''

    box_ano = []
    for d in data:
        t = d[4]
        p = d[6]
        f = find_filter_number(d[5])
        date_list[t][p][f].append(pd.to_datetime(d[0]))
        data_list[t][p][f].append(d[1])
        coverage_list[t][p][f].append(d[2])
        moon_list[t][p][f].append(d[3])
        error_list[t][p][f].append(d[7])
        telescope_list[t][p][f].append(find_telescope_name(t))
        filter_list[t][p][f].append(d[5])
        h_list[t][p][f].append(str(d[0]))

        if d[3] == 1:
            box_ano.append((d[0]))

    d_label.set(text='Loading . . . .')
    create_ext_list()
    d_label.set(text='Loading . . . . . ')
    if len(box_ano) > 0:
        create_and_set_annotations(min(box_ano) - relativedelta(days=1))


def create_ext_list():
    global ext_date_list, ext_data_list, ext_error_list, ext_coverage_list, ext_filter_list, \
        ext_telescope_list, ext_h_list, ext_data

    ext_date_list = [[[], [], [], []], [[], [], [], []]]
    ext_data_list = [[[], [], [], []], [[], [], [], []]]
    ext_error_list = [[[], [], [], []], [[], [], [], []]]
    ext_coverage_list = [[[], [], [], []], [[], [], [], []]]
    ext_telescope_list = [[[], [], [], []], [[], [], [], []]]
    ext_filter_list = [[[], [], [], []], [[], [], [], []]]
    ext_h_list = [[[], [], [], []], [[], [], [], []]]

    def find_ext_cc(date_, t, f):
        cc_ = 200
        p = 0
        for sdate_, cov_ in zip(date_list[t][p][f], coverage_list[t][p][f]):
            if sdate_ - relativedelta(minutes=1) <= date_ <= sdate_ + relativedelta(minutes=1):
                return cov_
        return cc_
    for e in ext_data:
        # DATE_TIME[0], EXTINCTION[1], EXT_ERROR[2], FILTER_BAND[3], TELESCOPE[4], CLOUD_COVERAGE[5]
        t = e[4]
        f = find_filter_number(e[3])

        ext_date_list[t][f].append(pd.to_datetime(e[0]))
        ext_data_list[t][f].append(e[1])
        ext_error_list[t][f].append(e[2])
        ext_telescope_list[t][f].append(find_telescope_name(t))
        ext_filter_list[t][f].append(e[3])
        ext_h_list[t][f].append(str(e[0]))

        ext_coverage_list[t][f].append(find_ext_cc(pd.to_datetime(e[0]), t, f))


def create_range_list():
    global range_days, range_data_list, range_error_list, range_coverage_list, range_moon_list, range_date

    range_days = []
    range_date = [[[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]],
                  [[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]]]
    range_error_list = []
    range_data_list = []
    range_coverage_list = []
    range_moon_list = []

    def add_day_list():
        range_days.append([[[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]],
                           [[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]]])
        range_data_list.append([[[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []],
                                 [[], [], [], []]],
                                [[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []],
                                 [[], [], [], []]]])
        range_error_list.append([[[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []],
                                  [[], [], [], []]],
                                 [[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []],
                                  [[], [], [], []]]])
        range_coverage_list.append([[[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []],
                                     [[], [], [], []]],
                                    [[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []],
                                     [[], [], [], []]]])
        range_moon_list.append([[[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [],
                                                                                        []], [[], [], [], []]],
                                [[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []],
                                 [[], [], [], []]]])

    for d in range_data:
        t = d[4]
        p = d[6]
        f = find_filter_number(d[5])

        date_ = find_range_date(d[0])

        if date_ not in range_date[t][p][f]:
            range_date[t][p][f].append(date_)
            add_day_list()

        nd = find_date_index(date_, range_date[t][p][f])
        range_days[nd][t][p][f].append(date_)
        range_data_list[nd][t][p][f].append(d[1])
        range_error_list[nd][t][p][f].append(d[7])
        range_coverage_list[nd][t][p][f].append(d[2])
        range_moon_list[nd][t][p][f].append(d[3])


def update_checkbox_list(list_, ind_):
    global checkbox_list
    checkbox_list[ind_] = list_
    update_data_source()
    slider_moved(0, 0, 0)


def update_range_checkbox_list(list_, ind_):
    global range_checkbox_list
    range_checkbox_list[ind_] = list_
    range_slider_moved(0, 0, 0)

"""
    initiate definitions
"""


def initiate():
    is_data = False
    create_list()
    create_range_list()

    update_data_source()

    slider_moved(cloud_coverage, 0, 30)
    range_slider_moved(range_cloud_coverage, 0, 30)
    for t in range(2):
        for p in range(5):
            for f in range(4):
                if len(data_list[t][p][f]) > 0:
                    is_data = True
    if is_data:
        time.sleep(2)
        d_label.set(text=' ')
    else:
        d_label.set(text='Date has no data to display')
    month_changed(month_, 0, 0)
    range_month_min_changed(month_, 0, 0)
    range_month_max_changed(month_, 0, 0)
    time.sleep(2)
    d_label.set(text=' ')
    r_label.set(text=' ')
    if fail:
        d_label.set(text=' Error on creating moon annotation', text_font_size='22px')
initiate()
# ==============================================================


for t in range(2):
    for p in range(5):
        for f in range(4):
            col_ = set_colour(t, f)
            if t == 0:
                plot[p].circle(source=data_source[t][p][f], x='x', y='y', line_width=2, color=col_, alpha='alpha')
            if t == 1:
                plot[p].diamond(source=data_source[t][p][f], x='x', y='y', line_width=2, color=col_, alpha='alpha')
            plot[p].line(source=span_source[t][p][f], x='x', y='y', line_width=0.1, color=col_)

for t in range(2):
    for f in range(4):
        col_ = set_colour(t, f)

        if t == 0:
            ext_plot.circle(source=ext_source[t][f], x='x', y='y', line_width=2, color=col_, alpha='alpha')
        if t == 1:
            ext_plot.diamond(source=ext_source[t][f], x='x', y='y', line_width=2, color=col_, alpha='alpha')

        ext_plot.line(source=ext_span_source[t][f], x='x', y='y', line_width=0.1, color=col_)

for t in range(2):
    tel_ = 'Sunrise' if t == 0 else 'Sunset'
    for p in range(5):
        for f in range(4):
            filt_ = 'V' if f == 0 else 'B' if f == 1 else 'R' if f == 2 else 'I'
            pos_ = 'Zenith' if p == 0 else 'North' if p == 1 else 'East' if p == 2 else 'West' if p == 3 else 'South'
            col_ = set_colour_range(t, p, f)
            if t == 0:
                range_plot.line(source=range_source[t][p][f], x='x', y='y', line_width=3,
                                line_color=col_, legend=tel_ + ' ' + pos_)
            if t == 1:
                range_plot.line(source=range_source[t][p][f], x='x', y='y', line_width=2, line_color=col_,
                                line_dash=[15, 2], legend=tel_ + ' ' + pos_)

            if f == 0:
                range_plot.circle(source=range_source[t][p][f], x='x', y='y', line_width=1, color=col_,
                                  fill_color = None, legend=' filter ' + filt_)

            if f == 1:
                range_plot.triangle(source=range_source[t][p][f], x='x', y='y', line_width=3, color=col_,
                                    legend=' filter ' + filt_)
            if f == 2:
                range_plot.diamond(source=range_source[t][p][f], x='x', y='y', line_width=3, color=col_,
                                   legend=' filter ' + filt_)
            if f == 3:
                range_plot.square(source=range_source[t][p][f], x='x', y='y', line_width=1,  color=col_,
                                  fill_color=None, legend=' filter ' + filt_)
            range_plot.line(source=range_span_source[t][p][f], x='x', y='y', line_width=0.1, line_dash=[6, 6],
                            color=col_)

            range_plot.legend.location = 'bottom_right'
            range_plot.legend.background_fill_alpha = 0.4
# ==========Plots===================================================================================================

"""
    Interactions definitions
"""
source.on_change('data', range_slider_moved)
range_cloud_coverage.callback = CustomJS(args=dict(source=source), code="""
        source.data = { value: [cb_obj.value] }
    """)

d_source.on_change('data', slider_moved)
cloud_coverage.callback = CustomJS(args=dict(source=d_source), code="""
        source.data = { value: [cb_obj.value] }
    """)

submit_btn.on_click(button_clicked)
week_btn.on_click(week_button_clicked)
range_submit_btn.on_click(range_button_clicked)

filter_group.on_click(lambda selected_indices: update_checkbox_list(selected_indices, 2))
telescope_group.on_click(lambda selected_tele: update_checkbox_list(selected_tele, 0))

range_filter_group.on_click(lambda selected_indices: update_range_checkbox_list(selected_indices, 2))
range_position_group.on_click(lambda selected_indices: update_range_checkbox_list(selected_indices, 1))
range_telescope_group.on_click(lambda selected_tele: update_range_checkbox_list(selected_tele, 0))

month_.on_change('value', month_changed)
range_month_min.on_change('value', range_month_min_changed)
range_month_max.on_change('value', range_month_max_changed)
# =======================================================================================


# ==========Widget Box==============================================================================================
inputs = widgetbox(cloud_coverage, filter_div, filter_group, telescope_div, telescope_group,
                   width=310, height=180,
                   sizing_mode='scale_both')
range_inputs = widgetbox(range_cloud_coverage, range_telescope_div, range_telescope_group, range_position_div,
                         range_position_group,
                         range_filter_div, range_filter_group)
wid_year = widgetbox(year_, week_btn, width=100, height=60)
wid_month = widgetbox(month_, width=90, height=60)
wid_day = widgetbox(day_, submit_btn, width=90, height=60)

dev_col = column( start_div)
r_dev_col = column(range_start_div, range_end_div)

wid_year_r = widgetbox(range_year_min, range_year_max, width=90, height=50)
wid_month_r = widgetbox(range_month_min, range_month_max, width=80, height=50)
wid_day_r = widgetbox(range_day_min, range_day_max, range_submit_btn, width=80, height=50)
# ==========Widget Box==============================================================================================
#
# ==========View====================================================================================================
"""
date_tab = column(row(gridplot([wid_year, wid_month, wid_day, ], ncols=3, plot_width=105),
                      message_plot),
                  row())
"""
date_tab = layout([[dev_col, wid_year, wid_month, wid_day, message_plot],
                   [gridplot(plot[0], plot[1],
                             plot[2], plot[3],
                             plot[4], ext_plot,
                             ncols=2, spacing=150,
                             plot_width=570, plot_height=250),
                    inputs]])


range_tab = layout([[r_dev_col, wid_year_r, wid_month_r, wid_day_r, r_message_plot], [range_plot, range_inputs]])

tab1 = Panel(child=date_tab, title="Date", sizing_mode="scale_both")
tab2 = Panel(child=range_tab, title="Date range", sizing_mode="scale_both")
tabs = Tabs(tabs=[tab1, tab2])
# ==========View====================================================================================================
#
# ==========Serve===================================================================================================
curdoc().add_root(tabs)
curdoc().title = "SkyBrightness"
