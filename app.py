import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import helper
import preprocessor

st.sidebar.title("WhatsApp Chat Analyser")

uploader_file = st.sidebar.file_uploader("Choose a file")
if uploader_file is not None:
    bytes_data = uploader_file.getvalue()
    data = bytes_data.decode('utf-8')
    df = preprocessor.preprocess(data)

    user_list = df['user'].unique().tolist()
    user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, "All Users")

    selected_user = st.sidebar.selectbox("Users", user_list)

    if st.sidebar.button("Show Analysis"):
        num_massages, num_words, num_media, num_links = helper.fetch_stats(selected_user, df)
        st.title("Top Statistics")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.header("Total Massages")
            st.title(num_massages)

        with col2:
            st.header("Total Words")
            st.title(num_words)

        with col3:
            st.header("Media Shared")
            st.title(num_media)

        with col4:
            st.header("Links Shared")
            st.title(num_links)

        # timeline
        st.title("Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user, df)
        fig = px.line(timeline, x="time", y="massage")
        fig.update_layout(autosize=False,
                          width=1500,
                          height=800)
        plt.tight_layout()
        st.plotly_chart(fig)

        st.title("Daily Timeline")
        timeline = helper.daily_timeline(selected_user, df)
        fig = px.line(timeline, x="time", y="massage")
        fig.update_layout(autosize=False,
                          width=1500,
                          height=800)
        plt.tight_layout()
        st.plotly_chart(fig)

        # Activity Time
        st.title("Activity Map")
        col1, col2 = st.columns(2)

        with col1:
            st.header("Most Busy Day")
            busy_day = helper.most_busy_day(selected_user, df)
            fig = px.bar(busy_day, x="Day", y="Total Massage", text_auto='.2s')
            plt.tight_layout()
            st.plotly_chart(fig)

        with col2:
            st.header("Most Busy Month")
            busy_day = helper.most_busy_month(selected_user, df)
            fig = px.bar(busy_day, x="Month", y="Total Massage", text_auto='.2s')
            plt.tight_layout()
            st.plotly_chart(fig)

        # finding the busiest user in group
        if selected_user == "All Users":
            st.title("Most Busy Users")
            x, tmp_df = helper.most_busy_users(df)

            fig, ax = plt.subplots()
            col1, col2 = st.columns(2)

            with col1:
                ax.bar(x.index, x.values, color='green')
                plt.xticks(rotation="90")
                st.pyplot(fig)

            with col2:
                st.table(tmp_df)

        # WordCloud
        st.title("Word Cloud")
        df_wc = helper.create_wordcloud(selected_user, df)
        fig, ax = plt.subplots()
        ax.imshow(df_wc)
        ax.axis("off")
        fig.tight_layout(pad=0)
        st.pyplot(fig)

        # Most Common Word
        st.title("Most Common Words")
        most_common_word_df = helper.most_common_words(selected_user, df)
        fig, ax = plt.subplots()
        ax.barh(most_common_word_df[0], most_common_word_df[1], color='green')
        plt.xlabel("Word Count")
        plt.xticks(rotation="90")
        fig.tight_layout()
        st.pyplot(fig)

        # Emoji Analysis
        emoji_df = helper.emoji_counter(selected_user, df)
        st.title("Emoji Counter")

        col1, col2 = st.columns(2)
        with col1:
            st.table(emoji_df)

        with col2:
            fig = px.pie(values=emoji_df.emoji_count, names=emoji_df.emoji)
            fig.update_traces(hoverinfo='label', textinfo='percent', textfont_size=20,
                              marker=dict(line=dict(color='#000000', width=2)))
            plt.tight_layout()
            st.plotly_chart(fig)

        # Activity Monitor

        fig, ax = plt.subplots(figsize=(24, 7))
        pivot_table = helper.activity_pivot_table(selected_user, df)
        sns.set(font_scale=1.6)
        ax = sns.heatmap(pivot_table, cmap="crest", linewidth=.5, annot=True, fmt='g')
        plt.tight_layout()

        st.title("Weekly Activity Monitor")
        st.pyplot(fig)
