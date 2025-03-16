from math import radians
import pandas as pd
import timedelta
from wordcloud import WordCloud
import re
from collections import Counter
import matplotlib.pyplot as plt
import emoji
import atexit
import seaborn as sns
import numpy as np
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import plotly.express as px
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import plotly.graph_objects as go


# Register cleanup function using atexit module
atexit.register(plt.close)

def fetch_stats(df):
    # Placeholder logic
    num_messages = df.shape[0]
    words = df['message'].apply(lambda x: len(str(x).split())).sum()
    num_media_messages = df[df['message'].str.contains('<Media omitted>')].shape[0]
    num_links = df[df['message'].str.contains('http')].shape[0]

    total_users = df['user'].nunique()-1
    total_messages_per_day = num_messages / ((pd.to_datetime('today') - df['date'].min()).days + 1)

    # Calculate most talkative user
    def most_talkative(selected_user, df):
        if selected_user != 'Overall':
            df = df[df['user'] == selected_user]
        user_counts = df['user'].value_counts()
        most_talkative_user = user_counts.idxmax()
        talkative_percentage = (user_counts[most_talkative_user] / len(df)) * 100
        return most_talkative_user, round(talkative_percentage, 2)

    most_talkative_user, talkative_percentage = most_talkative('Overall', df)

# Calculate most influential user based on media messages
    def most_influential_media_user(df):
        media_messages = df[df['message'].str.contains('<Media omitted>')]
        user_media_counts = media_messages['user'].value_counts()
        most_influential_user = user_media_counts.idxmax()
        influential_percentage = (user_media_counts[most_influential_user] / num_media_messages) * 100
        return most_influential_user, round(influential_percentage, 2)

    most_influential_user, influential_percentage = most_influential_media_user(df)

        # Calculate Early Bird (active between 5am to 10am)
    def early_bird(df):
        early_bird_messages = df[(df['date'].dt.hour >= 5) & (df['date'].dt.hour < 10)]
        if early_bird_messages.empty:
            return None, 0  # Return None for user and 0 for percentage if there are no messages in the specified time range
        else:
            user_counts = early_bird_messages['user'].value_counts()
            early_bird_user = user_counts.idxmax()
            early_bird_percentage = (user_counts[early_bird_user] / len(early_bird_messages)) * 100
            return early_bird_user, round(early_bird_percentage, 2)

    early_bird_user, early_bird_percentage = early_bird(df)

    # Calculate Night Owl (active between 12am to 4am)
    def night_owl(df):
        night_owl_messages = df[(df['date'].dt.hour >= 0) & (df['date'].dt.hour < 4)]
        if night_owl_messages.empty:
            return None, 0  # Return None for user and 0 for percentage if there are no messages in the specified time range
        else:
            user_counts = night_owl_messages['user'].value_counts()
            night_owl_user = user_counts.idxmax()
            night_owl_percentage = (user_counts[night_owl_user] / len(night_owl_messages)) * 100
            return night_owl_user, round(night_owl_percentage, 2)

    night_owl_user, night_owl_percentage = night_owl(df)


    # Get first and last message dates
    first_message_date = df['date'].min().strftime('%A %Y-%m-%d')
    last_message_date = df['date'].max().strftime('%A %Y-%m-%d')

    return {
        'num_messages': num_messages,
        'words': words,
        'num_media_messages': num_media_messages,
        'num_links': num_links,
        'total_users': total_users,
        'total_messages_per_day': "{:.2f}".format(total_messages_per_day),
        'most_talkative_user': most_talkative_user,
        'talkative_percentage': talkative_percentage,
        'most_influential_user': most_influential_user,
        'influential_percentage': influential_percentage,
        'early_bird_user': early_bird_user,
        'early_bird_percentage': early_bird_percentage,
        'night_owl_user': night_owl_user,
        'night_owl_percentage': night_owl_percentage,
        'first_message_date': first_message_date,
        'last_message_date': last_message_date
    }


def generate_wordcloud(df):
    # Concatenate all messages into a single string
    all_messages = ' '.join(df['message'].values.tolist())

    # Remove unwanted words like "media omitted"
    all_messages = re.sub(r'\bmedia omitted\b', '', all_messages, flags=re.IGNORECASE)
    all_messages = re.sub(r'\bmessage deleted\b', '', all_messages, flags=re.IGNORECASE)
    all_messages = re.sub(r'\bmessage\b', '', all_messages, flags=re.IGNORECASE)
    all_messages = re.sub(r'\bdeleted\b', '', all_messages, flags=re.IGNORECASE)
   
    # Generate the word cloud
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_messages)

    # Plot the word cloud
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout()

    # Save the word cloud image to a file
    wordcloud_image_path = 'static/wordcloud.png'
    plt.savefig(wordcloud_image_path)

    # Close the plot to free up memory
    plt.close()
    
    return wordcloud_image_path


# emoji
def generate_emoji_pie_chart(df, top_emoji_count=10, font_size=12):
    try:
        # Ensure `get_emoji_regexp` is available (assuming emoji >= 1.4.0)
        emojis = emoji.get_emoji_regexp().findall(' '.join(df['message']))
        emoji_counts = Counter(emojis)

        # Limit to top emojis
        top_emojis = emoji_counts.most_common(top_emoji_count)

        # Extract labels and values
        labels = [k for k, _ in top_emojis]
        values = [v for _, v in top_emojis]

        # Create pie chart
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, text=labels)])

        # Update layout to remove legend
        fig.update_layout(showlegend=False, title='Top 10 Emojis', title_x=0.55, title_y=1)

        # Save the pie chart as an image
        emoji_chart_image_path = 'static/emoji_chart.png'
        fig.write_image(emoji_chart_image_path)

        # Most used emoji and its count
        most_used_emoji, usage_count = top_emojis[0]

        # Total number of different types of emojis used
        total_emojis_used = len(emoji_counts)

        return emoji_chart_image_path, (most_used_emoji, usage_count), total_emojis_used

    except (AttributeError, ImportError) as e:
        print(f"Error generating emoji chart: {e}")
        # Implement a fallback approach or return default values
        return None, None, None  # Indicate error, handle accordingly


def generate_busiest_day_bar_graph(df):
    try:
        # Convert the date column to datetime
        df['date'] = pd.to_datetime(df['date'])

        # Extract day of the week from the date
        df['day_of_week'] = df['date'].dt.day_name()

        # Count the number of messages for each day of the week
        day_counts = df['day_of_week'].value_counts().sort_index()

        # Reindex to include all days of the week in correct order
        all_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_counts = day_counts.reindex(all_days, fill_value=0)

        # Plot the bar graph
        plt.figure(figsize=(8, 6))
        day_counts.plot(kind='bar', color='skyblue')
        plt.xlabel('Day of the Week')
        plt.ylabel('Number of Messages')
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Save the plot as an image
        busiest_day_image_path = 'static/busiest_day_bar_graph.png'
        plt.savefig(busiest_day_image_path)

        # Close the plot to free up memory
        plt.close()

        return busiest_day_image_path

    except Exception as e:
        print(f"Error generating busiest day bar graph: {e}")
        return None


def generate_busiest_month_bar_graph(df):
    try:
        # Convert the date column to datetime
        df['date'] = pd.to_datetime(df['date'])

        # Extract month from the date
        df['month'] = df['date'].dt.month_name()

        # Count the number of messages for each month
        month_counts = df['month'].value_counts().sort_index()

        # Reindex to include all months in correct order
        all_months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        month_counts = month_counts.reindex(all_months, fill_value=0)

        # Plot the bar graph
        plt.figure(figsize=(10, 6))
        month_counts.plot(kind='bar', color='lightgreen')
        plt.xlabel('Month')
        plt.ylabel('Number of Messages')
        # plt.title('Monthly Activity')
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Save the plot as an image
        busiest_month_image_path = 'static/busiest_month_bar_graph.png'
        plt.savefig(busiest_month_image_path)

        # Close the plot to free up memory
        plt.close()

        return busiest_month_image_path

    except Exception as e:
        print(f"Error generating busiest month bar graph: {e}")
        return None


def generate_activity_heatmap(df):
    # Pivot the DataFrame to get the count of messages per hour for each day
    activity_data = df.pivot_table(index='day_of_week', columns='hour', aggfunc='size', fill_value=0)

    # Reorder the days of the week for proper visualization
    activity_data = activity_data.reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])

    # Plot the heatmap
    plt.figure(figsize=(10, 6))
    sns.heatmap(activity_data, cmap='YlGnBu', annot=True, fmt='d', linewidths=.5)
    # plt.title('Message Activity Heatmap')
    plt.xlabel('Hour')
    plt.ylabel('Day of the Week')
    plt.tight_layout()
    plt.savefig('static/activity_heatmap.png')  # Save the heatmap image
    plt.close()

    return 'static/activity_heatmap.png'

def generate_user_activity_bar_graph(df):
    try:
        # Filter out 'group_notification' users
        filtered_df = df[df['user'] != 'group_notification']

        # Calculate total messages per user
        user_messages = filtered_df['user'].value_counts()

        # Calculate the number of weeks covered in the chat data
        num_weeks = (filtered_df['date'].max() - filtered_df['date'].min()).days // 7 + 1

        # Calculate average messages per week for each user
        user_avg_messages_per_week = user_messages / num_weeks

        # Select top 10 users with highest average messages per week
        top_users = user_avg_messages_per_week.nlargest(10)

        # Plot the bar graph
        plt.figure(figsize=(10, 6))
        top_users.plot(kind='bar', color='salmon')
        plt.xlabel('User')
        plt.ylabel('Average Messages per Week')
        plt.title('Top 10 Most Active Users')
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Save the plot as an image
        user_activity_image_path = 'static/user_activity_bar_graph.png'
        plt.savefig(user_activity_image_path)
        plt.close()  # Close the plot

        return user_activity_image_path

    except Exception as e:
        print(f"Error generating user activity bar graph: {e}")
        return None


def generate_common_words_bar_graph(df):
    # Preprocess messages
    messages = df['message'].str.lower()

    # Remove punctuation and symbols
    messages = messages.apply(lambda x: re.sub(r'[^a-zA-Z\s]', '', x))

    # Tokenize words
    words = ' '.join(messages).split()

    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    words = [word for word in words if word not in stop_words]

    # Define additional words or phrases to remove
    words_to_remove = ['media', 'omitted', 'message', 'deleted', '<>']  # Add more words as needed

    # Remove specific words or phrases
    words = [word for word in words if word not in words_to_remove]

    # Calculate word frequency
    word_freq = pd.Series(words).value_counts().reset_index()
    word_freq.columns = ['word', 'frequency']

    # Take top 10 common words
    top_10_words = word_freq.head(10)

    # Plot bar graph
    plt.figure(figsize=(10, 6))
    sns.barplot(x='frequency', y='word', data=top_10_words, palette='viridis')
    plt.title('Top 10 Common Words')
    plt.xlabel('Frequency')
    plt.ylabel('Word')
    plt.tight_layout()

    # Save bar graph image
    common_words_bar_graph_path = 'static/common_words_bar_graph.png'
    plt.savefig(common_words_bar_graph_path)
    plt.close()  # Close the plot to free memory

    return common_words_bar_graph_path



