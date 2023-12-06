import pandas as pd
import json
import swifter


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
news_all = pd.read_excel(file_root + 'News.xlsx', sheet_name='Sheet1')
news_all['NewsContent'] = news_all['NewsContent'].fillna('').astype(str).str.replace('[\u3000\t\n]', '', regex=True)

# Clean the news with no content
cnt_all = len(news_all)
cnt_before = cnt_all
news_filtered = news_all[news_all['NewsContent'] != '']
cnt_after = len(news_filtered)
print(
    'The number of news with no content is reduced from {} to {}, a total reduction of {}'.format(cnt_before, cnt_after,
                                                                                                  cnt_before - cnt_after))
print('Filter rate = {}'.format((cnt_before - cnt_after) / cnt_all))

# Clean the news with source from international media
cnt_before = len(news_filtered)
sources_to_filter = ['GCI', 'IFX', 'ACM', 'Admiral Markets', '3TG PLUS', 'ACY稀万国际', 'FBS', 'FxPro', 'FXCM',
                     'Domino多米乐', 'Activtrades', 'Hotforex', 'HPCforex', 'CMS/VT', 'Ikon Asia', 'IFX',
                     'www.cnforex.com', 'XFNA', 'NordFX', 'UBEforex', 'XTB', 'NordFX', 'Wind', 'OANDA', 'Markets.com',
                     'PNKForex', 'RocoForex', 'SFA外汇']
news_filtered = news_filtered[~news_filtered['NewsSource'].isin(sources_to_filter)]
cnt_after = len(news_filtered)
print(
    'The number of news with source from international media is reduced from {} to {}, a total reduction of {}'.format(
        cnt_before, cnt_after, cnt_before - cnt_after))
print('Filter rate = {}'.format((cnt_before - cnt_after) / cnt_all))

# Directly match the company name
news_filtered['Title&Content'] = news_filtered.apply(lambda row: row['Title'] + ' ' + row['NewsContent'], axis=1)
name_mapping = {row['fullname']: row['name'] for _, row in companies_df.iterrows()}
name_mapping.update({row['code']: row['name'] for _, row in companies_df.iterrows()})

company_terms = set(companies_df['name']) | set(companies_df['fullname']) | set(companies_df['code'])


def find_companies_optimized(text):
    """
    Find the companies in the text
    :param text:  to be searched
    :return: the list of companies found
    """
    companies = set()
    for term in company_terms:
        if term in text:
            # 如果 term 是 fullname 或 code，获取对应的 name
            company_name = name_mapping.get(term, term)
            companies.add(company_name)
    return list(companies) if companies else None


news_filtered['Company'] = news_filtered['Title&Content'].swifter.apply(find_companies_optimized)
# Split the news into two parts
news_to_match = news_filtered[news_filtered['Company'].isna()]
print('The number of news that can be roughly matched is {}'.format(len(news_filtered) - len(news_to_match)))
print('The number of news that cannot be roughly matched is {}'.format(cnt_all))

# save the data
news_to_match.to_csv(file_root + 'news_to_match.csv', encoding='utf-8-sig', index=False)
news_filtered.to_csv(file_root + 'News_filtered.csv', encoding='utf-8-sig', index=False)
