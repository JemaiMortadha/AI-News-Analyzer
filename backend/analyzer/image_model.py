"""
Image Sentiment Analyzer - Inference Module
Uses Transfer Learning with ResNet18
"""

import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
from pathlib import Path

class ImageSentimentAnalyzer:
    def __init__(self):
        self.model_path = Path(__file__).parent / 'image_sentiment.pth'
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.transform = self._get_transform()
        self.load_model()
    
    def _get_transform(self):
        """Image preprocessing pipeline (same as training)"""
        return transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
    
    def load_model(self):
        """Load trained ResNet18 model"""
        if not self.model_path.exists():
            raise FileNotFoundError(
                "Model file not found. Train the model first using: python3.10 train_image_model.py"
            )
        
        # Create ResNet18 with custom final layer
        self.model = models.resnet18(pretrained=False)
        num_features = self.model.fc.in_features
        self.model.fc = nn.Linear(num_features, 3)
        
        # Load trained weights
        self.model.load_state_dict(torch.load(self.model_path, map_location=self.device))
        self.model.to(self.device)
        self.model.eval()
    
    def predict(self, image_path):
        """
        Predict sentiment from image
        
        Args:
            image_path: Path to image file
            
        Returns:
            dict: {'sentiment': str, 'confidence': float}
        """
        # Load and preprocess image
        image = Image.open(image_path).convert('RGB')
        image_tensor = self.transform(image).unsqueeze(0).to(self.device)
        
        # Predict
        with torch.no_grad():
            output = self.model(image_tensor)
            probs = torch.softmax(output, dim=1)[0]
            sentiment_idx = torch.argmax(probs).item()
            confidence = probs[sentiment_idx].item()
        
        # Map index to sentiment (alphabetical order from ImageFolder)
        sentiment_map = {0: 'negative', 1: 'neutral', 2: 'positive'}
        
        return {
            'sentiment': sentiment_map[sentiment_idx],
            'confidence': round(confidence, 2)
        }
    
    def predict_batch(self, image_paths):
        """Predict sentiment for multiple images"""
        results = []
        for image_path in image_paths:
            try:
                result = self.predict(image_path)
                result['image'] = str(image_path)
                results.append(result)
            except Exception as e:
                results.append({
                    'image': str(image_path),
                    'error': str(e)
                })
        return results

# Global instance (singleton pattern)
_analyzer = None

def get_image_analyzer():
    """Get or create image sentiment analyzer instance"""
    global _analyzer
    if _analyzer is None:
        _analyzer = ImageSentimentAnalyzer()
    return _analyzer
