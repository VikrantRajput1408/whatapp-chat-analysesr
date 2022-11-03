import re
import pandas as pd


def preprocess(data):
    pattern = "\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s\w{1,2}\s-\s"
    msgs = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)
    df = pd.DataFrame({'date': dates, 'user_massage': msgs})
    df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y, %I:%M %p - ', )
    # Separate user and massages
    users = []
    massages = []
    for msg in df['user_massage']:
        entry = re.split(r'([\w\W]+?):\s', msg)
        if entry[1:]:
            users.append(entry[1])
            massages.append(entry[2][:-1])
        else:
            users.append('group_notification')
            massages.append(entry[0][:-1])
    df['user'] = users
    df['massage'] = massages
    df.drop(columns=['user_massage'], inplace=True)

    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month_name()
    df['day_name'] = df['date'].dt.day_name()
    df['day'] = df['date'].dt.day
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    return df
