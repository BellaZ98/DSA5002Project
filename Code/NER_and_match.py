import pandas as pd
import json
import swifter
from LAC import LAC
from tqdm import tqdm

# Read the data
with open('file_root.json', 'r') as f:
    data = json.load(f)

file_root = data['file_root']

# Import the A-share list
with open(file_root + 'A_share_list.json', 'r', encoding='utf-8') as file:
    A_share_list = json.load(file)
comp_all = []
for c in A_share_list:
    comp_all.append([c['name'], c['code'], c['fullname']])
companies_df = pd.DataFrame(comp_all, columns=['name', 'code', 'fullname'])

# Import the news data
news_to_match = pd.read_csv(file_root + 'News_to_match.csv')
news_filtered = pd.read_csv(file_root + 'News_filtered.csv')

# Use LAC to do NER
lac = LAC(mode='lac', use_cuda=True)
batch_size = 1000
texts = news_to_match['Title&Content']
results = []
for i in tqdm(range(0, len(texts), batch_size)):
    batch = texts[i:i + batch_size]
    processed_batch = lac.run(batch.tolist())
    results.extend(processed_batch)
news_to_match['NER'] = pd.Series(results, index=news_to_match.index)


def get_orgs(ner_result):
    orgs = []
    for i, type_w in enumerate(ner_result[1]):
        if type_w == 'ORG':
            orgs.append(ner_result[0][i])
    return orgs


news_to_match['Orgs'] = news_to_match['NER'].apply(get_orgs)
# Make some cleaning for the companies
# Enlarge the search space
companies_df['name_bk'] = companies_df['name']
special_mappings = {
    '*ST生物': '南华生物',
    'ST生态': '洪湖生态',
    '*ST节能': '神雾节能',
    '*ST环保': '天创信息',
    'ST海洋': '厦门海洋',
    '*ST集成': '成飞集成',
    '*ST数码': '航煤数码'
}

companies_df['name'] = companies_df['name'].map(special_mappings).fillna(companies_df['name'])
terms = ['S*ST', '*ST', 'ST', 'B股']


def remove_special_terms(name, special_terms=None):
    if special_terms is None:
        special_terms = terms
    for term in special_terms:
        name = name.replace(term, '')
    return name.strip()


# 使用DataFrame的apply和lambda函数来检查 name_bk 中是否含有特殊字段
contains_special_terms = companies_df['name_bk'].apply(
    lambda x: any(term in x for term in terms)
)
from thefuzz import fuzz

companies_set = set(companies_df['name'])


def match_company(orgs, companies=companies_set, threshold=80):
    matched = set()
    for org in orgs:
        for company in companies:
            similarity = fuzz.ratio(org, company)
            if similarity >= threshold:
                matched.add(company)
    return list(matched) if matched else None


news_to_match['Company'] = news_to_match['Orgs'].swifter.apply(match_company)
news_to_match[['NewsID', 'NewsContent', 'Company']].to_csv(file_root + 'news_to_match_Company.csv',
                                                           encoding='utf-8-sig', index=False)

# merge the news_to_match and news_filtered
# to match the company found in news_to_match
news_to_match_renamed = news_to_match.rename(columns={'Company': 'MatchedCompany'})
news_filtered = news_filtered.merge(news_to_match_renamed[['NewsID', 'MatchedCompany']], on='NewsID', how='left')
news_filtered['Company'] = news_filtered.apply(
    lambda row: row['MatchedCompany'] if pd.isna(row['Company']) else row['Company'],
    axis=1
)
news_filtered.drop(columns=['MatchedCompany'], inplace=True)
news_filtered.dropna(subset=['Company'], inplace=True)

# For the companies mapped, map them back
back_mappings = {}
for _, row in tqdm(companies_df.iterrows()):
    back_mappings[row['name']] = row['name_bk']
news_filtered['Company'] = news_filtered['Company'].map(back_mappings).fillna(news_filtered['Company'])

news_filtered.to_csv(file_root + 'News_matched.csv', encoding='utf-8-sig', index=True)
