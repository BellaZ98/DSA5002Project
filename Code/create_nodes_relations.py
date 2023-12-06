from neo4j import GraphDatabase
import pandas as pd
from tqdm import tqdm
import json

# Read the data
with open('file_root.json', 'r') as f:
    data = json.load(f)

file_root = data['file_root']
company = pd.read_csv(file_root + 'hidy.nodes.company.csv')
compete = pd.read_csv(file_root + 'hidy.relationships.compete.csv')
cooperate = pd.read_csv(file_root + 'hidy.relationships.cooperate.csv')
dispute = pd.read_csv(file_root + 'hidy.relationships.dispute.csv')
invest = pd.read_csv(file_root + 'hidy.relationships.invest.csv')
same_industry = pd.read_csv(file_root + 'hidy.relationships.same_industry.csv')
supply = pd.read_csv(file_root + 'hidy.relationships.supply.csv')

# Connect to the neo4j server
url = "neo4j://localhost:7687"
username = "neo4j"
password = "dsaa5002"

driver = GraphDatabase.driver(url, auth=(username, password))


# Import the company nodes
def create_node(tx, name, ID, code, label):
    tx.run("CREATE (a:Company {name: $name, ID: $ID, code: $code, label: $label})", name=name, ID=ID, code=code,
           label=label)


with driver.session() as session:
    print('Creating nodes...')
    for i in tqdm(range(len(company))):
        session.execute_write(create_node, company['company_name'][i], company[':ID'][i], company['code'][i],
                              company[':LABEL'][i])


# Load the relations
def create_relation(tx, start_ID, end_ID, relation):
    query = f"MATCH (a:Company), (b:Company) WHERE a.ID = $start_ID AND b.ID = $end_ID MERGE (a)-[r:{relation}]->(b)"
    tx.run(query, start_ID=start_ID, end_ID=end_ID)


with driver.session() as session:
    print('Creating relations compete:')
    for i, row in tqdm(compete.iterrows()):
        session.execute_write(create_relation, row[':START_ID'], row[':END_ID'], row[':TYPE'])

    print('Creating relations cooperate:')
    for i, row in tqdm(cooperate.iterrows()):
        session.execute_write(create_relation, row[':START_ID'], row[':END_ID'], row[':TYPE'])

    print('Creating relations invest:')
    for i, row in tqdm(invest.iterrows()):
        session.execute_write(create_relation, row[':START_ID'], row[':END_ID'], row[':TYPE'])

    print('Creating relations dispute:')
    for i, row in tqdm(dispute.iterrows()):
        session.execute_write(create_relation, row[':START_ID'], row[':END_ID'], row[':TYPE'])

    print('Creating relations same_industry:')
    for i, row in tqdm(same_industry.iterrows()):
        session.execute_write(create_relation, row[':START_ID'], row[':END_ID'], row[':TYPE'])

    print('Creating relations supply:')
    for i, row in tqdm(supply.iterrows()):
        session.execute_write(create_relation, row[':START_ID'], row[':END_ID'], row[':TYPE'])
