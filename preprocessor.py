import re
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Ensure NLTK data is downloaded
import nltk
nltk.download('stopwords')
nltk.download('punkt')

def preprocess(chat_data):
    chat_text = chat_data.decode('utf-8')  # Decode binary data into a string

    pattern = '\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s-\s'
    messages = re.split(pattern, chat_text)[1:]
    dates = re.findall(pattern, chat_text)

    df = pd.DataFrame({'user_message': messages, 'message_date': dates})
    df['message_date'] = pd.to_datetime(df['message_date'], format='%m/%d/%y, %H:%M - ')
    df.rename(columns={'message_date': 'date'}, inplace=True)  # Ensure consistency with column name

    users = []
    messages = []

    # Convert the 'date' column to datetime if it's not already in datetime format
    df['date'] = pd.to_datetime(df['date'])

    # Create the 'hour' column
    df['hour'] = df['date'].dt.hour

    for message in df['user_message']:
        entry = re.split('([\w\W]+?):\s', message, maxsplit=1)  # Split only at the first occurrence of ':'
        if len(entry) > 1:  # User name and message
            user = entry[1]
            users.append(user)
            messages.append(entry[2])
        else:  # Group notification or system message
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages


    return df

