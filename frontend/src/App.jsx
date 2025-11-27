import React, { useState, useEffect } from 'react'
import AnalyzerForm from './components/AnalyzerForm'
import ArticlesList from './components/ArticlesList'
import './App.css'

function App() {
  const [articles, setArticles] = useState([])
  const [loading, setLoading] = useState(false)

  const fetchArticles = async () => {
    try {
      setLoading(true)
      const response = await fetch('http://localhost:8000/api/articles/')
      const data = await response.json()
      setArticles(data)
    } catch (error) {
      console.error('Error fetching articles:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchArticles()
  }, [])

  const handleAnalysisComplete = () => {
    fetchArticles()
  }

  return (
    <div className="app">
      <header className="header">
        <h1>🤖 AI News Analyzer</h1>
        <p>Analyze sentiment of news articles using Machine Learning</p>
      </header>

      <main className="main">
        <AnalyzerForm onAnalysisComplete={handleAnalysisComplete} />
        <ArticlesList articles={articles} loading={loading} />
      </main>

      <footer className="footer">
        <p></p>
      </footer>
    </div>
  )
}

export default App