import numpy as np
import pandas as pd
import nltk
from sklearn import svm
from sklearn.metrics import classification_report
import pickle
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import torch

torch.set_num_threads(4)

model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
model.max_seq_length = 512

"""
train_df = pd.read_csv('./train.tsv', sep='\t')
test_df = pd.read_csv('./test.tsv', sep='\t')

train_text = train_df['query'].values[:1000]
test_text = test_df['query'].values[:1000]

X_train = model.encode(train_text, show_progress_bar=True)
X_test = model.encode(test_text, show_progress_bar=True)

y_train = train_df.target.values[:1000]
y_test = test_df.target.values[:1000]


clf = svm.SVC()
clf.fit(X_train, y_train)


predictions_rf = clf.predict(X_test)

print(classification_report(y_test, predictions_rf))

"""

classifier = pickle.load(open('./query_classifier.pickle', 'rb'))

res = classifier.predict(model.encode(['Quiero hacer un estudio de la energía solar']))

print(res.tolist()[0])