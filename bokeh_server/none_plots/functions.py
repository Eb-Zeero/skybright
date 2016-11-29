# functions mostly called
from datetime import timedelta
import os
from datetime import datetime
import ephem

import pandas as pd
from app import db


config = {
    'user': os.environ['SKY_DATABASE_USER'],
    'password': os.environ['SKY_DATABASE_PASSWORD'],
    'host': os.environ['SKY_DATABASE_URI'],
    'db': os.environ['SKY_DATABASE_USER'],
    'charset': os.environ['SKY_CHARSET']
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

    #sql = 'SELECT * FROM SomeTable'
    #df = pd.read_sql(sql, db.engine)

    sql = (
                    "SELECT DATE_TIME, SKYBRIGHTNESS, CLOUD_COVERAGE, MOON, TELESCOPE, FILTER_BAND, POSX, SB_ERROR "
                    "FROM SkyBrightness "
                    "WHERE DATE_TIME > '%s-%s-%s 13:00:00' "
                    "AND DATE_TIME < '%s-%s-%s 13:00:00' "
                    "AND SKYBRIGHTNESS != 0 "
                ) % (str(date_)[0:4], str(date_)[5:7], str(date_)[8:10],
                     str(date_n)[0:4], str(date_n)[5:7], str(date_n)[8:10])

    select_sb = (
              "SELECT DATE_TIME, SKYBRIGHTNESS, CLOUD_COVERAGE, MOON, TELESCOPE, FILTER_BAND, POSX, SB_ERROR "
              "FROM SkyBrightness "
              "WHERE DATE_TIME > '%s-%s-%s 13:00:00' "
              "AND DATE_TIME < '%s-%s-%s 13:00:00' "
              "AND SKYBRIGHTNESS != 0 "
          ) % (str(date_)[0:4], str(date_)[5:7], str(date_)[8:10],
               str(date_n)[0:4], str(date_n)[5:7], str(date_n)[8:10])

    #cnx = mysql.connector.connect(**config)
    try:
        df = pd.read_sql(sql, db.engine)
        print(df)
        #cursor = cnx.cursor()
        #cursor.execute(select_sb)
        #data = cursor.fetchall()

    except :#mysql.connector.Error as err:
        #if cnx:
        print("there was a problem with selecting")
         #   print(err)

    finally:
        #if cnx:
        #    cnx.close()
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
    #cnx = mysql.connector.connect(**config)
    try:
        #cursor = cnx.cursor()
        #cursor.execute(select_ext)
        #ext_data = cursor.fetchall()
        print("yeahh")

    except :#mysql.connector.Error as err:
        #if cnx:
        print("there was a problem with selecting")
        #    print(err)

    finally:
        #if cnx:
         #   cnx.close()
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

    #cnx = mysql.connector.connect(**config)
    try:
        print('yess')
        #cursor = cnx.cursor()
        #cursor.execute(select_sb)
        #range_data = cursor.fetchall()
    except:# mysql.connector.Error as err:
        #if cnx:
        print("there was a problem with selecting")
            #print(err)

    finally:
        #if cnx:
        #    cnx.close()
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
    #suth.horizon = '-18' #previous
    beg_twilight = suth.next_rising(ephem.Moon(), use_center=True)  # Begin civil twilight
    end_twilight = suth.next_setting(ephem.Moon(), use_center=True)  # End civil twilight
    if end_twilight < beg_twilight:
        beg_twilight = suth.previous_rising(ephem.Moon(), use_center=True)
    rise_set = [beg_twilight, end_twilight]
    return rise_set
