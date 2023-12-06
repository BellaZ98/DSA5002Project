import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from torch.utils.data import DataLoader
from transformers import DataCollatorWithPadding
from tqdm import tqdm
import gc
import pandas as pd
from torch.utils.data import Dataset
import json

# Check GPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

tokenizer = AutoTokenizer.from_pretrained("hw2942/bert-base-chinese-finetuning-financial-news-sentiment-v2")
model = AutoModelForSequenceClassification.from_pretrained(
    "hw2942/bert-base-chinese-finetuning-financial-news-sentiment-v2")


# Read the data
with open('file_root.json', 'r') as f:
    data = json.load(f)

file_root = data['file_root']
news_filtered = pd.read_csv(file_root + 'news_filtered.csv')
model.to(device)
# Data preprocessing
texts = []
for _, row in news_filtered.iterrows():
    texts.append(row['Title'] + ' ' + row['NewsContent'])

chunk_size = 10000  # 每次处理个文本


class TextDataset(Dataset):
    def __init__(self, encodings):
        self.encodings = encodings

    def __getitem__(self, idx):
        return {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}

    def __len__(self):
        return len(self.encodings['input_ids'])


predictions = []
# 分批处理文本
for i in tqdm(range(0, len(texts), chunk_size)):
    chunk = texts[i:i + chunk_size]
    # 使用tokenizer处理当前批次
    encoded_chunk = tokenizer(chunk, padding=True, truncation=True, max_length=512, return_tensors="pt")
    # 处理编码后的数据，例如保存到文件或用于模型训练
    dataset = TextDataset(encoded_chunk)
    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)
    # 创建DataLoader
    data_loader = DataLoader(dataset, batch_size=256, collate_fn=data_collator)
    # 批量预测
    model.eval()
    with torch.no_grad():
        for batch in tqdm(data_loader):
            batch = {k: v.to(device) for k, v in batch.items()}
            outputs = model(**batch)
            predictions.extend(torch.argmax(outputs.logits, dim=-1).tolist())
    # 清理内存
    del encoded_chunk
    gc.collect()

pred_sr = pd.Series(predictions)
sentiment_output = pd.DataFrame()
sentiment_output['NewsID'] = news_filtered['NewsID']
sentiment_output['Sentiment'] = pred_sr
sentiment_output.to_csv('/content/drive/MyDrive/data/sentiment_output.csv', index=False)
