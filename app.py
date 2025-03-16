# app.py

from flask import Flask, render_template, request,send_file,send_from_directory
from preprocessor import preprocess
from helper import fetch_stats, generate_wordcloud, generate_emoji_pie_chart, generate_activity_heatmap, generate_busiest_day_bar_graph, generate_busiest_month_bar_graph, generate_user_activity_bar_graph, generate_common_words_bar_graph 
import pandas as pd
from collections import Counter
import os
from datetime import datetime
from datetime import timedelta


app = Flask(__name__)

df = None  # Global DataFrame variable

def format_date(date_str):
    date = datetime.strptime(date_str, "%A %Y-%m-%d")
    day_suffix = "th" if 11 <= date.day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(date.day % 10, "th")
    return date.strftime(f"%A, %d{day_suffix} %B %Y")


@app.route('/', methods=['GET', 'POST'])
def index():
    global df

    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', error="No file part")

        file = request.files['file']
        if file.filename == '':
            return render_template('index.html', error="No selected file")

        if file:
            try:
                bytes_data = file.read()
                df = preprocess(bytes_data)
                stats = fetch_stats(df)
                wordcloud_image = generate_wordcloud(df)
                emoji_chart_image_path, most_used_emoji_info, total_emojis_used = generate_emoji_pie_chart(df)
                most_used_emoji, most_used_emoji_count = most_used_emoji_info  # Extracting the emoji and its count
                busiest_day_bar_graph_path = generate_busiest_day_bar_graph(df)
                busiest_month_bar_graph_path = generate_busiest_month_bar_graph(df)
                activity_heatmap_image = generate_activity_heatmap(df)
                user_activity_bar_graph_path = generate_user_activity_bar_graph(df)  # New graph
                common_words_bar_graph_path = generate_common_words_bar_graph(df)  # New graph

                # Calculate the most talkative user and their message count
                user_message_counts = Counter(df['user'])
                most_talkative_user, most_messages_count = user_message_counts.most_common(1)[0]
                total_messages = len(df)
                talkative_percentage = round((most_messages_count / total_messages) * 100, 2)

                # Calculate the most influential media user and their percentage
                most_influential_user = stats['most_influential_user']
                influential_percentage = stats['influential_percentage']

                    # Calculate Early Bird (active between 6am to 10am)
                early_bird_messages = df[(df['hour'] >= 6) & (df['hour'] < 10)]
                if early_bird_messages.empty:
                    early_bird_user, early_bird_percentage = None, 0
                else:
                    user_counts = early_bird_messages['user'].value_counts()
                    early_bird_user = user_counts.idxmax()
                    early_bird_percentage = (user_counts[early_bird_user] / len(early_bird_messages)) * 100
                    early_bird_percentage = round(early_bird_percentage, 2)

                # Calculate Night Owl (active between 12am to 6am)
                night_owl_messages = df[(df['hour'] >= 0) & (df['hour'] < 6)]
                if night_owl_messages.empty:
                    night_owl_user, night_owl_percentage = None, 0
                else:
                    user_counts = night_owl_messages['user'].value_counts()
                    night_owl_user = user_counts.idxmax()
                    night_owl_percentage = (user_counts[night_owl_user] / len(night_owl_messages)) * 100
                    night_owl_percentage= round(night_owl_percentage, 2)

                # Get the uploaded filename
                uploaded_filename = os.path.splitext(file.filename)[0]

                # Format first and last message dates
                first_message_date = format_date(stats['first_message_date'])
                last_message_date = format_date(stats['last_message_date'])

                return render_template('result.html',
                                        emoji_chart_image_path=emoji_chart_image_path,
                                        most_used_emoji=most_used_emoji,
                                        most_used_emoji_count=most_used_emoji_count,
                                        total_emojis_used=total_emojis_used,
                                        wordcloud_image=wordcloud_image,
                                        stats=stats,
                                        busiest_day_bar_graph_path=busiest_day_bar_graph_path,
                                        busiest_month_bar_graph_path=busiest_month_bar_graph_path,
                                        activity_heatmap_image=activity_heatmap_image,
                                        user_activity_bar_graph_path=user_activity_bar_graph_path, 
                                        common_words_bar_graph_path=common_words_bar_graph_path, 
                                        most_talkative_user=most_talkative_user,
                                        talkative_percentage=talkative_percentage,
                                        most_influential_user=most_influential_user,
                                        influential_percentage=influential_percentage,
                                        early_bird_user=early_bird_user,
                                        early_bird_percentage=early_bird_percentage,
                                        night_owl_user=night_owl_user,
                                        night_owl_percentage=night_owl_percentage,
                                        uploaded_filename=uploaded_filename,
                                        first_message_date=first_message_date, 
                                        last_message_date=last_message_date
                                        )

            except Exception as e:
                print("Error:", e)
                return render_template('index.html', error="An error occurred during processing")

    return render_template('index.html')

@app.route('/activity_percentage', methods=['POST'])
def activity_percentage():
    user = request.form['user']
    activity = request.form['activity']

    if df is None:
        return render_template('result.html', error="DataFrame is not loaded yet")

    activity_percentage = generate_activity_heatmap(df, user, activity)
    return render_template('result.html', user=user, activity=activity, activity_percentage=activity_percentage)

@app.route('/get_heatmap')
def get_heatmap():
    return send_file('static/activity_heatmap.png', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)


