from neo4j import GraphDatabase
from tqdm import tqdm_notebook as tqdm
import pandas as pd
import json

# Connect to the neo4j server
url = "neo4j://localhost:7687"
username = "neo4j"
password = "dsaa5002"

# Read the data
with open('file_root.json', 'r') as f:
    data = json.load(f)

file_root = data['file_root']

driver = GraphDatabase.driver(url, auth=(username, password))
# Import data
news_with_sentiment = pd.read_excel(file_root + "task1.xlsx")

#  Convert from string to list
news_with_sentiment['Explicit_Company'] = news_with_sentiment['Explicit_Company'].apply(lambda x: x[1:-1].split(', '))


def match_relationships(tx, start_company):
    query = (
        "MATCH (a:Company {name: $company_name})-[r]->(b) "
        "RETURN b.name as company, type(r) as relation"
    )
    result = tx.run(query, company_name=start_company)
    return [(record["company"], record["relation"]) for record in result]


opposite_impact_sentiment = ['compete', 'dispute']
same_impact_sentiment = ['cooperate', 'invest', 'same_industry', 'supply']

Implicit_Positive_Company = []
Implicit_Negative_Company = []
with driver.session() as session:
    for index, row in tqdm(news_with_sentiment.iterrows(), total=news_with_sentiment.shape[0]):
        positive = []
        negative = []
        for start_company in row['Explicit_Company']:
            relationships = session.execute_read(match_relationships, start_company)
            for end_company, relation in relationships:
                if row['label'] == 0:
                    if relation in opposite_impact_sentiment:
                        negative.append(end_company)
                    elif relation in same_impact_sentiment:
                        positive.append(end_company)
                else:
                    if relation in same_impact_sentiment:
                        negative.append(end_company)
                    elif relation in opposite_impact_sentiment:
                        positive.append(end_company)
        Implicit_Positive_Company.append(positive)
        Implicit_Negative_Company.append(negative)

news_with_sentiment['Implicit_Positive_Company'] = Implicit_Positive_Company
news_with_sentiment['Implicit_Negative_Company'] = Implicit_Negative_Company


def list_to_string(lst):
    # 将列表转换为字符串
    return ','.join(lst)


news_with_sentiment['Implicit_Positive_Company'] = news_with_sentiment['Implicit_Positive_Company'].apply(
    list_to_string)
news_with_sentiment['Implicit_Negative_Company'] = news_with_sentiment['Implicit_Negative_Company'].apply(
    list_to_string)
news_with_sentiment.to_excel(file_root + "task2.xlsx", index=False)
