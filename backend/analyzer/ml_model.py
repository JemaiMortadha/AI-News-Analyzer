import joblib
import os
from pathlib import Path

class SentimentAnalyzer:
    def __init__(self):
        self.model_path = Path(__file__).parent / 'sentiment_model.pkl'
        self.vectorizer_path = Path(__file__).parent / 'vectorizer.pkl'
        self.model = None
        self.vectorizer = None
        self.load_model()
    
    def load_model(self):
        """Load the pre-trained model and vectorizer"""
        if os.path.exists(self.model_path) and os.path.exists(self.vectorizer_path):
            self.model = joblib.load(self.model_path)
            self.vectorizer = joblib.load(self.vectorizer_path)
        else:
            raise FileNotFoundError("Model files not found. Please train the model first.")
    
    def predict(self, text):
        """Predict sentiment for given text"""
        # Transform text using vectorizer
        text_vectorized = self.vectorizer.transform([text])
        
        # Predict sentiment
        prediction = self.model.predict(text_vectorized)[0]
        
        # Get confidence scores
        probabilities = self.model.predict_proba(text_vectorized)[0]
        confidence = float(max(probabilities))
        
        # Map prediction to sentiment label
        sentiment_map = {0: 'negative', 1: 'neutral', 2: 'positive'}
        sentiment = sentiment_map.get(prediction, 'neutral')
        
        return {
            'sentiment': sentiment,
            'confidence': round(confidence, 2)
        }

# Singleton instance
_analyzer = None

def get_analyzer():
    global _analyzer
    if _analyzer is None:
        _analyzer = SentimentAnalyzer()
    return _analyzer