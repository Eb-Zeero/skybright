import time
from datetime import datetime, timedelta
from math import pi

import numpy as np
import pandas as pd
from bokeh.io import curdoc
from bokeh.layouts import column, widgetbox, layout, gridplot
from bokeh.models import HoverTool, ColumnDataSource, Select, Button, BoxAnnotation, Label, Legend
from bokeh.models.callbacks import CustomJS
from bokeh.models.widgets import Slider, Div, CheckboxGroup, Tabs, Panel
from bokeh.plotting import figure
from dateutil.relativedelta import relativedelta
import pymysql
import os
import ephem
import smtplib


def empty_source(to, po, fo):
    """
    Set data in the data_source to empty if the respective checkbox id not selected

    :param to: 0 or 1 for telescope,  sunrise or sunset respectively
    :param po: 0 to 4 for positions, Zenith south, east, north and west respectively
    :param fo: 0 to 3 for  filters, V, B, R and I respectively
    :return: None
    """
    data_source[to][po][fo].data['x'] = []
    data_source[to][po][fo].data['h_date'] = []
    data_source[to][po][fo].data['y'] = []
    data_source[to][po][fo].data['error'] = []
    data_source[to][po][fo].data['filter'] = []
    data_source[to][po][fo].data['telescope'] = []


def empty_range(to, po, fo):
    """
    Set data in the range_source to empty if the respective checkbox id not selected

    :param to: 0 or 1 for telescope,  sunrise or sunset respectively
    :param po: 0 to 4 for positions, Zenith south, east, north and west respectively
    :param fo: 0 to 3 for  filters, V, B, R and I respectively
    :return: None
    """
    range_source[to][po][fo].data['x'] = []
    range_source[to][po][fo].data['h_date'] = []
    range_source[to][po][fo].data['y'] = []
    range_source[to][po][fo].data['error'] = []
    range_source[to][po][fo].data['filter'] = []
    range_source[to][po][fo].data['position'] = []
    range_source[to][po][fo].data['telescope'] = []
    range_source[to][po][fo].data['count'] = []


def set_config():
    if __name__.startswith("bk_script"):
        try:
            """
            configuring environment variable for deployment and developing
            """
            env_file = "/home/deploy/skybright/.env"
            #
            env_var = []

            us, pa, ho, da = "", "", "", ""
            with open(env_file) as env:
                for line in env:
                    env_var.append([str(n) for n in line.strip().split('=')])
            for pair in env_var:
                try:
                    key, value = pair[0], pair[1]
                    if key == "SKY_DATABASE_USER":
                        us = value
                    if key == "SKY_DATABASE_PASSWORD":
                        pa = value
                    if key == "SKY_DATABASE_HOST":
                        ho = value
                    if key == "SKY_DATABASE_NAME":
                        da = value
                except IndexError:
                    print("A line in the file doesn't have enough entries.")

            config = {
                'user': us,
                'passwd': pa,
                'host': ho,
                'db': da,
            }
        except:
            config = {
                'user': os.environ['SKY_DATABASE_USER'],
                'passwd': os.environ['SKY_DATABASE_PASSWORD'],
                'host': os.environ['SKY_DATABASE_HOST'],
                'db': os.environ['SKY_DATABASE_NAME']
            }
    else:
        config = {
            'user': os.environ['LOCAL_DB_USER'],
            'password': os.environ['LOCAL_DB_PASS'],
            'host': os.environ['TEST_HOST'],
            'database': os.environ['TEST_DB'],
        }
    return config


def find_filter_number(char_):
    """
     find the checkbox index per given filter character
    :param char_: filter character
    :return: checkbox index none otherwise
    """
    num_ = 0 if char_ == 'V' else 1 if char_ == 'B' else 2 if char_ == 'R' else 3 if char_ == 'I' else -1
    return num_


def find_filter_name(num_):
    """
    find filter per checkbox index given
    :param num_: checkbox index
    :return: filter character  none otherwise
    """
    char_ = 'V' if num_ == 0 else 'B' if num_ == 1 else 'R' if num_ == 2 else 'I' if num_ == 3 else None
    return char_


def find_position(po):
    """

    :param po: position index
    :return: direction faced by the telescope none otherwise
    """
    return 'Zenith' if po == 0 else 'South' if po == 1 else 'East' if po == 2 else 'North' if po == 3 else 'West' \
        if po == 4 else None


def find_tittle(num_):
    """

    :param num_: checkbox index
    :return: direction faced in word, none otherwise
    """
    return 'Zenith' if num_ == 0 else 'South' if num_ == 1 else 'East' if num_ == 2 else 'North' if num_ == 3 \
        else 'West' if num_ == 4 else None


def find_telescope_name(tel):
    """

    :param tel: telescope checkbox index
    :return: telescope name None otherwise
    """
    return 'Sunrise' if tel == 0 else 'Sunset' if tel == 1 else None


def set_colour(tel, fil_):
    """
    Set a constant color for different filter and telescope
    :param tel: telescope checkbox index
    :param fil_: filter checkbox index
    :return: colour Black otherwise
    """
    co = 'black'
    if tel == 0:
        co = 'brown' if fil_ == 0 else 'blue' if fil_ == 1 else '#c615f2' if fil_ == 2 else 'green'
    if tel == 1:
        co = '#f2155f' if fil_ == 0 else '#07a9bf' if fil_ == 1 else '#f4ac02' if fil_ == 2 else '#02ce24'
    return co


def set_colour_range(tel, ps_, fil_):
    """
    Set a constant color for different filter and telescope
    :param ps_:
    :param tel: telescope checkbox index
    :param fil_: filter checkbox index
    :return: colour Black otherwise
    """
    clr_ = 'black'
    if tel == 0:
        if fil_ == 0:
            clr_ = '#56412b' if ps_ == 0 else '#4d4960' if ps_ == 1 else '#f20000' if ps_ == 2 else \
                '#5df4d8' if ps_ == 3 else '#ff00fd'
        if fil_ == 1:
            clr_ = '#8c745c' if ps_ == 0 else '#6f65a3' if ps_ == 1 else '#e07676' if ps_ == 2 else \
                '#076d05' if ps_ == 3 else '#dd6cdd'
        if fil_ == 2:
                clr_ = '#dd9144' if ps_ == 0 else '#3c2f7f' if ps_ == 1 else '#8c2b2b' if ps_ == 2 else \
                    '#4a6d49' if ps_ == 3 else '#a041a0'
        if fil_ == 3:
            clr_ = '#f47a00' if ps_ == 0 else '#290dba' if ps_ == 1 else '#ff9999' if ps_ == 2 else \
                '#4ed34c' if ps_ == 3 else '#590d59'
    if tel == 1:
        if fil_ == 0:
            clr_ = 'gold' if ps_ == 0 else 'skyblue' if ps_ == 1 else 'Orange' if ps_ == 2 else \
                '#1ff14d' if ps_ == 3 else '#8000ff'
        if fil_ == 1:
            clr_ = '#ff7199' if ps_ == 0 else '#1b8196' if ps_ == 1 else '#8e3d07' if ps_ == 2 else \
                '#000000' if ps_ == 3 else '#984be5'
        if fil_ == 2:
            clr_ = '#e0ce59' if ps_ == 0 else '#74a8b2' if ps_ == 1 else '#d9bc0f' if ps_ == 2 else \
                '#10967d' if ps_ == 3 else '#7b6096'
        if fil_ == 3:
            clr_ = '#96861b' if ps_ == 0 else '#007fc4' if ps_ == 1 else '#9b368a' if ps_ == 2 else \
                '#961082' if ps_ == 3 else '#522160'
    return clr_


def find_range_date(dte_):
    """
    Set date between 00:00:00 and 12:00:00 belong to the date before
    :param dte_: datetime
    :return: date
    """
    if '00:00:00' <= str(dte_)[11:] < '13:00:00':
        return (dte_ - timedelta(days=1)).date()
    elif '13:00:00' <= str(dte_)[11:] <= '23:59:59':
        return dte_.date()
    else:
        return dte_.date()


def find_value_index(value_, list_):
    """
    find the index of the given value in a given list
    :param value_: target value
    :param list_: list to check a value index
    :return: index of value in list -1 otherwise
    """
    if value_ in list_:
        return list_.index(value_)
    else:
        return -1


def append_twice(val_):
    """
    create a list of the given value with with element itself twice
    :param val_: anything that need to be double and returned in a list
    :return: list of value of length 2
    """
    return [val_, val_]


def read_database(dte_, num):
    """
    read the database table SkyBrightness
    :param dte_: date data needed
    :param num: number of days 1 or 7 including 7 days before date with date included
    :return: data from the query
    """
    config = set_config()
    data_ = []
    date_n = dte_ + timedelta(days=1)
    if num != 1:
        dte_ = date_n - timedelta(days=num)
    sql = (
                    "SELECT DATE_TIME, SKYBRIGHTNESS, CLOUD_COVERAGE, MOON, TELESCOPE, FILTER_BAND, POSX, SB_ERROR "
                    "FROM SkyBrightness "
                    "WHERE DATE_TIME > '%s-%s-%s 12:00:00' "
                    "AND DATE_TIME < '%s-%s-%s 12:00:00' "
                    "AND SKYBRIGHTNESS != 0 "
                ) % (str(dte_)[0:4], str(dte_)[5:7], str(dte_)[8:10],
                     str(date_n)[0:4], str(date_n)[5:7], str(date_n)[8:10])

    cnx = pymysql.connect(**config)
    try:
        cursor = cnx.cursor()
        cursor.execute(sql)
        data_ = cursor.fetchall()
    except:
        if cnx:
            pass

    finally:
        if cnx:
            cnx.close()
        return data_


def read_range_database(min_date, max_date):
    """
    read the database table SkyBrightness
    :param min_date: start date (after date noon), a list of int year, month and day
    :param max_date: end date (before date noon ), a list of int year, month and day
    :return: data from the query
    """
    config = set_config()
    range_dta = []
    select_sb = (
                    "SELECT DATE_TIME, SKYBRIGHTNESS, CLOUD_COVERAGE, MOON, TELESCOPE, FILTER_BAND, POSX, SB_ERROR  "
                    "FROM SkyBrightness "
                    "WHERE DATE_TIME > '%s-%s-%s 12:00:00' "
                    "AND DATE_TIME < '%s-%s-%s 12:00:00' "
                    "AND SKYBRIGHTNESS != 0 "
                ) % (min_date[0], min_date[1], min_date[2], max_date[0], max_date[1], max_date[2])

    cnx = pymysql.connect(**config)
    try:
        cursor = cnx.cursor()
        cursor.execute(select_sb)
        range_dta = cursor.fetchall()
    except:
        if cnx:
            pass

    finally:
        if cnx:
            cnx.close()
            return range_dta


def selector_to_date(yr_, mth_, dy_):
    """
    covert the string from selector to datetime
    :param yr_: year
    :param mth_: month
    :param dy_: day
    :return: datetime.datetime(year, month, day)
    """
    return datetime(int(yr_), int(mth_), int(dy_))


def find_moon_rise_set(dte_):
    """
    Use pyephem to find if moon was up on the given time and date
    :param dte_: string of datetime
    :return: list(moon rise and and moon set) respectively
    """
    suth = ephem.Observer()

    suth.date = dte_

    suth.lon = str(20.810694444444444)
    suth.lat = str(-32.37686111111111)
    suth.elev = 1460
    beg_twilight = suth.next_rising(ephem.Moon(), use_center=True)  # Begin civil twilight
    end_twilight = suth.next_setting(ephem.Moon(), use_center=True)  # End civil twilight
    if end_twilight < beg_twilight:
        beg_twilight = suth.previous_rising(ephem.Moon(), use_center=True)
    rise_set = [beg_twilight, end_twilight]
    return rise_set


def msg_plot():
    """
    massage plot that display data loading in the website
    This is done due to fail to implement status progress using bokeh
    :return: None
    """
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


def set_data_source(dte_, sb_, cc_, err_, tl_, fil_, te, po, fe):
    """
    Set the data source to be the values it receives per selected telescope, position and filter
    all params are list
    :param dte_: date
    :param sb_: sky brightness
    :param cc_: cloud coverage
    :param err_: sky brightness error
    :param tl_: telescope name
    :param fil_: filter band Character
    :param te: telescope checkbox index
    :param po: position checkbox index
    :param fe: filter checkbox index
    :return: None
    """
    global data_source
    data_source[te][po][fe].data['x'] = [d_ + timedelta(hours=2) for d_ in dte_]
    data_source[te][po][fe].data['y'] = ["{0: .2f}".format(float(d_)) for d_ in sb_]
    data_source[te][po][fe].data['coverage'] = cc_
    data_source[te][po][fe].data['h_date'] = [str(d_) for d_ in dte_]
    data_source[te][po][fe].data['error'] = ["{0: .2f}".format(float(d_)) for d_ in err_]
    data_source[te][po][fe].data['telescope'] = tl_
    data_source[te][po][fe].data['filter'] = fil_


def set_range_data_source(med_days, med_list, med_err, med_tel, med_pos, med_fil, med_cou):
    """
    Set the range data source to be the values it receives per selected telescope, position and filter and also the
    line span
    all params are list
    :param med_days: date
    :param med_list: median sky brightness
    :param med_err: standard deviation error
    :param med_tel: telescope name
    :param med_pos: position faced
    :param med_fil: filter band
    :param med_cou: number of data points
    :return: None
    """
    global range_data, range_source, range_span_source

    for te in range(2):
        for po in range(5):
            for fe in range(4):
                range_source[te][po][fe].data['x'] = med_days[te][po][fe]
                range_source[te][po][fe].data['h_date'] = [str(d_)[:10] for d_ in med_days[te][po][fe]]
                range_source[te][po][fe].data['y'] = ["{0: .2f}".format(float(d_)) for d_ in med_list[te][po][fe]]
                range_source[te][po][fe].data['error'] = ["{0: .2f}".format(float(d_)) for d_ in med_err[te][po][fe]]
                range_source[te][po][fe].data['telescope'] = med_tel[te][po][fe]
                range_source[te][po][fe].data['position'] = med_pos[te][po][fe]
                range_source[te][po][fe].data['filter'] = med_fil[te][po][fe]
                range_source[te][po][fe].data['count'] = med_cou[te][po][fe]

                if te not in range_checkbox_list[0] \
                        or po not in range_checkbox_list[1] \
                        or fe not in range_checkbox_list[2]:
                    empty_range(te, po, fe)

                if len(med_days[te][po][fe]) > 0 and len(med_list[te][po][fe]) > 0:
                    """
                    Setting the line span of unselected checkbox
                    """
                    range_span_source[te][po][fe].data['x'] = [min(med_days[te][po][fe]) - relativedelta(days=1),
                                                               max(med_days[te][po][fe]) + relativedelta(days=1)]
                    range_span_source[te][po][fe].data['h_date'] = append_twice("Median Line Statistics")

                    range_span_source[te][po][fe].data['y'] = \
                        append_twice(str("{0: .2f}".format(np.median(med_list[te][po][fe]))))
                    range_span_source[te][po][fe].data['error'] = \
                        append_twice(str("{0: .2f}".format(np.average(med_err[te][po][fe]))))
                    range_span_source[te][po][fe].data['coverage'] = append_twice('Average: ' +
                                                                                  str(np.average(med_list[te][po][fe])))
                    range_span_source[te][po][fe].data['telescope'] = append_twice(
                        'Min: ' + str(min(med_list[te][po][fe])))
                    range_span_source[te][po][fe].data['filter'] = append_twice('Max: ' +
                                                                                str(max(med_list[te][po][fe])))
                    range_span_source[te][po][fe].data['position'] = append_twice(med_pos[te][po][fe][0])
                    range_span_source[te][po][fe].data['count'] = append_twice(len(med_list[te][po][fe]))
                else:
                    """
                    removing the line span of unselected checkbox
                    """
                    range_span_source[te][po][fe].data['x'] = []
                    range_span_source[te][po][fe].data['h_date'] = []

                    range_span_source[te][po][fe].data['y'] = []
                    range_span_source[te][po][fe].data['error'] = []
                    range_span_source[te][po][fe].data['coverage'] = []
                    range_span_source[te][po][fe].data['telescope'] = []
                    range_span_source[te][po][fe].data['filter'] = []
                    range_span_source[te][po][fe].data['count'] = []


def update_line_span():
    """
    updating the line span of data tab
    :return: None
    """
    global data_source
    for te in range(2):
        for po in range(5):
            for fe in range(4):
                temp_list = []
                for ye, a in zip(data_source[te][po][fe].data['y'], data_source[te][po][fe].data['alpha']):
                    if a == 1:
                        temp_list.append(float(ye))

                sday = [min(date_list[te][po][fe]) - relativedelta(minutes=10) + relativedelta(hours=2),
                        max(date_list[te][po][fe]) + relativedelta(hours=2, minutes=10)] if \
                    len(date_list[te][po][fe]) > 0 else []
                shd = append_twice("Median line statistics") if len(temp_list) > 0 else []
                smed = append_twice("{0: .2f}".format(np.median(temp_list))) if len(temp_list) > 0 else []
                savg = append_twice("{0: .2f}".format(np.std(temp_list))) if len(temp_list) > 0 else []
                scov = append_twice('Avg: ' + "{0: .2f}".format((np.average(temp_list)))) if len(temp_list) > 0 else []
                smin = append_twice('Min: ' + "{0: .2f}".format((min(temp_list)))) if len(temp_list) > 0 else []
                smax = append_twice('Max: ' + "{0: .2f}".format((max(temp_list)))) if len(temp_list) > 0 else []

                span_source[te][po][fe].data['x'] = sday
                span_source[te][po][fe].data['h_date'] = shd
                span_source[te][po][fe].data['y'] = smed
                span_source[te][po][fe].data['error'] = savg
                span_source[te][po][fe].data['coverage'] = scov
                span_source[te][po][fe].data['telescope'] = smin
                span_source[te][po][fe].data['filter'] = smax


def slider_moved(attr, old, new):
    """
    Setting alpha of point with cloud coverage higher than attr new value to 0.1 else 1
    :param attr: slider
    :param old: previously selected cloud coverage
    :param new: current cloud coverage
    :return: None
    """
    cc = d_source.data['value'][0]
    for te in range(2):
        for po in range(5):
            for fe in range(4):
                if len(coverage_list[te][po][fe]) > 0:
                    data_source[te][po][fe].data['alpha'] = [1 if c <= cc else 0.1 for c in cc_list[te][po][fe]]

    update_line_span()


def range_slider_moved(attr, old, new):
    """
    removing point that are higher than the selected cloud coverage
    :param attr: range Slider
    :param old: previously selected cloud coverage
    :param new: current cloud coverage
    :return: None
    """
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
    temp_cou = [[[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]],
                [[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]]]
    for ye in range(len(range_data_list)):
        for te in range_checkbox_list[0]:
            for po in range_checkbox_list[1]:
                for fe in range_checkbox_list[2]:
                    d = []
                    l = []
                    e = []
                    if fe != 4:
                        for d_, s_, c_, m_, e_ in zip(range_days[ye][te][po][fe], range_data_list[ye][te][po][fe],
                                                      range_coverage_list[ye][te][po][fe],
                                                      range_moon_list[ye][te][po][fe],
                                                      range_error_list[ye][te][po][fe]):
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
                            temp_days[te][po][fe].append(d[0])
                            temp_sb[te][po][fe].append(float("{0: .2f}".format(np.median(l))))
                            temp_err[te][po][fe].append(float("{0: .2f}".format(np.std(l))))
                            temp_tel[te][po][fe].append(find_telescope_name(te))
                            temp_pos[te][po][fe].append(find_position(po))
                            temp_fil[te][po][fe].append(find_filter_name(fe))
                            temp_cou[te][po][fe].append(len(l))

    r_label.set(text='Loading . . . .')
    set_range_data_source(temp_days, temp_sb, temp_err, temp_tel, temp_pos, temp_fil, temp_cou)
    r_label.set(text='Done ')
    time.sleep(1)
    r_label.set(text=' ')


def update_data_source():
    """
    Update the data source, setting data for the selected checkbox
    :return: None
    """
    global data_source, checkbox_list
    for te in range(2):
        for po in range(5):
            for fe in range(4):
                if fe != 4:
                    if te not in checkbox_list[0] or fe not in checkbox_list[2]:
                        empty_source(te, po, fe)
                    else:
                        dt_, da_, co_, er_, te_, fi_ = ([] for i in range(6))
                        if 4 in checkbox_list[2]:

                            for dt, sb, co, er, tel, fi, mo in zip(date_list[te][po][fe], data_list[te][po][fe],
                                                                   coverage_list[te][po][fe], error_list[te][po][fe],
                                                                   telescope_list[te][po][fe], filter_list[te][po][fe],
                                                                   moon_list[te][po][fe]):
                                if mo == 0:
                                    dt_.append(dt)
                                    da_.append(sb)
                                    co_.append(co)
                                    er_.append(er)
                                    te_.append(tel)
                                    fi_.append(fi)
                            cc_list[te][po][fe] = co_
                            set_data_source(dt_, da_, co_, er_, te_, fi_, te, po, fe)

                        else:
                            dt_ = date_list[te][po][fe]
                            da_ = data_list[te][po][fe]
                            co_ = coverage_list[te][po][fe]
                            ho_ = h_list[te][po][fe]
                            er_ = error_list[te][po][fe]
                            te_ = telescope_list[te][po][fe]
                            fi_ = filter_list[te][po][fe]
                            cc_list[te][po][fe] = coverage_list[te][po][fe]
                            set_data_source(dt_, da_, co_, er_, te_, fi_, te, po, fe)


def button_clicked():
    """
    load new data from the database
    :return: None
    """
    global data
    is_data = False
    d_label.set(text='Loading . ')
    dte_ = selector_to_date(year_.value, month_.value, day_.value)
    data = read_database(dte_, 1)
    d_label.set(text='Loading . . .')
    create_list()
    d_label.set(text='Loading . . . .')
    update_data_source()
    d_label.set(text='Loading . . . . .')
    slider_moved(cloud_coverage, 0, 30)
    d_label.set(text='Done ')

    for te in range(2):
        for po in range(5):
            for fe in range(4):
                if len(data_list[te][po][fe]) > 0:
                    is_data = True
    if is_data:
        time.sleep(2)
        d_label.set(text=' ')
    else:
        d_label.set(text='Date has no data to display')


def week_button_clicked():
    """
    load new data from the database
    :return: None
    """
    global data, data_list
    is_data = False
    d_label.set(text='Loading . ')
    dte_ = selector_to_date(year_.value, month_.value, day_.value)
    data = read_database(dte_, 7)
    d_label.set(text='Loading . . ')
    create_list()
    update_data_source()
    d_label.set(text='Loading . ')
    slider_moved(cloud_coverage, 0, 30)
    d_label.set(text='Done ')

    for te in range(2):
        for po in range(5):
            for fe in range(4):
                if len(data_list[te][po][fe]) > 0:
                    is_data = True
    if is_data:
        time.sleep(2)
        d_label.set(text=' ')
    else:
        d_label.set(text='Date has no data to display')
    if fail:
        d_label.set(text=' Error on creating moon annotation', text_font_size='22px')


def range_button_clicked():
    """
    load new range data from the database
    :return: None
    """
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
        for te in range(2):
            for po in range(5):
                for fe in range(4):
                    if len(temp_sb[te][po][fe]) > 0:
                        is_data = True
        if is_data:
            time.sleep(2)
            r_label.set(text=' ')
        else:
            r_label.set(text_font_size='22px', text='Range has no data to display')


def month_changed(attr, old, new):
    """
    update the month date when date month is changed
    :param attr: not used
    :param old: not used
    :param new: not used
    :return: None
    """
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
    """
    update the month date when date month is changed
    :param attr: not used
    :param old: not used
    :param new: not used
    :return: None
    """
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
    """
    update the month date when date month is changed
    :param attr: not used
    :param old: not used
    :param new: not used
    :return: None
    """
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
    """
    Set the moon annotation
    :param min_day: date to start the annotation set
    :return: None
    """
    global annotations, fail
    moon_up_date = [min_day + timedelta(d) for d in range(10)]

    for i in range(5):
        for d in range(8):
            annotations[i][d].fill_alpha = 0
    d = 0
    for day in moon_up_date:
        for i in range(5):
            r_and_s = find_moon_rise_set(str(day + relativedelta(hours=2)))
            annotations[i][d].set(left=((r_and_s[0]).datetime() +
                                        relativedelta(hours=2, minutes=5)).timestamp() * 1000,
                                  right=((r_and_s[1]).datetime() +
                                         relativedelta(hours=1, minutes=55)).timestamp() * 1000)
            annotations[i][d].fill_alpha = 0.1
        d += 1


def create_list():
    """
    Creating a lists to store data. Two telescopes each with Five positions each position with 4 filter band
    :return:
    """
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

    box_ano = []
    for d in data:
        te = d[4]
        po = d[6]
        fe = find_filter_number(d[5])
        date_list[te][po][fe].append(d[0])
        data_list[te][po][fe].append(d[1])
        coverage_list[te][po][fe].append(d[2])
        moon_list[te][po][fe].append(d[3])
        error_list[te][po][fe].append("{0: .2f}".format(float(d[7])))
        telescope_list[te][po][fe].append(find_telescope_name(te))
        filter_list[te][po][fe].append(d[5])
        h_list[te][po][fe].append(str(d[0]))

        if d[3] == 1:
            box_ano.append((d[0]))
    d_label.set(text='Loading . . . . . ')
    if len(box_ano) > 0:
        create_and_set_annotations(min(box_ano) - relativedelta(days=1))


def create_range_list():
    """
    Create range data list all selected date with two telescopes with 5 positions with 4 filter bands
    :return: None
    """
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
        te = d[4]
        po = d[6]
        fe = find_filter_number(d[5])

        date_ = find_range_date(d[0])

        if date_ not in range_date[te][po][fe]:
            range_date[te][po][fe].append(date_)
            add_day_list()

        nd = find_value_index(date_, range_date[te][po][fe])
        range_days[nd][te][po][fe].append(date_)
        range_data_list[nd][te][po][fe].append(d[1])
        range_error_list[nd][te][po][fe].append(d[7])
        range_coverage_list[nd][te][po][fe].append(d[2])
        range_moon_list[nd][te][po][fe].append(d[3])


def update_checkbox_list(list_, ind_):
    """
    Updating the check box list
    :param list_: new list
    :param ind_: index of list to update/ set to new list (0 telescope, 1 positions, 2 filters)
    :return: None
    """
    global checkbox_list
    checkbox_list[ind_] = list_
    update_data_source()
    slider_moved(0, 0, 0)


def update_range_checkbox_list(list_, ind_):
    global range_checkbox_list
    range_checkbox_list[ind_] = list_
    range_slider_moved(0, 0, 0)

# initiate definitions =================================================================================================

#    Checkbox List
checkbox_list = [[0, 1], [0, 1, 2, 3, 4], [0]]
range_checkbox_list = [[0, 1], [0], [0]]
# ========================= Checkbox List End ====================================

# Selectors=============================================================================================================
dat = datetime.now() - timedelta(days=1)
dat_ = dat - timedelta(days=30)
y = ['2015', '2016']
m = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
day31 = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18',
         '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31']
day30 = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12',  '13', '14', '15', '16', '17', '18',
         '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30']
day29 = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12',  '13', '14', '15', '16', '17', '18',
         '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29']
day28 = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18',
         '19', '20', '21', '22', '23', '24', '25', '26', '27', '28']
fail = False
if str(dat)[:4] not in y:
    y.append(str(dat)[:4])

year_ = Select(title="Year:", value=str(dat)[:4], options=y)
month_ = Select(title="Month:", value=str(dat)[5:7], options=m)
day_ = Select(title="Day:", value=str(dat)[8:10])

range_year_min = Select(title="Year:", value=str(dat_)[:4], options=y)
range_month_min = Select(title="Month:", value=str(dat_)[5:7], options=m)
range_day_min = Select(title="Day:", value=str(dat_)[8:10])
range_year_max = Select(title="Year:", value=str(dat)[:4], options=y)
range_month_max = Select(title="Month:", value=str(dat)[5:7], options=m)
range_day_max = Select(title="Day:", value=str(dat)[8:10])

# Buttons ==============================================================================================================
submit_btn = Button(label="Submit")
week_btn = Button(label="Week")
range_submit_btn = Button(label="Submit")

# Checkbox =============================================================================================================
telescope_group = CheckboxGroup(labels=["Sunrise", "Sunset"], active=[0, 1])
filter_group = CheckboxGroup(labels=["V", "B", "R", "I", "Exclude moon"], active=[0])

range_telescope_group = CheckboxGroup(labels=['Sunrise', 'Sunset'], active=[0, 1])
range_position_group = CheckboxGroup(labels=["Zenith", "South", "East", "North", "West"], active=[0])
range_filter_group = CheckboxGroup(labels=["V", "B", "R", "I", "Exclude moon"], active=[0])

# Sliders ==============================================================================================================
cloud_coverage = Slider(name='slider', start=0, end=100, value=30, step=1, title="Cloud coverage",
                        callback_policy='mouseup')
range_cloud_coverage = Slider(name='range_slider', start=0, end=100, value=30, step=1, title="Cloud coverage",
                              callback_policy='mouseup')

# Dev ==================================================================================================================
telescope_div = Div(text=""" <div class="head-text" ><span >Telescope </span></div>""",  width=60, height=30)
filter_div = Div(text=""" <div class="head-text" ><span >Filter </span></div>""", width=60, height=30)

range_telescope_div = Div(text="""<div class="head-text" ><span >Telescope </span></div>""", width=60, height=30)
range_position_div = Div(text="""<div class="head-text" ><span >Position </span></div>""", width=60, height=30)
range_filter_div = Div(text="""<div class="head-text" ><span >Filter </span></div>""", width=60, height=30)

start_div = Div(text="""<div class="lead-text" ><span >Night Of: </span></div>""", width=140, height=40)

range_start_div = Div(text="""<div class = "lead-text-rng"><span>Start Date: </span></div>""", width=150, height=40)
range_end_div = Div(text=""" <div class = "lead-text-rng"><span>End Date: </span></div>""", width=150, height=50)

# DATA SOURCE ==========================================================================================================
data_source = [[[], [], [], [], []], [[], [], [], [], []]]
span_source = [[[], [], [], [], []], [[], [], [], [], []]]
for t in range(2):
    for p in range(5):
        for f in range(4):
            data_source[t][p].append(ColumnDataSource(data=dict(x=[], y=[], alpha=[], h_date=[], error=[],
                                                                telescope=[], filter=[])))
            span_source[t][p].append(ColumnDataSource(data=dict(x=[], h_date=[], y=[], coverage=[], telescope=[],
                                                                filter=[])))

range_source = [[[], [], [], [], []], [[], [], [], [], []]]
range_span_source = [[[], [], [], [], []], [[], [], [], [], []]]

for t in range(2):
    for p in range(5):
        for fr in range(4):
            range_source[t][p].append(ColumnDataSource(data=dict(x=[], y=[], h_date=[], telescope=[], filter=[],
                                                                 error=[], position=[], count=[])))
            range_span_source[t][p].append(ColumnDataSource(data=dict(x=[], h_date=[], y=[], telescope=[],
                                                                      filter=[], error=[], position=[], count=[])))

source = ColumnDataSource(data=dict(value=[30]))
d_source = ColumnDataSource(data=dict(value=[30]))

# Hovers ===============================================================================================================
tool_list = "pan,reset,save,wheel_zoom, box_zoom"
range_hover = HoverTool(
    tooltips="""
        <div>
            <div>
                <span style="font-size: 15px; font-weight: bold;">@h_date</span>
            </div>
            <div>
                <span style="font-size: 17px;">No. of Points: @count</span>
            </div>
            <div>
                <span style="font-size: 15px; font-weight: bold;">SB: </span>
                <span style="font-size: 15px; color: #669;">@y </span>
                <span style="font-size: 15px; color: #966;">+/-@error </span>
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
range_hover.line_policy = "interp"
range_hover.point_policy = "follow_mouse"
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
                    <span style="font-size: 17px; color: #669; font-weight: bold;">@y </span>
                    <span style="font-size: 17px; color: #966;">+/-@error </span>
                </div>
                <div>
                    <span style="font-size: 18px; font-weight: bold;">@telescope</span>
                    <span style="font-size: 17px; color: #669; font-weight: bold;"> @filter </span>
                </div>
            </div>
            """
    )
    hover[i].point_policy = "follow_mouse"
    hover[i].line_policy = "interp"
    tit_ = find_tittle(i)
    if i == 0:
        plt = figure(title=tit_,
                     toolbar_location='above',
                     tools=[tool_list],
                     x_axis_type="datetime",
                     background_fill_alpha=0.09,
                     plot_width=1140, plot_height=350
                     )
    else:
        plt = figure(title=tit_,
                     toolbar_location='above',
                     tools=[tool_list],
                     x_axis_type="datetime",
                     background_fill_alpha=0.09,
                     plot_width=570, plot_height=250)

    plot.append(plt)
    plot[i].xaxis.major_label_orientation = pi / 4
    plot[i].ygrid.grid_line_color = None
    plot[i].add_tools(hover[i])
    plot[i].title.text_font_size = "25px"
    plot[i].title.align = "center"
    plot[i].title.text_color = "navy"
    plot[i].border_fill_color = "#f4f4f4"
    plot[i].min_border = 30
    plot[i].x_range = plot[0].x_range
    plot[i].y_range = plot[0].y_range

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

# Annotations ==========================================================================================================
for i1 in range(5):
    for da in range(10):
        annotations[i1].append(BoxAnnotation(fill_color='green'))
        plot[i1].renderers.extend([annotations[i1][da]])

# Massage Plot =========================================================================================================

# Initial load of DATA =================================================================================================
date_ = selector_to_date(year_.value, month_.value, day_.value)
data = read_database(date_, 1)
range_data = read_range_database([range_year_min.value, range_month_min.value, range_day_min.value],
                                 [range_year_max.value, range_month_max.value, range_day_max.value])


def main():
    def initiate():
        """
        Initial load of the website
        :return: None
        """
        is_data = False
        create_list()
        create_range_list()

        update_data_source()

        slider_moved(cloud_coverage, 0, 30)
        range_slider_moved(range_cloud_coverage, 0, 30)
        for te in range(2):
            for po in range(5):
                for fe in range(4):
                    if len(data_list[te][po][fe]) > 0:
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

    msg_plot()
    initiate()
    # Plots ============================================================================================================
    for t in range(2):
        for p in range(5):
            for f in range(4):
                col_ = set_colour(t, f)
                if t == 0:
                    plot[p].circle(source=data_source[t][p][f], x='x', y='y', line_width=2, color=col_, alpha='alpha')
                if t == 1:
                    plot[p].diamond(source=data_source[t][p][f], x='x', y='y', line_width=2, color=col_, alpha='alpha')
                plot[p].line(source=span_source[t][p][f], x='x', y='y', line_width=1, color=col_)

    for t in range(2):
        tel_ = 'Sunrise' if t == 0 else 'Sunset'
        for p in range(5):
            for f in range(4):
                filt_ = 'V' if f == 0 else 'B' if f == 1 else 'R' if f == 2 else 'I'
                pos_ = find_position(p)
                col_ = set_colour_range(t, p, f)
                if f == 0:
                    fig0 = range_plot.circle(source=range_source[t][p][f], x='x', y='y', line_width=5, color=col_,
                                             fill_color=None)
                if f == 1:
                    fig1 = range_plot.triangle(source=range_source[t][p][f], x='x', y='y', line_width=5, color=col_)
                if f == 2:
                    fig2 = range_plot.diamond(source=range_source[t][p][f], x='x', y='y', line_width=5, color=col_)
                if f == 3:
                    fig3 = range_plot.square(source=range_source[t][p][f], x='x', y='y', line_width=5,  color=col_,
                                             fill_color=None)
                range_plot.line(source=range_span_source[t][p][f], x='x', y='y', line_width=1, color=col_)

                range_plot.legend.location = 'bottom_right'
                range_plot.legend.background_fill_alpha = 0.4

    #    Interactions definitions ======================================================================================

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
    year_.on_change('value', month_changed)
    range_year_min.on_change('value', range_month_min_changed)
    range_year_max.on_change('value', range_month_max_changed)

    # Widget Box =======================================================================================================
    inputs = widgetbox(cloud_coverage, filter_div, filter_group, telescope_div, telescope_group,
                       width=310, height=180,
                       sizing_mode='scale_both')
    range_inputs = widgetbox(range_cloud_coverage, range_telescope_div, range_telescope_group, range_position_div,
                             range_position_group,
                             range_filter_div, range_filter_group)
    wid_year = widgetbox(year_, week_btn, width=110, height=60)
    wid_month = widgetbox(month_, width=100, height=60)
    wid_day = widgetbox(day_, submit_btn, width=100, height=60)

    dev_col = column(start_div)
    r_dev_col = column(range_start_div, range_end_div)

    wid_year_r = widgetbox(range_year_min, range_year_max, width=110, height=50)
    wid_month_r = widgetbox(range_month_min, range_month_max, width=100, height=50)
    wid_day_r = widgetbox(range_day_min, range_day_max, range_submit_btn, width=100, height=50)

    # View =============================================================================================================

    date_tab = layout([[dev_col, wid_year, wid_month, wid_day, message_plot],
                       [gridplot([plot[0]],
                                 [plot[1], plot[2]],
                                 [plot[3], plot[4]],
                                 spacing=150),
                        inputs]])

    legend = Legend(legends=[
                    ('Filter V', [fig0]),
                    ('Filter B', [fig1]),
                    ('Filter R', [fig2]),
                    ('Filter I', [fig3])
                    ], location=(0, -30))
    range_plot.add_layout(legend, 'left')

    range_tab = layout([[r_dev_col, wid_year_r, wid_month_r, wid_day_r, r_message_plot], [range_plot, range_inputs]])

    tab1 = Panel(child=date_tab, title="Date", sizing_mode="scale_both")
    tab2 = Panel(child=range_tab, title="Date range", sizing_mode="scale_both")
    tabs = Tabs(tabs=[tab1, tab2])

    # Serve ============================================================================================================
    curdoc().add_root(tabs)
    curdoc().title = "SkyBrightness"

print("This is the name!!", __name__)
if __name__.startswith("bk_script"):
    main()
