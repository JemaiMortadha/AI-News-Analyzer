#!/usr/bin/env python
"""
Train a simple sentiment analysis model
Run this once to generate the model files
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import joblib
from pathlib import Path

# Training data - simple sentiment examples
training_data = [
    # Positive
    ("This is excellent news", 2),
    ("Great article, very informative", 2),
    ("Wonderful development in technology", 2),
    ("Fantastic progress has been made", 2),
    ("Outstanding achievement by the team", 2),
    ("Amazing results from the study", 2),
    ("Love this innovation", 2),
    ("Brilliant work on the project", 2),
    ("Superb performance in the market", 2),
    ("Incredible breakthrough in science", 2),
    ("This is good news for everyone", 2),
    ("Positive outlook for the future", 2),
    ("Exciting times ahead", 2),
    ("Best solution I've seen", 2),
    ("Highly successful campaign", 2),
    
    # Negative
    ("This is terrible news", 0),
    ("Very disappointing results", 0),
    ("Awful situation developing", 0),
    ("Bad news for the economy", 0),
    ("Horrible outcome of the event", 0),
    ("Worst case scenario unfolding", 0),
    ("Terrible disaster strikes", 0),
    ("Sad development in the region", 0),
    ("Poor performance this quarter", 0),
    ("Disastrous impact on communities", 0),
    ("Negative trends continue", 0),
    ("Crisis deepens as situation worsens", 0),
    ("Failed attempt at resolution", 0),
    ("Disturbing reports emerge", 0),
    ("Unfortunate turn of events", 0),
    
    # Neutral
    ("The meeting was held yesterday", 1),
    ("Report published on Tuesday", 1),
    ("The company announced quarterly results", 1),
    ("Study shows data trends", 1),
    ("Conference scheduled for next month", 1),
    ("New policy takes effect", 1),
    ("Research conducted over six months", 1),
    ("Analysis of market conditions", 1),
    ("Survey completed with participants", 1),
    ("Documentation has been updated", 1),
    ("The report contains statistics", 1),
    ("Officials meet to discuss plans", 1),
    ("Data collected from various sources", 1),
    ("Information released to the public", 1),
    ("Statement issued by organization", 1),
]

texts, labels = zip(*training_data)

# Create and train the model
vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1, 2))
model = MultinomialNB()

# Fit vectorizer and model
X = vectorizer.fit_transform(texts)
model.fit(X, labels)

# Save the model and vectorizer
model_dir = Path(__file__).parent
joblib.dump(model, model_dir / 'sentiment_model.pkl')
joblib.dump(vectorizer, model_dir / 'vectorizer.pkl')

print("✅ Model trained and saved successfully!")
print(f"   - Model saved to: {model_dir / 'sentiment_model.pkl'}")
print(f"   - Vectorizer saved to: {model_dir / 'vectorizer.pkl'}")

# Test the model
test_texts = [
    "This is amazing news!",
    "Terrible accident occurred",
    "The meeting will be held tomorrow"
]

for text in test_texts:
    X_test = vectorizer.transform([text])
    prediction = model.predict(X_test)[0]
    sentiment_map = {0: 'negative', 1: 'neutral', 2: 'positive'}
    print(f"Text: '{text}' -> Sentiment: {sentiment_map[prediction]}")