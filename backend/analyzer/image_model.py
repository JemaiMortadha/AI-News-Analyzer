import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import requests
from io import BytesIO
from pathlib import Path
import os

class ImageSentimentAnalyzer:
    def __init__(self):
        self.model_path = Path(__file__).parent / 'image_sentiment.pth'
        self.device = torch.device('cpu') # Force CPU for inference stability
        self.model = None
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        self.classes = ['negative', 'neutral', 'positive'] # Assuming these are the classes from training
        self.load_model()

    def create_model(self):
        """Recreate the model architecture used in training"""
        model = models.resnet18(pretrained=False) # No need to download pretrained weights, we load ours
        num_features = model.fc.in_features
        model.fc = nn.Linear(num_features, 3)
        return model

    def load_model(self):
        if not self.model_path.exists():
            print(f"Warning: Image model not found at {self.model_path}")
            return
        
        try:
            self.model = self.create_model()
            self.model.load_state_dict(torch.load(self.model_path, map_location=self.device))
            self.model.to(self.device)
            self.model.eval()
        except Exception as e:
            print(f"Error loading image model: {e}")

    def predict(self, image_source):
        """
        Predict sentiment from image.
        image_source: can be a URL string or a PIL Image object
        """
        if not self.model:
            return {'sentiment': 'neutral', 'confidence': 0.0}

        try:
            img = None
            if isinstance(image_source, str):
                # Download image
                response = requests.get(image_source, timeout=10, stream=True)
                response.raise_for_status()
                img = Image.open(BytesIO(response.content)).convert('RGB')
            else:
                img = image_source.convert('RGB')

            # Preprocess
            img_tensor = self.transform(img).unsqueeze(0).to(self.device)

            # Inference
            with torch.no_grad():
                outputs = self.model(img_tensor)
                probs = torch.softmax(outputs, dim=1)[0]
                sentiment_idx = torch.argmax(probs).item()
                confidence = probs[sentiment_idx].item()

            return {
                'sentiment': self.classes[sentiment_idx],
                'confidence': round(confidence, 2)
            }

        except Exception as e:
            print(f"Image analysis error: {e}")
            return {'sentiment': 'neutral', 'confidence': 0.0}

_image_analyzer = None

def get_image_analyzer():
    global _image_analyzer
    if _image_analyzer is None:
        _image_analyzer = ImageSentimentAnalyzer()
    return _image_analyzer
