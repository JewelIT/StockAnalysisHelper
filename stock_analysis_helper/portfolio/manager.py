"""Portfolio Manager for handling user's stock and crypto holdings"""

import json
import yaml
from typing import Dict, List, Optional
from pathlib import Path


class PortfolioManager:
    """Manages user's portfolio of stocks and cryptocurrencies"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize portfolio manager
        
        Args:
            config_path: Path to portfolio configuration file (JSON or YAML)
        """
        self.config_path = config_path
        self.portfolio = {
            "stocks": [],
            "crypto": [],
            "watchlist": []
        }
        
        if config_path:
            self.load_portfolio(config_path)
    
    def load_portfolio(self, config_path: str) -> None:
        """
        Load portfolio from configuration file
        
        Args:
            config_path: Path to configuration file
        """
        path = Path(config_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Portfolio configuration file not found: {config_path}")
        
        with open(path, 'r') as f:
            if path.suffix in ['.yaml', '.yml']:
                self.portfolio = yaml.safe_load(f)
            elif path.suffix == '.json':
                self.portfolio = json.load(f)
            else:
                raise ValueError(f"Unsupported file format: {path.suffix}")
    
    def save_portfolio(self, output_path: str) -> None:
        """
        Save portfolio to configuration file
        
        Args:
            output_path: Path to save configuration
        """
        path = Path(output_path)
        
        with open(path, 'w') as f:
            if path.suffix in ['.yaml', '.yml']:
                yaml.dump(self.portfolio, f, default_flow_style=False)
            elif path.suffix == '.json':
                json.dump(self.portfolio, f, indent=2)
            else:
                raise ValueError(f"Unsupported file format: {path.suffix}")
    
    def add_stock(self, symbol: str, shares: float, purchase_price: float) -> None:
        """
        Add a stock to portfolio
        
        Args:
            symbol: Stock ticker symbol
            shares: Number of shares
            purchase_price: Price per share at purchase
        """
        self.portfolio["stocks"].append({
            "symbol": symbol.upper(),
            "shares": shares,
            "purchase_price": purchase_price
        })
    
    def add_crypto(self, symbol: str, amount: float, purchase_price: float) -> None:
        """
        Add cryptocurrency to portfolio
        
        Args:
            symbol: Crypto symbol (e.g., BTC, ETH)
            amount: Amount of crypto
            purchase_price: Price per unit at purchase
        """
        self.portfolio["crypto"].append({
            "symbol": symbol.upper(),
            "amount": amount,
            "purchase_price": purchase_price
        })
    
    def add_to_watchlist(self, symbol: str, asset_type: str = "stock") -> None:
        """
        Add symbol to watchlist
        
        Args:
            symbol: Symbol to watch
            asset_type: Type of asset (stock or crypto)
        """
        self.portfolio["watchlist"].append({
            "symbol": symbol.upper(),
            "type": asset_type
        })
    
    def get_all_symbols(self) -> List[str]:
        """Get all symbols in portfolio and watchlist"""
        symbols = []
        
        for stock in self.portfolio.get("stocks", []):
            symbols.append(stock["symbol"])
        
        for crypto in self.portfolio.get("crypto", []):
            symbols.append(crypto["symbol"] + "-USD")
        
        for item in self.portfolio.get("watchlist", []):
            if item["type"] == "crypto":
                symbols.append(item["symbol"] + "-USD")
            else:
                symbols.append(item["symbol"])
        
        return list(set(symbols))
    
    def get_portfolio_summary(self) -> Dict:
        """Get summary of portfolio"""
        return {
            "total_stocks": len(self.portfolio.get("stocks", [])),
            "total_crypto": len(self.portfolio.get("crypto", [])),
            "watchlist_items": len(self.portfolio.get("watchlist", [])),
            "stocks": self.portfolio.get("stocks", []),
            "crypto": self.portfolio.get("crypto", []),
            "watchlist": self.portfolio.get("watchlist", [])
        }
