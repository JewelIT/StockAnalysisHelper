"""
Social Media Data Fetcher
Fetches sentiment data from Reddit and StockTwits (free APIs)
"""
import requests
from datetime import datetime, timedelta
import praw
import os

class SocialMediaFetcher:
    def __init__(self):
        """Initialize social media API clients"""
        self.stocktwits_base_url = "https://api.stocktwits.com/api/2"
        
        # Reddit setup (optional - requires credentials)
        self.reddit = None
        try:
            # Try to initialize Reddit if credentials are in environment
            reddit_client_id = os.getenv('REDDIT_CLIENT_ID')
            reddit_client_secret = os.getenv('REDDIT_CLIENT_SECRET')
            if reddit_client_id and reddit_client_secret:
                self.reddit = praw.Reddit(
                    client_id=reddit_client_id,
                    client_secret=reddit_client_secret,
                    user_agent="FinBertPortfolioAnalyzer/1.0"
                )
        except Exception as e:
            print(f"Reddit API not configured (optional): {e}")
    
    def fetch_stocktwits_messages(self, ticker, max_messages=30):
        """
        Fetch recent messages from StockTwits (free, no auth required)
        
        Args:
            ticker: Stock ticker symbol
            max_messages: Maximum number of messages to fetch
            
        Returns:
            List of dicts with 'text', 'created_at', 'sentiment' (if available)
        """
        messages = []
        
        try:
            url = f"{self.stocktwits_base_url}/streams/symbol/{ticker}.json"
            
            # Add headers to mimic browser request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
                'Referer': f'https://stocktwits.com/symbol/{ticker}'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'messages' in data:
                    for msg in data['messages'][:max_messages]:
                        # Extract message data
                        message_data = {
                            'text': msg.get('body', ''),
                            'created_at': msg.get('created_at', ''),
                            'source': 'StockTwits',
                            'user': msg.get('user', {}).get('username', 'Unknown')
                        }
                        
                        # StockTwits sometimes includes user sentiment tags
                        if 'entities' in msg and 'sentiment' in msg['entities']:
                            sentiment = msg['entities']['sentiment']
                            if sentiment:
                                message_data['user_sentiment'] = sentiment.get('basic', 'Unknown')
                        
                        messages.append(message_data)
                        
                print(f"✓ Fetched {len(messages)} StockTwits messages for {ticker}")
            else:
                print(f"⚠️  StockTwits API returned status {response.status_code} for {ticker}")
                # Don't raise error, just return empty list
                
        except Exception as e:
            print(f"⚠️  Could not fetch StockTwits data for {ticker}: {e}")
        
        return messages
    
    def fetch_reddit_posts(self, ticker, max_posts=20, subreddits=['wallstreetbets', 'stocks', 'investing']):
        """
        Fetch recent Reddit posts mentioning the ticker (requires Reddit API credentials)
        
        Args:
            ticker: Stock ticker symbol
            max_posts: Maximum number of posts to fetch
            subreddits: List of subreddits to search
            
        Returns:
            List of dicts with 'text', 'created_at', 'score', 'subreddit'
        """
        posts = []
        
        if not self.reddit:
            print("Reddit API not configured. Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET environment variables.")
            return posts
        
        try:
            for subreddit_name in subreddits:
                try:
                    subreddit = self.reddit.subreddit(subreddit_name)
                    
                    # Search for ticker mentions
                    for post in subreddit.search(f"${ticker} OR {ticker}", time_filter='week', limit=max_posts):
                        post_data = {
                            'text': f"{post.title}. {post.selftext[:500]}",  # Title + partial body
                            'created_at': datetime.fromtimestamp(post.created_utc).isoformat(),
                            'source': f'Reddit r/{subreddit_name}',
                            'score': post.score,
                            'url': f"https://reddit.com{post.permalink}"
                        }
                        posts.append(post_data)
                        
                        if len(posts) >= max_posts:
                            break
                    
                    if len(posts) >= max_posts:
                        break
                        
                except Exception as e:
                    print(f"Error fetching from r/{subreddit_name}: {e}")
                    continue
            
            print(f"✓ Fetched {len(posts)} Reddit posts for {ticker}")
            
        except Exception as e:
            print(f"Error fetching Reddit data for {ticker}: {e}")
        
        return posts
    
    def fetch_all_social_media(self, ticker, max_per_source=20):
        """
        Fetch from all available social media sources
        
        Args:
            ticker: Stock ticker symbol
            max_per_source: Max messages per source
            
        Returns:
            List of all social media posts/messages
        """
        all_posts = []
        
        # Fetch from StockTwits (always try)
        stocktwits_messages = self.fetch_stocktwits_messages(ticker, max_per_source)
        all_posts.extend(stocktwits_messages)
        
        # Fetch from Reddit (if configured)
        reddit_posts = self.fetch_reddit_posts(ticker, max_per_source)
        all_posts.extend(reddit_posts)
        
        # If no posts were fetched, return empty (graceful degradation)
        if not all_posts:
            print(f"ℹ️  No social media data available for {ticker}")
            print(f"   To enable social media: Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET")
        
        return all_posts
    
    @staticmethod
    def get_demo_posts(ticker):
        """
        Generate demo social media posts for testing
        (Used when APIs are unavailable)
        """
        return [
            {
                'text': f"Just bought more ${ticker}! Looking bullish for Q4 📈",
                'source': 'Demo - StockTwits',
                'created_at': '2025-10-05T10:30:00',
                'user': 'demo_trader1'
            },
            {
                'text': f"Interesting technical setup on ${ticker}. Breakout incoming?",
                'source': 'Demo - StockTwits',
                'created_at': '2025-10-05T09:15:00',
                'user': 'demo_analyst'
            },
            {
                'text': f"{ticker} earnings look promising. Long term hold for me.",
                'source': 'Demo - Reddit',
                'created_at': '2025-10-04T16:45:00',
                'score': 45
            }
        ]
