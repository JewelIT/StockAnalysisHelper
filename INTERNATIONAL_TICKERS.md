# International Ticker Support

## Current Support via Yahoo Finance

The application currently uses **yfinance** which supports global markets with exchange suffixes.

## Supported Markets

### United States 🇺🇸
- Format: `TICKER`
- Examples: `AAPL`, `MSFT`, `GOOGL`, `TSLA`

### Ireland 🇮🇪
- Format: `TICKER.IR`
- Examples: `UPL.IR`, `RYA.IR`, `CRG.IR`

### United Kingdom 🇬🇧
- Format: `TICKER.L`
- Examples: `HSBA.L`, `BP.L`, `VOD.L`, `LLOY.L`

### Germany 🇩🇪
- Format: `TICKER.DE`
- Examples: `SAP.DE`, `VOW3.DE`, `BMW.DE`, `SIE.DE`

### France 🇫🇷
- Format: `TICKER.PA`
- Examples: `MC.PA`, `OR.PA`, `AI.PA`, `BNP.PA`

### Japan 🇯🇵
- Format: `CODE.T`
- Examples: `7203.T` (Toyota), `6758.T` (Sony), `9984.T` (SoftBank)

### Hong Kong 🇭🇰
- Format: `CODE.HK`
- Examples: `0700.HK` (Tencent), `0941.HK` (China Mobile)

### Canada 🇨🇦
- Format: `TICKER.TO`
- Examples: `SHOP.TO`, `TD.TO`, `RY.TO`

### Australia 🇦🇺
- Format: `TICKER.AX`
- Examples: `BHP.AX`, `CBA.AX`, `WBC.AX`

### Switzerland 🇨🇭
- Format: `TICKER.SW`
- Examples: `NESN.SW` (Nestlé), `NOVN.SW` (Novartis)

### Netherlands 🇳🇱
- Format: `TICKER.AS`
- Examples: `ASML.AS`, `INGA.AS`, `AD.AS`

### Spain 🇪🇸
- Format: `TICKER.MC`
- Examples: `TEF.MC` (Telefónica), `SAN.MC` (Santander)

### Italy 🇮🇹
- Format: `TICKER.MI`
- Examples: `UCG.MI`, `ISP.MI`, `ENI.MI`

### India 🇮🇳
- NSE: `TICKER.NS`
- BSE: `TICKER.BO`
- Examples: `RELIANCE.NS`, `TCS.NS`, `INFY.BO`

### China 🇨🇳
- Shanghai: `CODE.SS`
- Shenzhen: `CODE.SZ`
- Examples: `600519.SS` (Kweichow Moutai), `000858.SZ` (Wuliangye)

## Cryptocurrency Support

### Format: `SYMBOL-USD`
- Examples: `BTC-USD`, `ETH-USD`, `BNB-USD`, `ADA-USD`

### Format: `SYMBOL-EUR`
- Examples: `BTC-EUR`, `ETH-EUR`

## Troubleshooting

### "No data found, symbol may be delisted"
This error appears when:
1. **Missing exchange suffix** - Add the correct suffix (e.g., `UPL.IR` not `UPL`)
2. **Delisted stock** - Company no longer trades
3. **Wrong exchange** - Try different suffix
4. **Spelling error** - Verify ticker symbol

### How to Find the Correct Ticker
1. Search on Yahoo Finance: https://finance.yahoo.com/
2. Look at the URL or chart - the ticker will include the suffix
3. Example: `https://finance.yahoo.com/quote/UPL.IR` → Use `UPL.IR`

## Future Enhancements

We're considering adding alternative data sources for better coverage:
- **Alpha Vantage** - Enhanced global coverage
- **CoinGecko** - Better crypto support
- **Twelve Data** - More international markets
- **Financial Modeling Prep** - Additional data points

## Need More Markets?

If you need support for a specific market not listed here, check Yahoo Finance first. Most global exchanges are supported with the right suffix.

Common suffixes:
- `.L` = London
- `.PA` = Paris (Euronext Paris)
- `.DE` = Frankfurt (Xetra)
- `.T` = Tokyo
- `.HK` = Hong Kong
- `.TO` = Toronto
- `.AX` = Sydney
- `.NS/.BO` = India
- `.SS/.SZ` = China
