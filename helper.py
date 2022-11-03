from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
import string
import emoji
from collections import Counter


def remove_stopwords(massage):
    with open('stop_hinglist.txt', 'r') as f:
        stopword = f.read()
        f.close()
    stopword += "\n,\ngya\ngye"

    words = []
    for msg in massage:
        msg = msg.translate(str.maketrans('', '', string.punctuation))
        for word in msg.lower().split(" "):
            if word not in stopword:
                words.append(word)
    return words


def fetch_stats(user, df):
    if user != "All Users":
        df = df[df['user'] == user]

    # Number of Massages
    num_msgs = df.shape[0]

    # Number of Words, media, and links
    num_media = 0
    links = []
    words = []
    url_extractor = URLExtract()
    for msg in df['massage']:
        links.extend(url_extractor.find_urls(msg))
        if msg == "<Media omitted>" or msg == "<omitted Media>":
            num_media += 1
        else:
            words.extend(msg.split())

    num_words = len(words)
    num_links = len(links)
    return num_msgs, num_words, num_media, num_links


def most_busy_users(df):
    x = df['user'].value_counts()
    percent = round((x / df.shape[0]) * 100, 2).reset_index().rename(columns={'index': 'name', 'user': 'massage '
                                                                                                       'percentage'})

    return x.head(), percent.head(15)


def create_wordcloud(selected_user, df):
    if selected_user != "All Users":
        df = df[df["user"] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['massage'] != '<Media omitted>']
    with open('stop_hinglist.txt', 'r') as f:
        stopword = f.read()
        f.close()
    stopword += "\n,\ngya\ngye"

    words = remove_stopwords(temp['massage'])

    wc = WordCloud(width=1500, height=1200, min_font_size=1, background_color='white')
    df_wc = wc.generate(" ".join(words))
    return df_wc


def most_common_words(selected_user, df):
    if selected_user != "All Users":
        df = df[df["user"] == selected_user]
    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['massage'] != '<Media omitted>']
    with open('stop_hinglist.txt', 'r') as f:
        stopword = f.read()
        f.close()
    stopword += "\n,\ngya\ngye"

    words = remove_stopwords(temp['massage'])
    rtn_df = pd.DataFrame(Counter(words).most_common(20))
    return rtn_df


def emoji_counter(selected_user, df):
    if selected_user != "All Users":
        df = df[df["user"] == selected_user]
    emojis = []
    for massage in df['massage']:
        emojis.extend(emoji.distinct_emoji_list(massage))
    counts = Counter(emojis)
    emoji_df = pd.DataFrame(counts.most_common(len(counts)))
    emoji_df.rename(columns={0: "emoji", 1: "emoji_count"}, inplace=True)

    top_emoji = emoji_df.head(10)
    other_emoji_count = sum(emoji_df['emoji_count']) - sum(top_emoji['emoji_count'])
    top_emoji.loc[5] = ['other', other_emoji_count]
    return top_emoji


def monthly_timeline(selected_user, df):
    if selected_user != "All Users":
        df = df[df["user"] == selected_user]
    timeline = df.groupby(['year', 'month']).count()['massage'].reset_index()
    timeline["time"] = timeline['month'] + "-" + timeline['year'].astype(str)
    return timeline


def daily_timeline(selected_user, df):
    if selected_user != "All Users":
        df = df[df["user"] == selected_user]
    timeline = df.groupby(['year', 'month', 'day']).count()['massage'].reset_index()
    timeline["time"] = timeline['day'].astype(str) + " " + timeline['month'] + "-" + timeline['year'].astype(str)
    return timeline


def most_busy_day(selected_user, df):
    if selected_user != "All Users":
        df = df[df["user"] == selected_user]
    x = df['day_name'].value_counts().reset_index().values.tolist()
    tmp_dct = {'Sunday': 1, 'Monday': 2, 'Tuesday': 3, 'Wednesday': 4, 'Thursday': 5, "Friday": 6, "Saturday": 7}
    x.sort(key=lambda t: tmp_dct[t[0]])
    return pd.DataFrame(x, columns=(['Day', "Total Massage"]))


def most_busy_month(selected_user, df):
    if selected_user != "All Users":
        df = df[df["user"] == selected_user]
    x = df['month'].value_counts().reset_index().values.tolist()
    tmp_dct = {'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, "June": 6, "July": 7, 'August': 8,
               'September': 9, 'October': 10, 'November': 11, "December": 12}
    x.sort(key=lambda t: tmp_dct[t[0]])
    return pd.DataFrame(x, columns=(['Month', "Total Massage"]))


def activity_pivot_table(selected_user, df):
    if selected_user != "All Users":
        df = df[df["user"] == selected_user]
    df['period'] = df['hour'].astype(str) + '-' + (df['hour'] + 1).astype(str)
    df.replace({"24-25": "0-1"}, inplace=True)
    pivot_table = df.pivot_table(index='day_name', columns='period', values='massage', aggfunc='count').fillna(0)
    pivot_table = pivot_table.reindex(sorted(pivot_table.columns, key=lambda x: int(x.split('-')[0])), axis=1)
    tmp_day = {'Sunday': 1, 'Monday': 2, 'Tuesday': 3, 'Wednesday': 4, 'Thursday': 5, "Friday": 6, "Saturday": 7}
    pivot_table = pivot_table.reindex(sorted(pivot_table.index, key=lambda x: tmp_day[x]), axis=0)
    return pivot_table


