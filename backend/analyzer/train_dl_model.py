#!/usr/bin/env python
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
import pickle
from pathlib import Path
from collections import Counter

import pandas as pd

# Load with explicit parameters
df = pd.read_csv('dataset.csv', quoting=1)  # QUOTE_ALL

# Convert sentiment to int
df['sentiment'] = pd.to_numeric(df['sentiment'], errors='coerce')
df = df.dropna()
df['sentiment'] = df['sentiment'].astype(int)

# Verify
print(f"\nPositive: {(df['sentiment']==2).sum()}")
print(f"Negative: {(df['sentiment']==0).sum()}")
print(f"Neutral: {(df['sentiment']==1).sum()}")

texts = df['text'].tolist()
labels = df['sentiment'].tolist()

training_data = list(zip(texts, labels))

# Hyperparameters
VOCAB_SIZE = 5000
EMBEDDING_DIM = 128
NUM_FILTERS = 128
FILTER_SIZES = [3, 4, 5]
MAX_LENGTH = 50
NUM_CLASSES = 3
EPOCHS = 100
BATCH_SIZE = 8

# Build vocabulary
def build_vocab(texts):
    all_words = ' '.join(texts).lower().split()
    word_counts = Counter(all_words)
    vocab = {word: idx + 2 for idx, (word, _) in enumerate(word_counts.most_common(VOCAB_SIZE - 2))}
    vocab['<PAD>'] = 0
    vocab['<UNK>'] = 1
    return vocab

# Text to sequence
def text_to_sequence(text, vocab, max_length):
    words = text.lower().split()
    seq = [vocab.get(word, vocab['<UNK>']) for word in words]
    if len(seq) < max_length:
        seq += [vocab['<PAD>']] * (max_length - len(seq))
    else:
        seq = seq[:max_length]
    return seq

# Dataset
class SentimentDataset(Dataset):
    def __init__(self, texts, labels, vocab):
        self.texts = [text_to_sequence(text, vocab, MAX_LENGTH) for text in texts]
        self.labels = labels
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        return torch.tensor(self.texts[idx]), torch.tensor(self.labels[idx])

# CNN Model
class SentimentCNN(nn.Module):
    def __init__(self, vocab_size, embedding_dim, num_filters, filter_sizes, num_classes):
        super(SentimentCNN, self).__init__()
        
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        
        self.convs = nn.ModuleList([
            nn.Conv1d(embedding_dim, num_filters, kernel_size=fs)
            for fs in filter_sizes
        ])
        
        self.dropout = nn.Dropout(0.5)
        self.fc = nn.Linear(len(filter_sizes) * num_filters, num_classes)
    
    def forward(self, x):
        # x: (batch_size, seq_len)
        embedded = self.embedding(x)  # (batch_size, seq_len, embedding_dim)
        embedded = embedded.permute(0, 2, 1)  # (batch_size, embedding_dim, seq_len)
        
        conved = [torch.relu(conv(embedded)) for conv in self.convs]
        pooled = [torch.max_pool1d(conv, conv.shape[2]).squeeze(2) for conv in conved]
        
        cat = torch.cat(pooled, dim=1)
        cat = self.dropout(cat)
        
        return self.fc(cat)

# Prepare data
texts, labels = zip(*training_data)
vocab = build_vocab(texts)

dataset = SentimentDataset(texts, labels, vocab)
dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)

# Device configuration
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")

# Initialize model
model = SentimentCNN(len(vocab), EMBEDDING_DIM, NUM_FILTERS, FILTER_SIZES, NUM_CLASSES).to(device)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Training
print("Training CNN model...")
for epoch in range(EPOCHS):
    total_loss = 0
    for texts_batch, labels_batch in dataloader:
        # Move data to device
        texts_batch = texts_batch.to(device)
        labels_batch = labels_batch.to(device)
        
        optimizer.zero_grad()
        outputs = model(texts_batch)
        loss = criterion(outputs, labels_batch)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    
    if (epoch + 1) % 10 == 0:
        print(f'Epoch [{epoch+1}/{EPOCHS}], Loss: {total_loss/len(dataloader):.4f}')

# Save model and vocab
model_dir = Path(__file__).parent
torch.save(model.state_dict(), model_dir / 'sentiment_cnn.pth')

with open(model_dir / 'vocab.pkl', 'wb') as f:
    pickle.dump(vocab, f)

print("\n✅ CNN Model trained and saved!")

# Test
model.eval()
test_texts = [
    "This is amazing news!",
    "Terrible accident occurred",
    "The meeting will be held tomorrow"
]

sentiment_map = {0: 'negative', 1: 'neutral', 2: 'positive'}

with torch.no_grad():
    for text in test_texts:
        seq = torch.tensor([text_to_sequence(text, vocab, MAX_LENGTH)]).to(device)
        output = model(seq)
        pred = torch.softmax(output, dim=1)
        sentiment_idx = torch.argmax(pred).item()
        confidence = pred[0][sentiment_idx].item()
        print(f"\nText: '{text}'")
        print(f"Sentiment: {sentiment_map[sentiment_idx]} ({confidence:.2%})")