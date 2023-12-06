# DSA5002Project

The final project for the DSAA5002.
Using the relations between A-share companies and the sentiment information in financial news to categorize the effect of the news on the companies.

## Initial setup

Make sure you've changed the file_root in `/code/file_root.json`, the value should be changed into the folder path where `News.xlsx` is in.

**Install Requirements**

```
pip install -r requirements.txt
```


## File list

If you only want to check the code, you can ignore the folder `/Notebooks` . Run the `.py` files in folder `/Code` one by one.
You can also click RunAll to run every `.ipynb` file in folder `/Notebooks`

- `task1.xlsx` - The output required for the Task1.
- `task2.xlsx` - The output required for the Task2.
- `requirements.txt`

- `/Code`

  - `file_root.json` - Stores the route of the file_root.
  - `clean_the_news.py` - First part of the solution to task1 quesiton1, using many filters to clean the data, match the content of news with the A share company names.
  - `NER_and_match.py` - Second part of the solution to task1 quesiton1, use NER to match the company names that cannot be matched in the first part.
  - `sentiment_analysis.py` - First part of the solution to task1 quesiton2, Sentiment Analysis using fine-tuned bert.
  - `join_sentiment_and_news.py` - Second part of the solution to task1 quesiton2, join the sentiment data with the matched result in task1 question2 and output the file required in task1 question2.
  - `create_nodes_and_relations.py` - Solution to task2 question1, create nodes representing companies and create the relations between them.
  - `calculate_effects_using_relations.py` - Solution to task2 question2, interact with neo4j to get the relations and calculate the effect of the news.
  
- `/Notebooks` - Notebooks I used when dealing with the problem. If you only want to check the python script, you can ignore them. You can also check the output without running them.

  - `project_solutionT1Q1.ipynb` - Solution to task1 quesiton1, using many filters to clean the data, match the content of news with the A share company names.
  - `project_solutionT1Q2P1.ipynb` - First part of the solution to task1 quesiton2, Sentiment Analysis using fine-tuned bert.
  - `project_solutionT1Q2P2.ipynb` - Second part of the solution to task1 quesiton2, join the sentiment data with the matched result in task1 question2 and output the file required in task1 question2.
  - `project_solutionT2Q1.ipynb` - Solution to task2 question1, create nodes representing companies and create the relations between them.
  - `project_solutionT2Q2.ipynb` - Solution to task2 question2, interact with neo4j to get the relations and calculate the effect of the news.
