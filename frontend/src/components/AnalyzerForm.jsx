import React, { useState } from 'react'
import axios from 'axios'

const AnalyzerForm = ({ onAnalysisComplete }) => {
  const [text, setText] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!text.trim()) {
      setError('Please enter some text to analyze')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await axios.post('http://localhost:8000/api/analyze/', {
        text: text
      })
      
      setResult(response.data)
      onAnalysisComplete()
      
    } catch (err) {
      setError('Failed to analyze text. Please try again.')
      console.error('Error:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card">
      <h2>📝 Analyze News Article</h2>
      
      <form onSubmit={handleSubmit} className="form">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Enter news article text or headline here..."
          disabled={loading}
        />
        
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