import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { FaHeart, FaRegHeart, FaBookmark, FaRegBookmark, FaExternalLinkAlt } from 'react-icons/fa';

const ArticlesList = ({ filter = 'all' }) => {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const { user } = useAuth();

  // Filters state
  const [category, setCategory] = useState('');
  const [search, setSearch] = useState('');

  useEffect(() => {
    fetchArticles();
  }, [filter, page, category, search]);

  const fetchArticles = async () => {
    setLoading(true);
    setError(null);
    try {
      let url = '/news/';
      const params = { page };

      if (filter === 'saved') {
        url = '/news/saved/';
      } else {
        if (category) params.category = category;
        if (search) params.search = search;
      }

      const response = await axios.get(url, { params });

      if (filter === 'saved') {
        // Saved endpoint returns { results: [...] } without pagination metadata currently
        setArticles(response.data.results || []);
        setTotalPages(1);
      } else {
        setArticles(response.data.results || []);
        setTotalPages(response.data.pagination?.total_pages || 1);
      }
    } catch (err) {
      console.error('Error fetching articles:', err);
      setError('Failed to load articles. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  const handleLike = async (articleId) => {
    if (!user) return alert('Please login to like articles');
    try {
      await axios.post(`/news/${articleId}/like/`);
      // Optimistic update
      setArticles(articles.map(a => {
        if (a._id === articleId) {
          return {
            ...a,
            is_liked: !a.is_liked,
            like_count: a.is_liked ? a.like_count - 1 : a.like_count + 1
          };
        }
        return a;
      }));
    } catch (err) {
      console.error('Error liking article:', err);
    }
  };

  const handleSave = async (articleId) => {
    if (!user) return alert('Please login to save articles');
    try {
      await axios.post(`/news/${articleId}/save/`);
      // Optimistic update
      setArticles(articles.map(a => {
        if (a._id === articleId) {
          return {
            ...a,
            is_saved: !a.is_saved,
            save_count: a.is_saved ? a.save_count - 1 : a.save_count + 1
          };
        }
        return a;
      }));

      // If we are in saved view and unsave, remove it
      if (filter === 'saved') {
        setArticles(articles.filter(a => a._id !== articleId));
      }
    } catch (err) {
      console.error('Error saving article:', err);
    }
  };

  const handleView = (articleId) => {
    if (user) {
      // Fire and forget view tracking
      axios.get(`/news/${articleId}/`).catch(err => console.error("Error tracking view", err));
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short', day: 'numeric', year: 'numeric'
    });
  };

  return (
    <div className="articles-container">
      <div className="feed-header">
        <h1>{filter === 'saved' ? 'Saved Articles' : 'Latest News'}</h1>

        {filter !== 'saved' && (
          <div className="filters">
            <select
              value={category}
              onChange={(e) => { setCategory(e.target.value); setPage(1); }}
              className="category-select"
            >
              <option value="">All Categories</option>
              <option value="technology">Technology</option>
              <option value="business">Business</option>
              <option value="science">Science</option>
              <option value="health">Health</option>
              <option value="entertainment">Entertainment</option>
              <option value="sports">Sports</option>
              <option value="general">General</option>
            </select>

            <input
              type="text"
              placeholder="Search news..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && setPage(1)}
              className="search-input"
            />
          </div>
        )}
      </div>

      {loading ? (
        <div className="loading">Loading articles...</div>
      ) : error ? (
        <div className="error-message">{error}</div>
      ) : articles.length === 0 ? (
        <div className="empty-state">
          <p>No articles found.</p>
        </div>
      ) : (
        <div className="articles-grid">
          {articles.map(article => (
            <div key={article._id} className="article-card">
              {article.image_url && article.image_url !== 'None' ? (
                <div className="article-image">
                  <img
                    src={article.image_url}
                    alt={article.title}
                    onError={(e) => {
                      e.target.style.display = 'none';
                      e.target.parentElement.classList.add('no-image');
                      e.target.parentElement.innerHTML = `<div class="placeholder-image"><span class="category-icon">${article.category.toUpperCase()}</span></div>`;
                    }}
                  />
                  <span className={`sentiment-badge ${article.sentiment}`}>
                    {article.sentiment}
                  </span>
                </div>
              ) : (
                <div className="article-image no-image">
                  <div className="placeholder-image">
                    <span className="category-icon">{article.category?.toUpperCase() || 'NEWS'}</span>
                  </div>
                  <span className={`sentiment-badge ${article.sentiment}`}>
                    {article.sentiment}
                  </span>
                </div>
              )}
              <div className="article-content">
                <div className="article-meta-top">
                  <span className="source">{article.source}</span>
                  <span className="date">{formatDate(article.published_at)}</span>
                </div>

                <h3 className="article-title">
                  <a
                    href={article.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    onClick={() => handleView(article._id)}
                  >
                    {article.title}
                  </a>
                </h3>

                <p className="article-desc">
                  {article.description ? article.description.substring(0, 120) + '...' : ''}
                </p>

                <div className="article-actions">
                  <div className="action-buttons">
                    <button
                      onClick={() => handleLike(article._id)}
                      className={`btn-action ${article.is_liked ? 'liked' : ''}`}
                    >
                      {article.is_liked ? <FaHeart /> : <FaRegHeart />}
                      <span>{article.like_count}</span>
                    </button>

                    <button
                      onClick={() => handleSave(article._id)}
                      className={`btn-action ${article.is_saved ? 'saved' : ''}`}
                    >
                      {article.is_saved ? <FaBookmark /> : <FaRegBookmark />}
                    </button>
                  </div>

                  <a
                    href={article.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="read-more"
                    onClick={() => handleView(article._id)}
                  >
                    Read <FaExternalLinkAlt />
                  </a>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {totalPages > 1 && (
        <div className="pagination">
          <button
            disabled={page === 1}
            onClick={() => setPage(p => p - 1)}
            className="btn-page"
          >
            Previous
          </button>
          <span className="page-info">Page {page} of {totalPages}</span>
          <button
            disabled={page === totalPages}
            onClick={() => setPage(p => p + 1)}
            className="btn-page"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
};

export default ArticlesList;