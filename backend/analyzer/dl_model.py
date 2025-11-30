import torch
import torch.nn as nn
import pickle
from pathlib import Path

class SentimentCNN(nn.Module):
    def __init__(self, vocab_size, embedding_dim=128, num_filters=128, filter_sizes=[3,4,5], num_classes=3):
        super(SentimentCNN, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        self.convs = nn.ModuleList([
            nn.Conv1d(embedding_dim, num_filters, kernel_size=fs)
            for fs in filter_sizes
        ])
        self.dropout = nn.Dropout(0.5)
        self.fc = nn.Linear(len(filter_sizes) * num_filters, num_classes)
    
    def forward(self, x):
        embedded = self.embedding(x).permute(0, 2, 1)
        conved = [torch.relu(conv(embedded)) for conv in self.convs]
        pooled = [torch.max_pool1d(conv, conv.shape[2]).squeeze(2) for conv in conved]
        cat = self.dropout(torch.cat(pooled, dim=1))
        return self.fc(cat)

def text_to_sequence(text, vocab, max_length=50):
    words = text.lower().split()
    seq = [vocab.get(word, vocab['<UNK>']) for word in words]
    if len(seq) < max_length:
        seq += [vocab['<PAD>']] * (max_length - len(seq))
    else:
        seq = seq[:max_length]
    return seq

class SentimentAnalyzer:
    def __init__(self):
        self.model_path = Path(__file__).parent / 'sentiment_cnn.pth'
        self.vocab_path = Path(__file__).parent / 'vocab.pkl'
        self.max_length = 50
        self.model = None
        self.vocab = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.load_model()
    
    def load_model(self):
        if not self.model_path.exists() or not self.vocab_path.exists():
            raise FileNotFoundError("Model files not found. Train model first.")
        
        with open(self.vocab_path, 'rb') as f:
            self.vocab = pickle.load(f)
        
        # Force CPU to avoid CUDA compatibility issues
        self.device = torch.device('cpu')
        
        self.model = SentimentCNN(len(self.vocab))
        self.model.load_state_dict(torch.load(self.model_path, map_location=self.device))
        self.model.to(self.device)
        self.model.eval()
    
    def predict(self, text):
        seq = torch.tensor([text_to_sequence(text, self.vocab, self.max_length)]).to(self.device)
        
        with torch.no_grad():
            output = self.model(seq)
            probs = torch.softmax(output, dim=1)[0]
            sentiment_idx = torch.argmax(probs).item()
            confidence = probs[sentiment_idx].item()
        
        sentiment_map = {0: 'negative', 1: 'neutral', 2: 'positive'}
        
        return {
            'sentiment': sentiment_map[sentiment_idx],
            'confidence': round(confidence, 2)
        }

_analyzer = None

def get_analyzer():
    global _analyzer
    if _analyzer is None:
        _analyzer = SentimentAnalyzer()
    return _analyzer