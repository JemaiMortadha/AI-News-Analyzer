#!/usr/bin/env python3


import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
from PIL import ImageFile
import time
from pathlib import Path

# Allow loading of truncated images
ImageFile.LOAD_TRUNCATED_IMAGES = True

# Hyperparameters
BATCH_SIZE = 32
EPOCHS = 15  # Fewer epochs needed with transfer learning
LEARNING_RATE = 0.001
IMAGE_SIZE = 224  # ResNet expects 224x224

# Device configuration
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")

def create_model():
    """
    Create ResNet18 model with custom final layer
    - Pre-trained layers: FROZEN (don't train)
    - Final layer: TRAINED from scratch on our data
    """
    # Load pre-trained ResNet18
    print("\n📥 Loading pre-trained ResNet18...")
    model = models.resnet18(pretrained=True)
    
    # Freeze all layers (don't train them)
    for param in model.parameters():
        param.requires_grad = False
    
    # Replace final layer (this is what we train!)
    # ResNet18 has 512 features before final layer
    num_features = model.fc.in_features
    model.fc = nn.Linear(num_features, 3)  # 3 classes: positive, neutral, negative
    
    print(f"✅ Model loaded! Training only final layer ({num_features} → 3)")
    print(f"   Pre-trained params: {sum(p.numel() for p in model.parameters() if not p.requires_grad):,}")
    print(f"   Trainable params: {sum(p.numel() for p in model.parameters() if p.requires_grad):,}")
    
    return model

# Data augmentation for training
train_transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(10),
    transforms.ColorJitter(brightness=0.2, contrast=0.2),
    transforms.ToTensor(),
    # ImageNet normalization (required for pre-trained models)
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# Validation transform (no augmentation)
val_transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# Load datasets
print("\n📂 Loading datasets...")
train_dataset = datasets.ImageFolder('image_dataset/train', transform=train_transform)
val_dataset = datasets.ImageFolder('image_dataset/val', transform=val_transform)

print(f"Training samples: {len(train_dataset)}")
print(f"Validation samples: {len(val_dataset)}")
print(f"Classes: {train_dataset.classes}")

# Data loaders
train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=0)
val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)

# Initialize model
model = create_model().to(device)
criterion = nn.CrossEntropyLoss()

# Only optimize the final layer (the one we're training)
optimizer = optim.Adam(model.fc.parameters(), lr=LEARNING_RATE)

# Learning rate scheduler
scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=2)

# Training function
def train_epoch(model, loader, criterion, optimizer):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0
    
    for images, labels in loader:
        images, labels = images.to(device), labels.to(device)
        
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        
        running_loss += loss.item()
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()
    
    avg_loss = running_loss / len(loader)
    accuracy = 100 * correct / total
    return avg_loss, accuracy

# Validation function
def validate(model, loader, criterion):
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0
    
    with torch.no_grad():
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)
            
            running_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
    
    avg_loss = running_loss / len(loader)
    accuracy = 100 * correct / total
    return avg_loss, accuracy

# Training loop
print("\n🚀 Starting training...")
print("=" * 70)

best_val_acc = 0.0
start_time = time.time()

for epoch in range(EPOCHS):
    epoch_start = time.time()
    
    # Train
    train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer)
    
    # Validate
    val_loss, val_acc = validate(model, val_loader, criterion)
    
    # Update learning rate
    scheduler.step(val_loss)
    
    epoch_time = time.time() - epoch_start
    
    # Print progress
    print(f"Epoch [{epoch+1}/{EPOCHS}] ({epoch_time:.1f}s)")
    print(f"  Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}%")
    print(f"  Val Loss:   {val_loss:.4f} | Val Acc:   {val_acc:.2f}%")
    
    # Save best model
    if val_acc > best_val_acc:
        best_val_acc = val_acc
        torch.save(model.state_dict(), 'image_sentiment.pth')
        print(f"  ✅ Saved best model! (Val Acc: {val_acc:.2f}%)")
    
    print("-" * 70)

total_time = time.time() - start_time
print(f"\n✅ Training completed in {total_time/60:.2f} minutes!")
print(f"🏆 Best validation accuracy: {best_val_acc:.2f}%")
print(f"💾 Model saved as: image_sentiment.pth")

# Test predictions
print("\n🧪 Testing predictions...")
model.eval()
class_names = train_dataset.classes

# Get a batch of validation images
dataiter = iter(val_loader)
images, labels = next(dataiter)
images, labels = images.to(device), labels.to(device)

with torch.no_grad():
    outputs = model(images)
    _, predicted = torch.max(outputs, 1)
    probs = torch.softmax(outputs, dim=1)

# Show first 5 predictions
print("\nSample predictions:")
for i in range(min(5, len(labels))):
    actual = class_names[labels[i]]
    pred = class_names[predicted[i]]
    confidence = probs[i][predicted[i]].item()
    status = "✅" if actual == pred else "❌"
    print(f"{status} Actual: {actual:8s} | Predicted: {pred:8s} ({confidence:.2%})")

print("\n🎉 Training complete! Ready for inference.")
