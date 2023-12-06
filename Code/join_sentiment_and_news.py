import pandas as pd
import json


# Read the data
with open('file_root.json', 'r') as f:
    data = json.load(f)

file_root = data['file_root']

news_matched = pd.read_csv(file_root + 'news_matched.csv', encoding='utf-8-sig')
sentiment_output = pd.read_csv(file_root + 'sentiment_output.csv', encoding='utf-8-sig')
news_with_sentiment = news_matched.merge(sentiment_output, on='NewsID', how='left')
task_output = news_with_sentiment[['NewsID', 'NewsContent', 'Company', 'Sentiment']]
task_output['Sentiment'] = task_output['Sentiment'].replace({0: 0, 2: 1, 1: 1})
# Change the column name to fit the requirement
task_output.rename(columns={'Company': 'Explicit_Company', 'Sentiment': 'label'}, inplace=True)
task_output.to_excel(r"D:\Career\HKUST(GZ)\5002\dsaa5002_project\task1.xlsx", index=False)
