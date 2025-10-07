import React from 'react'

const ArticlesList = ({ articles, loading }) => {
  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (loading) {
    return (
      <div className="card">
        <h2>📚 Recent Analyses</h2>
        <div className="loading">Loading...</div>
      </div>
    )
  }

  return (
    <div className="card">
      <h2>📚 Recent Analyses ({articles.length})</h2>
      
      {articles.length === 0 ? (
        <div className="empty">
          <p>No articles analyzed yet.</p>
          <p>Start by analyzing your first article!</p>
        </div>
      ) : (
        <div className="articles-list">
          {articles.map((article) => (
            <div key={article._id} className="article-item">
              <p className="article-text">{article.text}</p>
              <div className="article-meta">
                <div>
                  <span className={`sentiment ${article.sentiment}`}>
                    {article.sentiment}
                  </span>
                  <span className="confidence">
                    {(article.confidence * 100).toFixed(1)}%
                  </span>
                </div>
                <span className="article-date">
                  {formatDate(article.created_at)}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default ArticlesList