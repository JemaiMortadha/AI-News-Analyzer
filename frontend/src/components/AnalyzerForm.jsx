import React, { useState } from 'react'
import axios from 'axios'

const AnalyzerForm = ({ onAnalysisComplete }) => {
  const [text, setText] = useState('')
  const [image, setImage] = useState(null)
  const [imagePreview, setImagePreview] = useState(null)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleImageChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      setImage(file)

      // Create preview
      const reader = new FileReader()
      reader.onloadend = () => {
        setImagePreview(reader.result)
      }
      reader.readAsDataURL(file)

      // Clear text when image is selected
      setText('')
    }
  }

  const handleTextChange = (e) => {
    setText(e.target.value)
    // Clear image when text is entered
    if (e.target.value && image) {
      setImage(null)
      setImagePreview(null)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    // Check if either text or image is provided
    if (!text.trim() && !image) {
      setError('Please enter text or upload an image to analyze')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      let response

      if (image) {
        // Analyze image
        const formData = new FormData()
        formData.append('image', image)

        response = await axios.post('http://localhost:8000/api/analyze-image/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
      } else {
        // Analyze text
        response = await axios.post('http://localhost:8000/api/analyze/', {
          text: text
        })
      }

      setResult(response.data)
      onAnalysisComplete()

    } catch (err) {
      setError(err.response?.data?.error || 'Failed to analyze. Please try again.')
      console.error('Error:', err)
    } finally {
      setLoading(false)
    }
  }

  const clearImage = () => {
    setImage(null)
    setImagePreview(null)
  }

  return (
    <div className="card">
      <h2>📝 Analyze News Article</h2>

      <form onSubmit={handleSubmit} className="form">
        <textarea
          value={text}
          onChange={handleTextChange}
          placeholder="Enter news article text or headline here..."
          disabled={loading || !!image}
        />

        <div style={{ margin: '1rem 0', textAlign: 'center', color: '#666' }}>
          OR
        </div>

        <div style={{ marginBottom: '1rem', textAlign: 'center' }}>
          <label
            htmlFor="image-upload"
            style={{
              display: 'inline-block',
              padding: '0.75rem 1.5rem',
              background: image ? '#4caf50' : '#2196f3',
              color: 'white',
              borderRadius: '4px',
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading ? 0.6 : 1
            }}
          >
            📷 {image ? 'Image Selected' : 'Upload Image'}
          </label>
          <input
            id="image-upload"
            type="file"
            accept="image/jpeg,image/jpg,image/png,image/gif"
            onChange={handleImageChange}
            disabled={loading || !!text}
            style={{ display: 'none' }}
          />

          {image && (
            <button
              type="button"
              onClick={clearImage}
              disabled={loading}
              style={{
                marginLeft: '1rem',
                padding: '0.75rem 1.5rem',
                background: '#f44336',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: loading ? 'not-allowed' : 'pointer'
              }}
            >
              ✕ Remove
            </button>
          )}
        </div>

        {imagePreview && (
          <div style={{ marginBottom: '1rem', textAlign: 'center' }}>
            <img
              src={imagePreview}
              alt="Preview"
              style={{
                maxWidth: '100%',
                maxHeight: '300px',
                borderRadius: '8px',
                border: '2px solid #ddd'
              }}
            />
          </div>
        )}

        <button type="submit" disabled={loading}>
          {loading ? '⏳ Analyzing...' : '🔍 Analyze Sentiment'}
        </button>
      </form>

      {error && (
        <div className="result" style={{ background: '#ffebee' }}>
          <p style={{ color: '#c62828' }}>❌ {error}</p>
        </div>
      )}

      {result && (
        <div className="result">
          <h3>Analysis Result:</h3>
          <div>
            <span className={`sentiment ${result.sentiment}`}>
              {result.sentiment.toUpperCase()}
            </span>
            <span className="confidence">
              Confidence: {(result.confidence * 100).toFixed(1)}%
            </span>
          </div>
        </div>
      )}
    </div>
  )
}

export default AnalyzerForm