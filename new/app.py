# -*- coding: utf-8 -*-
"""app.py

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1u5maFXNetq5d0QtuLjQoRJ_kk9RdtG7a
"""



import pandas as pd
df = pd.read_csv('updated_output.csv');
# Specify the columns you want to keep
columns_to_keep = ['bibliography.subjects', 'textofbook', 'bibliography.author.name','bibliography.title']

# Drop all columns except the specified ones
df = df[columns_to_keep]
# Drop rows with NaN values in 'textofbook' column
df = df.dropna(subset=['textofbook'])
# Drop rows with NaN values in 'textofbook' column
df = df.dropna(subset=['bibliography.subjects'])
df = df.sample(frac=1, random_state=42)

import nltk


import pandas as pd
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from flask import Flask, render_template, request
import pandas as pd
import nltk

# Load your data into a DataFrame
# ... (same code as before to load data and preprocess texts)

# Create a dictionary mapping book texts to author names, subjects, and titles
book_info = {}
for idx, row in df.iterrows():
    book_info[row['textofbook']] = {
        'author': row['bibliography.author.name'],
        'subjects': row['bibliography.subjects'],
        'title': row['bibliography.title']
    }

# Preprocess the book texts
stop_words = set(stopwords.words('english'))
preprocessed_texts = []

for text in df['textofbook']:
    # Tokenize the text
    tokens = nltk.word_tokenize(text.lower())

    # Remove stopwords and punctuation
    filtered_tokens = [token for token in tokens if token.isalnum() and token not in stop_words]

    preprocessed_texts.append(' '.join(filtered_tokens))

# Create TF-IDF matrix
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(preprocessed_texts)



# Create Flask app
app = Flask(__name__)

# Route for the homepage
@app.route('/')
def home():
    return render_template('index.html')

# Route for handling queries
@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    top_results = retrieve_docs(query)
    return render_template('results.html', results=top_results, query=query)

# Function to retrieve relevant documents
def retrieve_docs(query):
      query_vec = vectorizer.transform([query])
      similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()

    # Sort and return the top 5 most relevant document indices
      top_indices = (-similarities).argsort()[:5]

    # Retrieve author names, genres, titles, and texts for the top indices
      top_results = []
      for idx in top_indices:
          book_text = df.iloc[idx]['textofbook']
          top_results.append({
              'author': book_info[book_text]['author'],
              'subjects': book_info[book_text]['subjects'],
              'title': book_info[book_text]['title'],
              'text': book_text[:100] + "..."
          })

      return top_results

if __name__ == '__main__':
    app.run(debug=True)