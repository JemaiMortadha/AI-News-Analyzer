# 🤖 AI News Analyzer

A full-stack web application that analyzes the sentiment of news articles using Machine Learning.

## 🔧 Tech Stack

- **Frontend:** React.js (Vite)
- **Backend:** Django + Django REST Framework
- **Database:** MongoDB
- **Machine Learning:** Scikit-learn (TfidfVectorizer + MultinomialNB)
- **Containerization:** Docker & Docker Compose

## ✨ Features

- 📝 Analyze sentiment of news articles (Positive, Neutral, Negative)
- 🎯 Confidence score for each prediction
- 💾 Store analyzed articles in MongoDB
- 📊 View last 10 analyzed articles
- 🎨 Clean and responsive UI
- 🐳 Fully containerized with Docker

## 🚀 Quick Start

### Prerequisites

- Docker Desktop installed
- Docker Compose installed

### Run the Application

1. **Clone or create the project structure**

2. **Start all services:**

```bash
docker-compose up --build