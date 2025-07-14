import pandas as pd
import os


def preprocess_planetrip():
    if not os.path.exists("planetrip_filtered.csv"):
        return False
    df = pd.read_csv('planetrip_filtered.csv')
    df = df.drop_duplicates(keep='first').reset_index(drop=True)

    # df['destination'] = df['destination'].str.extract(r'\((\w{3})\)')

    df['price'] = df['price'].str.replace('.', '', regex=False).astype(int)

    df['start_time'] = df['start_time'].str.replace('h', ':')
    df['end_time'] = df['end_time'].str.replace('h', ':')

    df['start_hour'] = df['start_time'].str.split(':').str[0].astype(int)
    df['end_hour'] = df['end_time'].str.split(':').str[0].astype(int)

    df['start_hour'] = pd.cut(
        df['start_hour'],
        bins=[0, 3, 9, 15, 21, 24],
        labels=['EarlyMorning', 'Morning',
                'Afternoon', 'Evening', 'LateNight'],
        include_lowest=True
    )
    df['end_hour'] = pd.cut(
        df['end_hour'],
        bins=[0, 3, 9, 15, 21, 24],
        labels=['EarlyMorning', 'Morning',
                'Afternoon', 'Evening', 'LateNight'],
        include_lowest=True
    )

    time_parts = df['trip_time'].str.extract(
        r'(?:(?P<hour>\d+)h)?\s*(?:(?P<minute>\d+)m)?')
    time_parts = time_parts.astype(float).fillna(0)
    df['trip_mins'] = time_parts['hour'] * 60 + time_parts['minute']
    df['trip_mins'] = df['trip_mins'].astype(int)

    df.drop(columns=['start_time', 'end_time', 'trip_time'], inplace=True)

    def convert_vn_date(date_str, year=2025):
        day, month = date_str.strip().split(' thg ')
        dt = pd.to_datetime(f"{day}-{int(month):02d}-{year}", dayfirst=True)
        return dt
    df['start_day'] = df['start_day'].apply(lambda x: convert_vn_date(x, 2025))
    df['end_day'] = df['end_day'].apply(lambda x: convert_vn_date(x, 2025))

    holidays = [
        pd.Timestamp('2025-04-30').date(),
        pd.Timestamp('2025-05-01').date(),
    ]

    nearby_holidays = [
        pd.Timestamp('2025-04-29').date(),
        pd.Timestamp('2025-05-02').date(),
        pd.Timestamp('2025-05-03').date(),
        pd.Timestamp('2025-05-04').date(),
    ]

    def is_holiday(date):
        d = date.date()
        if d in holidays:
            return 3
        elif d in nearby_holidays:
            return 2
        elif d.weekday() >= 4:  # Friday = 4
            return 1
        else:
            return 0
    df['is_holiday'] = df['start_day'].apply(is_holiday)

    df['crawl_date'] = pd.to_datetime(
        df['crawl_date'], format='%d-%m-%Y', errors='coerce')
    df['days_left'] = (pd.to_datetime(df['start_day']) -
                       pd.to_datetime(df['crawl_date'])).dt.days

    df.drop(columns=['start_day', 'end_day', 'crawl_date'], inplace=True)

    df.to_csv(f'planetrip_preprocessed.csv', index=False)
    return True
