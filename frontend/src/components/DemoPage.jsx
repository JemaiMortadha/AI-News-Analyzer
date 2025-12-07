import React, { useState, useEffect } from 'react'
import AnalyzerForm from './AnalyzerForm'
import AnalysesHistory from './AnalysesHistory'
import '../OldApp.css'

const DemoPage = () => {
    const [articles, setArticles] = useState([])
    const [loading, setLoading] = useState(false)
    const [refreshTrigger, setRefreshTrigger] = useState(0)

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
    }, [refreshTrigger])

    const handleAnalysisComplete = () => {
        setRefreshTrigger(prev => prev + 1)
    }

    return (
        <div className="demo-page-wrapper">
            <div className="app">
                <header className="header">
                    <h1>🤖 AI News Analyzer</h1>
                    <p>Analyze sentiment of news articles using Deep Learning</p>
                </header>

                <main className="main">
                    <AnalyzerForm onAnalysisComplete={handleAnalysisComplete} />
                    <AnalysesHistory articles={articles} loading={loading} />
                </main>
            </div>
        </div>
    )
}

export default DemoPage
