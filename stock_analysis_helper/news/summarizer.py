"""News Summarizer for fetching and summarizing financial news"""

import feedparser
import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from bs4 import BeautifulSoup


class NewsSummarizer:
    """Fetches and summarizes financial news"""
    
    def __init__(self):
        """Initialize news summarizer"""
        self.news_sources = {
            "yahoo": "https://finance.yahoo.com/rss/",
            "seeking_alpha": "https://seekingalpha.com/feed.xml"
        }
    
    def fetch_news_from_rss(self, url: str, max_items: int = 10) -> List[Dict]:
        """
        Fetch news from RSS feed
        
        Args:
            url: RSS feed URL
            max_items: Maximum number of items to fetch
            
        Returns:
            List of news articles
        """
        try:
            feed = feedparser.parse(url)
            articles = []
            
            for entry in feed.entries[:max_items]:
                articles.append({
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "published": entry.get("published", ""),
                    "summary": entry.get("summary", ""),
                    "source": feed.feed.get("title", "Unknown")
                })
            
            return articles
        except Exception as e:
            print(f"Error fetching RSS feed: {e}")
            return []
    
    def search_news_for_symbol(self, symbol: str, max_results: int = 10) -> List[Dict]:
        """
        Search for news related to a specific symbol
        
        Args:
            symbol: Stock/crypto symbol
            max_results: Maximum number of results
            
        Returns:
            List of news articles
        """
        articles = []
        
        # Yahoo Finance RSS for specific symbol
        yahoo_rss = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}&region=US&lang=en-US"
        yahoo_news = self.fetch_news_from_rss(yahoo_rss, max_results)
        articles.extend(yahoo_news)
        
        return articles[:max_results]
    
    def get_trending_news(self, max_results: int = 20) -> List[Dict]:
        """
        Get trending financial news
        
        Args:
            max_results: Maximum number of results
            
        Returns:
            List of trending news articles
        """
        articles = []
        
        # Yahoo Finance main feed
        yahoo_main = "https://feeds.finance.yahoo.com/rss/2.0/headline?region=US&lang=en-US"
        articles.extend(self.fetch_news_from_rss(yahoo_main, max_results))
        
        return articles[:max_results]
    
    def summarize_news(self, articles: List[Dict]) -> Dict:
        """
        Create a summary of news articles
        
        Args:
            articles: List of news articles
            
        Returns:
            Summary information
        """
        if not articles:
            return {
                "total_articles": 0,
                "summary": "No news articles available.",
                "articles": []
            }
        
        # Create a brief summary
        titles = [article["title"] for article in articles if article.get("title")]
        
        summary_text = f"Found {len(articles)} news articles. "
        if titles:
            summary_text += f"Top headlines include: {', '.join(titles[:3])}"
        
        return {
            "total_articles": len(articles),
            "summary": summary_text,
            "articles": articles,
            "latest_article": articles[0] if articles else None
        }
    
    def get_news_for_portfolio(self, symbols: List[str], articles_per_symbol: int = 5) -> Dict:
        """
        Get news for all symbols in portfolio
        
        Args:
            symbols: List of symbols
            articles_per_symbol: Number of articles per symbol
            
        Returns:
            Dictionary with news for each symbol
        """
        portfolio_news = {}
        
        for symbol in symbols:
            news = self.search_news_for_symbol(symbol, articles_per_symbol)
            portfolio_news[symbol] = {
                "symbol": symbol,
                "articles": news,
                "count": len(news)
            }
        
        return portfolio_news
    
    def extract_text_from_articles(self, articles: List[Dict]) -> List[str]:
        """
        Extract text content from articles for sentiment analysis
        
        Args:
            articles: List of news articles
            
        Returns:
            List of text strings
        """
        texts = []
        
        for article in articles:
            text_parts = []
            
            if article.get("title"):
                text_parts.append(article["title"])
            
            if article.get("summary"):
                text_parts.append(article["summary"])
            
            if text_parts:
                texts.append(" ".join(text_parts))
        
        return texts
