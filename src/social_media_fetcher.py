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
        
        # Create a session for persistent connections
        self.session = requests.Session()
        
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
        Fetch recent messages from StockTwits using public API (no auth required)
        
        Public API endpoint: https://api.stocktwits.com/api/2/streams/symbol/{TICKER}.json
        
        Args:
            ticker: Stock ticker symbol
            max_messages: Maximum number of messages to fetch
            
        Returns:
            List of dicts with 'text', 'created_at', 'sentiment' (if available)
        """
        messages = []
        
        try:
            url = f"{self.stocktwits_base_url}/streams/symbol/{ticker}.json"
            
            # Add headers to mimic browser request and avoid rate limiting
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Referer': f'https://stocktwits.com/symbol/{ticker}',
                'Origin': 'https://stocktwits.com',
                'Connection': 'keep-alive',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-site'
            }
            
            response = self.session.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'messages' in data:
                    for msg in data['messages'][:max_messages]:
                        # Extract message data
                        message_id = msg.get('id', '')
                        message_data = {
                            'text': msg.get('body', ''),
                            'created_at': msg.get('created_at', ''),
                            'source': 'StockTwits',
                            'user': msg.get('user', {}).get('username', 'Unknown'),
                            # Construct link to the post
                            'link': f'https://stocktwits.com/message/{message_id}' if message_id else ''
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
                if response.status_code == 403:
                    print(f"   StockTwits may be rate limiting or blocking automated requests.")
                    print(f"   Continuing with Reddit data only...")
                # Don't raise error, just return empty list - NO DEMO DATA
                
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
                            'link': f"https://reddit.com{post.permalink}"  # Consistent field name
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
    
    def fetch_all_social_media(self, ticker, max_per_source=20, days=7):
        """
        Fetch from all available social media sources
        
        Args:
            ticker: Stock ticker symbol
            max_per_source: Max messages per source
            days: Maximum age of posts in days (default: 7)
            
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
        
        # If no posts were fetched, just return empty list - NO FAKE DATA
        if not all_posts:
            print(f"ℹ️  No social media data available for {ticker}")
            print(f"   To enable more sources:")
            print(f"   - Reddit: Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET environment variables")
            print(f"   - StockTwits free API has rate limits and may return 403 errors")
            return []  # Return empty list instead of demo data
        
        # Filter posts by age
        from datetime import datetime, timedelta, timezone
        import logging
        logger = logging.getLogger(__name__)
        
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        filtered_posts = []
        for post in all_posts:
            created_at = post.get('created_at', '')
            if created_at:
                try:
                    # Handle multiple timestamp formats
                    if isinstance(created_at, (int, float)):
                        # Unix timestamp
                        post_date = datetime.fromtimestamp(created_at, tz=timezone.utc)
                    elif isinstance(created_at, str):
                        # Try ISO format first (most common for social media APIs)
                        if 'T' in created_at or '+' in created_at or created_at.endswith('Z'):
                            post_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                            # Ensure timezone-aware
                            if post_date.tzinfo is None:
                                post_date = post_date.replace(tzinfo=timezone.utc)
                        else:
                            # Try other common formats
                            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%d/%m/%Y %H:%M:%S', '%m/%d/%Y %H:%M:%S']:
                                try:
                                    post_date = datetime.strptime(created_at, fmt).replace(tzinfo=timezone.utc)
                                    break
                                except ValueError:
                                    continue
                            else:
                                # No format worked, log it
                                logger.warning(f"Unrecognized date format for social media post: '{created_at}' (type: {type(created_at).__name__})")
                                filtered_posts.append(post)
                                continue
                    else:
                        logger.warning(f"Unexpected timestamp type for social media post: {type(created_at).__name__} = {created_at}")
                        filtered_posts.append(post)
                        continue
                    
                    if post_date >= cutoff_date:
                        filtered_posts.append(post)
                except (ValueError, TypeError, OSError) as e:
                    # If date parsing fails, log and include the post
                    logger.warning(f"Failed to parse social media date '{created_at}': {str(e)}")
                    filtered_posts.append(post)
            else:
                # Include posts without timestamp
                filtered_posts.append(post)
        
        return filtered_posts
    
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
