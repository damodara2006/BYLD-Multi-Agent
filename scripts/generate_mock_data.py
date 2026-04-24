import json
import os
from pathlib import Path
from typing import List, Dict

def generate_portfolio() -> List[Dict]:
    return [
        {"ticker": "RELIANCE.NS", "holding_name": "Reliance Industries Limited", "sector": "Energy", "instrument_type": "Equity", "quantity": 50, "avg_cost": 2400.50, "current_price": 2850.00, "currency": "INR"},
        {"ticker": "HDFCBANK.NS", "holding_name": "HDFC Bank Limited", "sector": "Financials", "instrument_type": "Equity", "quantity": 100, "avg_cost": 1500.00, "current_price": 1450.75, "currency": "INR"},
        {"ticker": "TCS.NS", "holding_name": "Tata Consultancy Services", "sector": "IT", "instrument_type": "Equity", "quantity": 25, "avg_cost": 3200.00, "current_price": 3900.20, "currency": "INR"},
        {"ticker": "INFY.NS", "holding_name": "Infosys Limited", "sector": "IT", "instrument_type": "Equity", "quantity": 75, "avg_cost": 1400.80, "current_price": 1420.50, "currency": "INR"},
        {"ticker": "ITC.NS", "holding_name": "ITC Limited", "sector": "FMCG", "instrument_type": "Equity", "quantity": 300, "avg_cost": 210.00, "current_price": 420.30, "currency": "INR"},
        {"ticker": "ICICIBANK.NS", "holding_name": "ICICI Bank Limited", "sector": "Financials", "instrument_type": "Equity", "quantity": 80, "avg_cost": 800.50, "current_price": 1050.00, "currency": "INR"},
        {"ticker": "SBI.NS", "holding_name": "State Bank of India", "sector": "Financials", "instrument_type": "Equity", "quantity": 120, "avg_cost": 450.00, "current_price": 750.00, "currency": "INR"},
        {"ticker": "BHARTIARTL.NS", "holding_name": "Bharti Airtel Limited", "sector": "Telecommunication", "instrument_type": "Equity", "quantity": 60, "avg_cost": 650.00, "current_price": 1150.80, "currency": "INR"},
        {"ticker": "HUL.NS", "holding_name": "Hindustan Unilever Limited", "sector": "FMCG", "instrument_type": "Equity", "quantity": 40, "avg_cost": 2300.25, "current_price": 2250.00, "currency": "INR"},
        {"ticker": "LARSEN.NS", "holding_name": "Larsen & Toubro Limited", "sector": "Industrials", "instrument_type": "Equity", "quantity": 30, "avg_cost": 1900.00, "current_price": 3600.50, "currency": "INR"},
        {"ticker": "BAJFINANCE.NS", "holding_name": "Bajaj Finance Limited", "sector": "Financials", "instrument_type": "Equity", "quantity": 15, "avg_cost": 5500.00, "current_price": 7000.00, "currency": "INR"},
        {"ticker": "SGB2024.NS", "holding_name": "Sovereign Gold Bond 2024", "sector": "Commodity", "instrument_type": "Bond", "quantity": 50, "avg_cost": 5000.00, "current_price": 6200.00, "currency": "INR"},
        {"ticker": "NIFTYBEES.NS", "holding_name": "Nippon India ETF Nifty 50 BeES", "sector": "Market Index", "instrument_type": "ETF", "quantity": 200, "avg_cost": 200.50, "current_price": 250.75, "currency": "INR"},
        {"ticker": "ZOMATO.NS", "holding_name": "Zomato Limited", "sector": "Consumer Discretionary", "instrument_type": "Equity", "quantity": 500, "avg_cost": 60.00, "current_price": 180.50, "currency": "INR"},
        {"ticker": "INDIGO.NS", "holding_name": "InterGlobe Aviation Limited", "sector": "Aviation", "instrument_type": "Equity", "quantity": 20, "avg_cost": 1800.00, "current_price": 3100.00, "currency": "INR"},
        {"ticker": "PPFAS-FLEXI.MF", "holding_name": "Parag Parikh Flexi Cap Direct Growth", "sector": "Diversified Equity", "instrument_type": "Mutual Fund", "quantity": 1540.5, "avg_cost": 55.20, "current_price": 74.80, "currency": "INR"},
    ]

def generate_news(base_path: Path):
    news_items = [
        {"title": "Reliance AGM Announcements Highlight New Green Energy Push", "tickers": "RELIANCE.NS", "content": "Reliance Industries detailed their expansive plan for renewable energy over the next decade. The board committed billions to solar and hydrogen initiatives. Market analysts are extremely bullish on the long-term prospects."},
        {"title": "HDFC Bank Reports Q3 Earnings Amid Margin Pressures", "tickers": "HDFCBANK.NS", "content": "HDFC Bank continues to show strong loan growth, but net interest margins (NIM) remain under pressure following the recent merger. Retail deposits have surged, providing a stable base for future lending efforts."},
        {"title": "TCS Wins Mega Deal in European Banking Sector", "tickers": "TCS.NS", "content": "Tata Consultancy Services secured a multi-year IT transformation contract worth $1.5 billion with a leading European bank. This bolsters their order book and showcases strong pipeline demand despite global macro uncertainties."},
        {"title": "Infosys Adjusts Revenue Guidance Downwards for the Fiscal Year", "tickers": "INFY.NS", "content": "In a surprising move, Infosys has slightly lowered its upper-end revenue guidance, citing delayed decision-making by clients in the US region. However, their operating margin target remains steadfast."},
        {"title": "ITC Hotel Business Demerger Update", "tickers": "ITC.NS", "content": "ITC Limited has finalized the sharing ratio for the demerger of its hotel business. Shareholders will receive 1 share of the independent entity for every 10 shares held in ITC, unlocking specific intrinsic value."},
        {"title": "ICICI Bank Posts Record Low Non-Performing Assets", "tickers": "ICICIBANK.NS", "content": "Driven by robust collection strategies and a cleaner corporate book, ICICI Bank posted its lowest Gross NPA ratio in a decade. The stock soared 3% in early morning trading as a response to the stellar asset quality."},
        {"title": "SBI Unveils Plans to Expand YONO App Globally", "tickers": "SBI.NS", "content": "State Bank of India is looking to take its comprehensive digital banking platform, YONO, to international markets, starting with Southeast Asia. This move aims to tap into the NRI diaspora looking for seamless integrations."},
        {"title": "Bharti Airtel ARPU Hits New High Following Tariff Hikes", "tickers": "BHARTIARTL.NS", "content": "Benefiting from recent premiumization shifts and entry-level tariff hikes, Bharti Airtel reported an industry-leading Average Revenue Per User (ARPU). Telecom analysts predict further steady growth in the next two quarters."},
        {"title": "HUL Manages Inflationary Headwinds with Tactical Pricing", "tickers": "HUL.NS", "content": "Hindustan Unilever Limited has skillfully navigated raw material cost fluctuations through calibrated price adjustments and changes in packaging sizes. Rural demand is also showing green shoots of recovery."},
        {"title": "Larsen & Toubro Secures Mega Infrastructure Contract in the Middle East", "tickers": "LARSEN.NS", "content": "The infrastructure giant, Larsen & Toubro, has bagged another 'Mega' contract (worth over Rs 7000 crores) for a high-speed rail corridor project in the Middle East. Order inflows for the quarter exceed estimates."},
        {"title": "Bajaj Finance Introduces New Features to EMI Network Card", "tickers": "BAJFINANCE.NS", "content": "To compete with rising credit card penetrations, Bajaj Finance revamped its EMI Network platform. Customers can now access higher limits for travel and healthcare, aiming to retain market share in consumer durable financing."},
        {"title": "Sovereign Gold Bonds Series Launch Sees Heavy Subscription", "tickers": "SGB2024.NS", "content": "The latest tranche of RBI's Sovereign Gold Bonds witnessed enormous retail participation. Amid global geopolitical tensions, investors are flocking to gold as a safe haven, supplemented by the 2.5% annual fixed interest."},
        {"title": "Nifty 50 Hits All-Time High Led by Banking Heavyweights", "tickers": "NIFTYBEES.NS, HDFCBANK.NS, ICICIBANK.NS", "content": "A sudden rush of Foreign Institutional Investor (FII) buying propelled the Nifty 50 index to an unprecedented all-time high today. The surge was largely driven by leading private banks beating market earnings expectations."},
        {"title": "Zomato Reports Consecutive Quarters of Profitability", "tickers": "Zomato.NS", "content": "Food delivery giant Zomato continues to defy early skeptics by posting its third consecutive profitable quarter. Blinkit, its quick commerce arm, achieved EBITDA breakeven much earlier than anticipated."},
        {"title": "IndiGo Expands Fleet with Massive Airbus Order", "tickers": "INDIGO.NS", "content": "InterGlobe Aviation, operating as IndiGo, placed a historic order for 500 Airbus A320neo family aircraft. This aggressive capacity expansion aims to cement their dominance in India's rapidly growing domestic aviation market."},
        {"title": "RBI Keeps Repo Rate Unchanged at 6.5%", "tickers": "GENERAL", "content": "The Reserve Bank of India’s Monetary Policy Committee unanimously decided to keep the benchmark repo rate unchanged for the fifth consecutive time, citing balanced inflation and growth dynamics in the domestic economy."},
        {"title": "SEBI Mandates Stricter T+0 Settlement Framework Guidelines", "tickers": "GENERAL", "content": "The Securities and Exchange Board of India (SEBI) has released a consultation paper aiming to transition the Indian equity markets to an optional T+0 (same day) trade settlement cycle, improving overall liquidity."},
        {"title": "Government Slashes Windfall Tax on Domestic Crude", "tickers": "RELIANCE.NS", "content": "In a major relief to domestic oil producers, the central government has significantly reduced the windfall profit tax on domestically produced crude oil, responding to the recent softening of global benchmark Brent crude prices."},
        {"title": "Tech Stocks Rally on Hints of US Fed Rate Cuts", "tickers": "TCS.NS, INFY.NS", "content": "Indian IT service companies saw a sharp rally following dovish comments from the US Federal Reserve. A potential cut in US interest rates could revive discretionary technology spending among North American clients."},
        {"title": "Monsoon Forecast Looks Favorable for FMCG Sector", "tickers": "ITC.NS, HUL.NS", "content": "The Indian Meteorological Department has predicted an above-normal monsoon for the upcoming season. This outlook is a massive booster for FMCG companies counting on rural income recovery to drive volume growth."}
    ]
    
    for i, item in enumerate(news_items, 1):
        filename = base_path / f"news_{i:02d}.md"
        content = f"---\nDate: 2026-04-24\nTickers: {item['tickers']}\n---\n\n# {item['title']}\n\n{item['content']}\n"
        with open(filename, 'w') as f:
            f.write(content)

def generate_glossary(base_path: Path):
    terms = [
        "- **STT (Securities Transaction Tax)**: A tax levied on all transactions processing on the recognized stock exchanges in India.",
        "- **SIP (Systematic Investment Plan)**: A facility offered by mutual funds allowing investors to invest a fixed amount regularly at predefined intervals.",
        "- **XIRR (Extended Internal Rate of Return)**: A metric used to calculate returns on investments where there are multiple transactions happening at different times.",
        "- **NFO (New Fund Offer)**: The first time a new mutual fund scheme is launched and open for subscription by the asset management company.",
        "- **AUM (Assets Under Management)**: The total market value of the investments managed by a mutual fund, venture capital firm, or brokerage house.",
        "- **NAV (Net Asset Value)**: Represents the per unit/share price of the mutual fund on a specific date or time.",
        "- **ETF (Exchange Traded Fund)**: A type of investment fund and exchange-traded product tracking an underlying asset or index, traded on the stock market.",
        "- **CAGR (Compound Annual Growth Rate)**: The mean annual growth rate of an investment over a specified period of time longer than one year.",
        "- **KYC (Know Your Customer)**: The mandatory process of identifying and verifying the client's identity when opening an account according to SEBI regulations.",
        "- **Demat Account**: An account used to hold shares and securities in electronic format, required for trading in the Indian stock market.",
        "- **Dividend Yield**: A financial ratio that shows how much a company pays out in dividends each year relative to its stock price.",
        "- **Repo Rate**: The rate at which the central bank (RBI) of India lends money to commercial banks in the event of any shortfall of funds.",
        "- **Sensex**: The benchmark index of the BSE (Bombay Stock Exchange) comprising 30 of the largest and most actively traded stocks.",
        "- **Nifty 50**: The flagship benchmark index of the National Stock Exchange (NSE) representing the weighted average of 50 of the largest Indian companies.",
        "- **Retail Investor**: An individual or non-professional investor who buys and sells securities, mutual funds, or ETFs through traditional or online brokerage firms.",
        "- **STCG (Short-Term Capital Gains)**: Profit from the sale of listed equity shares or equity-oriented mutual funds held for less than 12 months, taxed at a flat rate of 20% under Section 111A of the Income Tax Act.",
        "- **LTCG (Long-Term Capital Gains)**: Profit from the sale of listed equity shares or equity-oriented mutual funds held for more than 12 months, taxed at 12.5% on gains exceeding Rs 1.25 lakh in a financial year under Section 112A.",
    ]
    
    with open(base_path / "glossary.md", 'w') as f:
        f.write("# BYLD Wealth Glossary\n\n" + "\n".join(terms) + "\n")

if __name__ == "__main__":
    data_dir = Path("data")
    news_dir = data_dir / "news"
    
    data_dir.mkdir(exist_ok=True)
    news_dir.mkdir(exist_ok=True)
    
    # Write Portfolio
    with open(data_dir / "portfolio.json", 'w') as f:
        json.dump(generate_portfolio(), f, indent=4)
        
    # Write News
    generate_news(news_dir)
    
    # Write Glossary
    generate_glossary(data_dir)
    
    print("Mock data generated successfully in './data/'.")
