import React, { useState } from 'react';
import axios from 'axios';

const AnalyzerDemo = () => {
    const [text, setText] = useState('');
    const [imageFile, setImageFile] = useState(null);
    const [imagePreview, setImagePreview] = useState(null);
    const [textResult, setTextResult] = useState(null);
    const [imageResult, setImageResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleImageSelect = (e) => {
        const file = e.target.files[0];
        if (file) {
            setImageFile(file);
            const reader = new FileReader();
            reader.onloadend = () => {
                setImagePreview(reader.result);
            };
            reader.readAsDataURL(file);
        }
    };

    const analyzeText = async () => {
        if (!text.trim()) {
            setError('Please enter some text to analyze');
            return;
        }

        setLoading(true);
        setError(null);
        try {
            const response = await axios.post('/analyze/', { text });
            setTextResult(response.data);
        } catch (err) {
            setError('Failed to analyze text: ' + (err.response?.data?.error || err.message));
        } finally {
            setLoading(false);
        }
    };

    const analyzeImage = async () => {
        if (!imageFile) {
            setError('Please select an image to analyze');
            return;
        }

        setLoading(true);
        setError(null);
        try {
            const formData = new FormData();
            formData.append('image', imageFile);

            const response = await axios.post('/analyze-image/', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            setImageResult(response.data);
        } catch (err) {
            setError('Failed to analyze image: ' + (err.response?.data?.error || err.message));
        } finally {
            setLoading(false);
        }
    };

    const getSentimentColor = (sentiment) => {
        switch (sentiment?.toLowerCase()) {
            case 'positive': return '#22c55e';
            case 'negative': return '#ef4444';
            case 'neutral': return '#64748b';
            default: return '#94a3b8';
        }
    };

    return (
        <div className="demo-container">
            <div className="demo-header">
                <h1>🤖 AI Sentiment Analyzer Demo</h1>
                <p>Test the Deep Learning models for text and image sentiment analysis</p>
            </div>

            <div className="demo-grid">
                {/* Text Analysis Section */}
                <div className="demo-card">
                    <h2>📝 Text Sentiment Analysis</h2>
                    <p className="demo-description">Using CNN model trained on sentiment data</p>

                    <textarea
                        value={text}
                        onChange={(e) => setText(e.target.value)}
                        placeholder="Enter text to analyze sentiment..."
                        rows="4"
                        className="demo-textarea"
                    />

                    <button
                        onClick={analyzeText}
                        disabled={loading || !text.trim()}
                        className="btn-analyze"
                    >
                        {loading ? 'Analyzing...' : 'Analyze Text'}
                    </button>

                    {textResult && (
                        <div className="result-card" style={{ borderColor: getSentimentColor(textResult.sentiment) }}>
                            <div className="result-label">Sentiment</div>
                            <div
                                className="result-sentiment"
                                style={{ color: getSentimentColor(textResult.sentiment) }}
                            >
                                {textResult.sentiment?.toUpperCase()}
                            </div>
                            <div className="result-confidence">
                                Confidence: {(textResult.confidence * 100).toFixed(1)}%
                            </div>
                        </div>
                    )}
                </div>

                {/* Image Analysis Section */}
                <div className="demo-card">
                    <h2>🖼️ Image Sentiment Analysis</h2>
                    <p className="demo-description">Using ResNet18 model with transfer learning</p>

                    <div className="image-upload">
                        <input
                            type="file"
                            accept="image/*"
                            onChange={handleImageSelect}
                            id="image-input"
                            style={{ display: 'none' }}
                        />
                        <label htmlFor="image-input" className="upload-label">
                            {imagePreview ? 'Change Image' : 'Select Image'}
                        </label>
                    </div>

                    {imagePreview && (
                        <div className="image-preview">
                            <img src={imagePreview} alt="Preview" />
                        </div>
                    )}

                    <button
                        onClick={analyzeImage}
                        disabled={loading || !imageFile}
                        className="btn-analyze"
                    >
                        {loading ? 'Analyzing...' : 'Analyze Image'}
                    </button>

                    {imageResult && (
                        <div className="result-card" style={{ borderColor: getSentimentColor(imageResult.sentiment) }}>
                            <div className="result-label">Sentiment</div>
                            <div
                                className="result-sentiment"
                                style={{ color: getSentimentColor(imageResult.sentiment) }}
                            >
                                {imageResult.sentiment?.toUpperCase()}
                            </div>
                            <div className="result-confidence">
                                Confidence: {(imageResult.confidence * 100).toFixed(1)}%
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {error && (
                <div className="error-banner">{error}</div>
            )}
        </div>
    );
};

export default AnalyzerDemo;
