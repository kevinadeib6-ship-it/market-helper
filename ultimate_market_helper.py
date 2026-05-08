"""
Ultimate Market Helper
======================

A beginner-friendly terminal stock market contest assistant.

What it does:
- Uses an optional editable stock list or HTMW CSV import.
- Shows contest-focused scanners instead of an account/portfolio screen.
- Gives AI-style Buy / Sell / Hold suggestions using moving averages,
  momentum, and trend analysis.
- Adds risk labels, volatility, stop-loss ideas, and take-profit ideas.
- Prints alert flags for large moves and technical changes.
- Adds HowTheMarketWorks-style contest helpers for position limits,
  commissions, minimum price rules, and trade planning.
- Scans top movers from a watchlist.
- Prints latest stock news headlines when yfinance provides them.
- Saves each refresh to a CSV history file.
- Auto-refreshes every 60 seconds.
- Uses colored terminal output with colorama.

Required pip installs:
    pip install yfinance pandas colorama

How to run:
    python ultimate_market_helper.py

How to edit your portfolio:
    Change the PORTFOLIO dictionary below. The key is the stock ticker and the
    value is the number of shares you own.

How to connect HowTheMarketWorks safely:
    Export or copy your HTMW Open Positions report into a CSV file named
    htmw_open_positions.csv and save it in this same folder. The script will
    auto-load it if it finds ticker and shares/quantity columns.

Important note:
    This script is for education and contest research only. It is not financial
    advice. Always make your own decisions.
"""

from __future__ import annotations

import os
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path
import traceback
from typing import Dict, Iterable, List, Tuple

import pandas as pd
import yfinance as yf
from colorama import Fore, Style, init


# Starts colorama so colored output works on Windows, macOS, and Linux.
init(autoreset=True)

# Keep saved files next to this script, even if you launch it from another
# folder such as C:\Windows\system32.
SCRIPT_DIR = Path(__file__).resolve().parent
HTMW_PORTFOLIO_CSV = SCRIPT_DIR / "htmw_open_positions.csv"


# -----------------------------
# Easy-to-edit settings
# -----------------------------

# Edit this portfolio whenever your contest positions change.
PORTFOLIO: Dict[str, float] = {
    "AAPL": 5,
    "TSLA": 2,
    "NVDA": 3,
    "AMZN": 1,
    "META": 2,
}

# If this is True, the script will replace PORTFOLIO with positions loaded
# from htmw_open_positions.csv when that file exists.
LOAD_HTMW_PORTFOLIO_CSV = True

# If your stock contest gives you uninvested cash, put it here.
# HowTheMarketWorks contests can have custom rules. Update these to match the
# rules shown inside your specific contest before using the trade planner.
HTMW_STARTING_CASH = 100000.00
HTMW_POSITION_LIMIT_PERCENT = 25.0
HTMW_COMMISSION_PER_TRADE = 10.00
HTMW_MIN_BUY_PRICE = 1.00
HTMW_DAY_TRADING_ALLOWED = False
HTMW_SHORT_SELLING_ALLOWED = False
HTMW_MARGIN_ALLOWED = False
HTMW_CONTEST_END_DATE = ""  # Example: "2026-06-01", or leave blank.

# Add more symbols here if you want the top movers scanner to watch more stocks.
WATCHLIST: List[str] = [
    "AAPL",
    "MSFT",
    "GOOGL",
    "GOOG",
    "AMZN",
    "META",
    "NVDA",
    "TSLA",
    "AMD",
    "INTC",
    "QCOM",
    "MU",
    "ARM",
    "NFLX",
    "AVGO",
    "ORCL",
    "CRM",
    "ADBE",
    "NOW",
    "SHOP",
    "UBER",
    "ABNB",
    "JPM",
    "BAC",
    "GS",
    "MS",
    "C",
    "AXP",
    "V",
    "MA",
    "LLY",
    "JNJ",
    "PFE",
    "MRK",
    "ABBV",
    "TMO",
    "UNH",
    "COST",
    "WMT",
    "TGT",
    "HD",
    "MCD",
    "SBUX",
    "NKE",
    "DIS",
    "PEP",
    "KO",
    "PG",
    "XOM",
    "CVX",
    "COP",
    "GE",
    "CAT",
    "BA",
    "LMT",
    "PLTR",
    "COIN",
    "SMCI",
    "RIVN",
    "SOFI",
    "HOOD",
    "ROKU",
    "SNOW",
    "CRWD",
    "NET",
    "DDOG",
    "ZS",
    "MSTR",
    "SPY",
    "QQQ",
    "DIA",
    "IWM",
    "DOW",
    "HON",
    "RTX",
    "NOC",
    "GD",
    "DE",
    "MMM",
    "UPS",
    "FDX",
    "CSX",
    "UNP",
    "GM",
    "F",
    "TM",
    "HMC",
    "LI",
    "NIO",
    "XPEV",
    "LCID",
    "MRNA",
    "BMY",
    "GILD",
    "REGN",
    "VRTX",
    "ISRG",
    "ZTS",
    "CVS",
    "ELV",
    "CI",
    "HUM",
    "WFC",
    "SCHW",
    "BLK",
    "BX",
    "PYPL",
    "SQ",
    "AFRM",
    "RBLX",
    "U",
    "PATH",
    "AI",
    "IONQ",
    "RGTI",
    "QBTS",
    "MARA",
    "RIOT",
    "CLSK",
    "WULF",
    "HUT",
    "DKNG",
    "PENN",
    "MGM",
    "WYNN",
    "LVS",
    "DAL",
    "UAL",
    "AAL",
    "LUV",
    "CCL",
    "RCL",
    "NCLH",
    "BKNG",
    "EXPE",
    "MAR",
    "HLT",
    "CMG",
    "YUM",
    "DPZ",
    "BROS",
    "CELH",
    "MNST",
    "KDP",
    "CL",
    "KMB",
    "MDLZ",
    "KHC",
    "T",
    "VZ",
    "TMUS",
    "CMCSA",
    "PARA",
    "WBD",
    "SPOT",
    "PINS",
    "SNAP",
    "BABA",
    "PDD",
    "JD",
    "BIDU",
    "SE",
    "MELI",
    "TSM",
    "ASML",
    "NXPI",
    "TXN",
    "ADI",
    "MRVL",
    "LRCX",
    "KLAC",
    "AMAT",
    "ASX",
    "ON",
    "ENPH",
    "FSLR",
    "SEDG",
    "NEE",
    "DUK",
    "SO",
    "AEP",
    "O",
    "PLD",
    "AMT",
    "EQIX",
    "SLB",
    "HAL",
    "OXY",
    "EOG",
    "MPC",
    "PSX",
    "VLO",
    "NEM",
    "GOLD",
    "FCX",
    "CLF",
    "X",
    "NUE",
    "MOS",
    "CF",
    "TAN",
    "ARKK",
    "ARKG",
    "ARKW",
    "XLE",
    "XLK",
    "XLF",
    "XLV",
    "XLY",
    "XLI",
    "XLU",
    "XLP",
    "XLB",
    "XLRE",
    "SMH",
    "SOXX",
    "IBB",
    "XBI",
    "KWEB",
    "HYG",
    "TLT",
    "GLD",
    "SLV",
]

# Extra contest names that are not just the same mega-cap favorites. This adds
# smaller growth, turnaround, international, commodity, volatility, and niche ETF
# ideas so the scanners have more variety to work with.
WATCHLIST.extend(
    [
        "WING",
        "SHAK",
        "CAVA",
        "SG",
        "SFM",
        "W",
        "CHWY",
        "ETSY",
        "FIVE",
        "OLLI",
        "BURL",
        "ANF",
        "GAP",
        "CROX",
        "DECK",
        "ONON",
        "LULU",
        "ELF",
        "ULTA",
        "KVUE",
        "RIVN",
        "QS",
        "CHPT",
        "BLNK",
        "RUN",
        "BE",
        "PLUG",
        "FCEL",
        "ACHR",
        "JOBY",
        "RKLB",
        "ASTS",
        "LUNR",
        "SOUN",
        "BBAI",
        "SERV",
        "TEM",
        "RXRX",
        "SDGR",
        "CRSP",
        "EDIT",
        "BEAM",
        "NTLA",
        "DNA",
        "SAVA",
        "VKTX",
        "IOVA",
        "TGTX",
        "GERN",
        "NBIS",
        "ALAB",
        "VRT",
        "APP",
        "TTD",
        "MDB",
        "ESTC",
        "OKTA",
        "TWLO",
        "DOCU",
        "BILL",
        "HIMS",
        "OSCR",
        "CLOV",
        "OPEN",
        "UPST",
        "NU",
        "TME",
        "YMM",
        "GRAB",
        "CPNG",
        "S",
        "GENI",
        "SKLZ",
        "MTCH",
        "BMBL",
        "IOT",
        "GTLB",
        "RPD",
        "FROG",
        "PCOR",
        "TOST",
        "DUOL",
        "COUR",
        "ZI",
        "RKT",
        "UWMC",
        "RDFN",
        "Z",
        "ZG",
        "COMP",
        "AA",
        "SCCO",
        "TECK",
        "VALE",
        "RIO",
        "BHP",
        "WPM",
        "PAAS",
        "AG",
        "U",
        "CCJ",
        "UUUU",
        "UEC",
        "URNM",
        "URA",
        "BOIL",
        "KOLD",
        "UNG",
        "USO",
        "DBA",
        "WEAT",
        "CORN",
        "SOYB",
        "VXX",
        "UVXY",
        "SVXY",
        "BITO",
        "IBIT",
        "FBTC",
        "ETHE",
        "EEM",
        "EWZ",
        "EWJ",
        "INDA",
        "EWT",
        "EWY",
        "FXI",
        "EFA",
    ]
)

# Remove accidental duplicates and a few stale ticker symbols while preserving
# order. These stale symbols can create noisy yfinance warnings.
STALE_OR_RENAMED_SYMBOLS = {"SQ", "PARA", "RDFN", "ZI", "X"}
WATCHLIST = [
    symbol
    for symbol in dict.fromkeys(WATCHLIST)
    if symbol not in STALE_OR_RENAMED_SYMBOLS
]

# Leveraged ETFs can move much faster than normal stocks. They can be useful
# in contests, but they also add major risk and are usually poor long-term holds.
THREE_X_ETFS: List[str] = [
    "TQQQ",  # 3x Nasdaq 100 bull
    "SQQQ",  # 3x Nasdaq 100 bear
    "UPRO",  # 3x S&P 500 bull
    "SPXU",  # 3x S&P 500 bear
    "SOXL",  # 3x semiconductor bull
    "SOXS",  # 3x semiconductor bear
    "FNGU",  # 3x big tech bull ETN
    "FNGD",  # 3x big tech bear ETN
    "LABU",  # 3x biotech bull
    "LABD",  # 3x biotech bear
    "TECL",  # 3x technology bull
    "TECS",  # 3x technology bear
    "BULZ",  # 3x technology-focused bull ETN
    "BERZ",  # 3x technology-focused bear ETN
    "DFEN",  # 3x aerospace and defense bull
    "DRN",   # 3x real estate bull
    "TNA",   # 3x small-cap bull
    "TZA",   # 3x small-cap bear
    "UDOW",  # 3x Dow bull
    "SDOW",  # 3x Dow bear
    "FAS",   # 3x financial bull
    "FAZ",   # 3x financial bear
    "DPST",  # 3x regional banks bull
    "NAIL",  # 3x homebuilders bull
    "RETL",  # 3x retail bull
    "GUSH",  # 2x oil and gas bull
    "DRIP",  # 2x oil and gas bear
    "NUGT",  # 2x gold miners bull
    "DUST",  # 2x gold miners bear
    "YINN",  # 3x China bull
    "YANG",  # 3x China bear
    "EDC",   # 3x emerging markets bull
    "EDZ",   # 3x emerging markets bear
    "TMF",   # 3x long bonds bull
    "TMV",   # 3x long bonds bear
    "ERX",   # 2x energy bull, useful if your contest allows leveraged ETFs
    "ERY",   # 2x energy bear, useful if your contest allows leveraged ETFs
]

REFRESH_SECONDS = 30
HISTORY_PERIOD = "1y"
HISTORY_INTERVAL = "1d"
INTRADAY_PERIOD = "1d"
INTRADAY_INTERVAL = "15m"
FAST_REFRESH_MODE = True
SHOW_NEWS_BREAKOUTS = True
NEWS_BREAKOUT_SYMBOL_LIMIT = 30
NEWS_HEADLINES_PER_STOCK = 2
TOP_MOVERS_TO_SHOW = 20
TOP_CONTEST_IDEAS_TO_SHOW = 20
TOP_15_MIN_LOOKBACK_TO_SHOW = 20
MIN_CONTEST_CANDIDATE_SCORE = 5.0
EXPORT_CSV_FILE = SCRIPT_DIR / "market_helper_history.csv"
ERROR_LOG_FILE = SCRIPT_DIR / "market_helper_errors.log"

# Alerts make noisy market days easier to spot at a glance.
BIG_MOVE_ALERT_PERCENT = 3.0
HIGH_VOLATILITY_ALERT_PERCENT = 4.0
CONCENTRATION_WARNING_PERCENT = 35.0

# Keep the interface calm and mostly white. Set to False if you want stronger
# red/green/yellow colors throughout the dashboard.
CLEAN_WHITE_UI = True

# Fast mode only checks the most useful short-term names for the 15-minute
# lookback scanner instead of downloading intraday candles for every ticker.
FAST_INTRADAY_SYMBOLS: List[str] = [
    "TSLA",
    "NVDA",
    "AMD",
    "AAPL",
    "META",
    "AMZN",
    "MSFT",
    "GOOGL",
    "PLTR",
    "COIN",
    "MSTR",
    "SOFI",
    "HOOD",
    "CRWD",
    "NET",
    "DDOG",
    "SNOW",
    "TQQQ",
    "SQQQ",
    "SOXL",
    "SOXS",
    "UPRO",
    "SPXU",
    "TNA",
    "TZA",
    "LABU",
    "LABD",
    "UVXY",
    "VXX",
    "SOUN",
    "RKLB",
    "ASTS",
    "ACHR",
    "JOBY",
    "RGTI",
    "IONQ",
    "MARA",
    "RIOT",
    "IBIT",
    "BITO",
]

NEWS_BREAKOUT_KEYWORDS = {
    "earnings": 3,
    "beats": 3,
    "beat": 2,
    "raises": 3,
    "raised": 2,
    "guidance": 2,
    "upgrade": 3,
    "upgraded": 3,
    "buy rating": 3,
    "partnership": 2,
    "deal": 2,
    "contract": 2,
    "approval": 3,
    "fda": 3,
    "launch": 2,
    "breakout": 2,
    "surges": 3,
    "rallies": 2,
    "record": 2,
    "acquisition": 2,
    "merger": 2,
    "ai": 1,
}

NEWS_RISK_KEYWORDS = {
    "misses": -3,
    "miss": -2,
    "cuts": -3,
    "cut": -2,
    "downgrade": -3,
    "downgraded": -3,
    "sell rating": -3,
    "lawsuit": -3,
    "investigation": -3,
    "probe": -2,
    "delay": -2,
    "delayed": -2,
    "recall": -3,
    "layoffs": -2,
    "bankruptcy": -5,
    "fraud": -4,
    "plunges": -3,
    "falls": -2,
}


# -----------------------------
# Terminal helpers
# -----------------------------

def clear_screen() -> None:
    """Clear the terminal so each refresh looks like a fresh dashboard."""
    os.system("cls" if os.name == "nt" else "clear")


def money(value: float) -> str:
    """Format a number as dollars."""
    return f"${value:,.2f}"


def pct(value: float) -> str:
    """Format a number as a percentage."""
    return f"{value:+.2f}%"


def color_for_change(value: float) -> str:
    """Choose green for positive numbers, red for negative numbers."""
    if CLEAN_WHITE_UI:
        return Fore.WHITE
    if value > 0:
        return Fore.GREEN
    if value < 0:
        return Fore.RED
    return Fore.WHITE


def color_for_signal(signal: str) -> str:
    """Choose a color based on the suggestion."""
    if CLEAN_WHITE_UI:
        return Fore.WHITE
    if signal == "BUY":
        return Fore.GREEN
    if signal == "SELL":
        return Fore.RED
    return Fore.YELLOW


def terminal_width() -> int:
    """Return a practical terminal width for drawing clean dashboard lines."""
    return max(90, min(shutil.get_terminal_size((110, 30)).columns, 130))


def dashboard_rule(color: str = Fore.CYAN) -> str:
    """Create a horizontal rule that fits the current terminal."""
    if CLEAN_WHITE_UI:
        color = Fore.WHITE
    return color + "=" * terminal_width()


def trim_text(text: str, max_length: int) -> str:
    """Shorten long text so news and reasons do not wreck the layout."""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3].rstrip() + "..."


def metric_card(label: str, value: str, color: str = Fore.WHITE, width: int = 27) -> str:
    """Create a compact one-line metric card for the account summary."""
    clean_value = trim_text(value, width - len(label) - 5)
    if CLEAN_WHITE_UI:
        color = Fore.WHITE
    return color + f"[ {label}: {clean_value} ]".ljust(width)


def signal_badge(signal: str) -> str:
    """Return a colored signal badge that is easy to scan."""
    if CLEAN_WHITE_UI:
        return Fore.WHITE + f"{signal:^6}" + Style.RESET_ALL
    return color_for_signal(signal) + f"[{signal:^6}]" + Style.RESET_ALL


def risk_badge(risk_label: str) -> str:
    """Return a colored risk badge."""
    if CLEAN_WHITE_UI:
        return Fore.WHITE + f"{risk_label:^7}" + Style.RESET_ALL
    if risk_label == "High":
        color = Fore.RED
    elif risk_label == "Medium":
        color = Fore.YELLOW
    elif risk_label == "Low":
        color = Fore.GREEN
    else:
        color = Fore.WHITE
    return color + f"[{risk_label:^7}]" + Style.RESET_ALL


def progress_bar(value: float, width: int = 24) -> str:
    """Create an ASCII progress bar for allocation percentages."""
    filled = max(0, min(width, int(round((value / 100) * width))))
    return "|" + "#" * filled + "." * (width - filled) + "|"


def print_title(text: str) -> None:
    """Print a dashboard section title in a consistent style."""
    print(Fore.WHITE + Style.BRIGHT + f"\n{text.upper()}")
    print(Fore.WHITE + "-" * terminal_width())


def log_error(exc: Exception) -> None:
    """Save unexpected errors so crashes are easier to diagnose."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with ERROR_LOG_FILE.open("a", encoding="utf-8") as file:
            file.write(f"\n[{timestamp}] {type(exc).__name__}: {exc}\n")
            file.write(traceback.format_exc())
            file.write("\n")
    except Exception:
        print(Fore.RED + "Could not write the error log file.")
        print(traceback.format_exc())


# -----------------------------
# Market data helpers
# -----------------------------

def safe_download(symbols: Iterable[str], period: str, interval: str) -> pd.DataFrame:
    """
    Download market history with yfinance.

    yfinance can sometimes return empty data if markets are closed, a ticker is
    invalid, or the internet connection is having a rough moment. This wrapper
    keeps the rest of the dashboard from crashing.
    """
    try:
        data = yf.download(
            tickers=list(symbols),
            period=period,
            interval=interval,
            group_by="ticker",
            auto_adjust=True,
            progress=False,
            # Fast mode uses parallel requests. If yfinance ever complains
            # about a cache lock, set FAST_REFRESH_MODE to False.
            threads=FAST_REFRESH_MODE,
        )
        return data if isinstance(data, pd.DataFrame) else pd.DataFrame()
    except Exception as exc:
        print(Fore.RED + f"Could not download market data: {exc}")
        return pd.DataFrame()


def find_column(columns: Iterable[str], possible_names: Iterable[str]) -> str | None:
    """Find a CSV column by comparing lowercase cleaned names."""
    cleaned_columns = {
        str(column).strip().lower().replace(" ", "").replace("_", ""): str(column)
        for column in columns
    }

    for name in possible_names:
        cleaned_name = name.strip().lower().replace(" ", "").replace("_", "")
        if cleaned_name in cleaned_columns:
            return cleaned_columns[cleaned_name]

    return None


def load_htmw_portfolio_from_csv() -> Dict[str, float] | None:
    """
    Load positions from an exported HTMW Open Positions CSV.

    This avoids storing your login or password. You export/copy your positions
    from HTMW, save them as htmw_open_positions.csv next to this script, and the
    dashboard reads the symbols and share counts.
    """
    if not LOAD_HTMW_PORTFOLIO_CSV or not HTMW_PORTFOLIO_CSV.exists():
        return None

    try:
        positions = pd.read_csv(HTMW_PORTFOLIO_CSV)
    except Exception as exc:
        print(Fore.WHITE + f"Could not read {HTMW_PORTFOLIO_CSV.name}: {exc}")
        return None

    ticker_column = find_column(
        positions.columns,
        ["ticker", "symbol", "stock", "security", "ticker symbol"],
    )
    shares_column = find_column(
        positions.columns,
        ["shares", "quantity", "qty", "shares owned", "open quantity"],
    )

    if not ticker_column or not shares_column:
        print(
            Fore.WHITE
            + f"{HTMW_PORTFOLIO_CSV.name} was found, but I could not find ticker "
            + "and shares columns."
        )
        return None

    loaded_portfolio: Dict[str, float] = {}
    for _, row in positions.iterrows():
        symbol = str(row.get(ticker_column, "")).strip().upper()
        shares = pd.to_numeric(row.get(shares_column, 0), errors="coerce")

        if not symbol or symbol == "NAN" or pd.isna(shares) or float(shares) == 0:
            continue

        loaded_portfolio[symbol] = loaded_portfolio.get(symbol, 0.0) + float(shares)

    return loaded_portfolio or None


def active_portfolio() -> Dict[str, float]:
    """Return HTMW CSV positions when available, otherwise the manual portfolio."""
    imported_portfolio = load_htmw_portfolio_from_csv()
    return imported_portfolio if imported_portfolio else PORTFOLIO


def get_symbol_history(all_data: pd.DataFrame, symbol: str) -> pd.DataFrame:
    """
    Pull one ticker's OHLCV history from a yfinance download result.

    yfinance returns a slightly different column shape when one ticker is
    requested versus many tickers, so this function handles both.
    """
    if all_data.empty:
        return pd.DataFrame()

    if isinstance(all_data.columns, pd.MultiIndex):
        if symbol not in all_data.columns.get_level_values(0):
            return pd.DataFrame()
        history = all_data[symbol].copy()
    else:
        history = all_data.copy()

    needed_columns = {"Open", "High", "Low", "Close", "Volume"}
    if not needed_columns.intersection(history.columns):
        return pd.DataFrame()

    return history.dropna(subset=["Close"])


def latest_price(history: pd.DataFrame) -> float:
    """Return the latest closing price from a stock history table."""
    if history.empty or "Close" not in history:
        return 0.0
    return float(history["Close"].iloc[-1])


def daily_change_percent(history: pd.DataFrame) -> float:
    """Calculate the latest one-day percentage move."""
    if history.empty or len(history) < 2:
        return 0.0
    latest = float(history["Close"].iloc[-1])
    previous = float(history["Close"].iloc[-2])
    if previous == 0:
        return 0.0
    return ((latest - previous) / previous) * 100


def daily_profit_loss(history: pd.DataFrame, shares: float) -> float:
    """Estimate today's dollar profit or loss for one position."""
    if history.empty or len(history) < 2:
        return 0.0
    latest = float(history["Close"].iloc[-1])
    previous = float(history["Close"].iloc[-2])
    return (latest - previous) * shares


def calculate_risk_metrics(history: pd.DataFrame) -> Dict[str, float | str]:
    """
    Estimate simple risk information from recent daily returns.

    Volatility is the typical size of the daily moves over the last 30 trading
    days. This is not perfect, but it is easy to understand and useful for
    contest decision-making.
    """
    if history.empty or len(history) < 35:
        return {
            "volatility": 0.0,
            "risk_label": "Unknown",
            "support": 0.0,
            "resistance": 0.0,
            "stop_loss": 0.0,
            "take_profit": 0.0,
        }

    closes = history["Close"]
    current = float(closes.iloc[-1])
    returns = closes.pct_change().dropna().tail(30)
    volatility = float(returns.std() * 100)
    support = float(closes.tail(20).min())
    resistance = float(closes.tail(20).max())

    if volatility >= 4:
        risk_label = "High"
    elif volatility >= 2:
        risk_label = "Medium"
    else:
        risk_label = "Low"

    # A simple contest-style stop and target. You can customize these numbers.
    stop_loss = min(current * 0.95, support)
    take_profit = max(current * 1.08, resistance)

    return {
        "volatility": volatility,
        "risk_label": risk_label,
        "support": support,
        "resistance": resistance,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
    }


def trading_days_until_contest_end() -> int | None:
    """Estimate trading days left if you filled in HTMW_CONTEST_END_DATE."""
    if not HTMW_CONTEST_END_DATE:
        return None

    try:
        today = pd.Timestamp.today().normalize()
        end_date = pd.Timestamp(HTMW_CONTEST_END_DATE).normalize()
    except Exception:
        return None

    if end_date < today:
        return 0

    days = pd.bdate_range(today, end_date)
    return max(0, len(days) - 1)


def max_position_value(contest_size: float) -> float:
    """Calculate the largest allowed dollar value for one holding."""
    return contest_size * (HTMW_POSITION_LIMIT_PERCENT / 100)


def max_new_shares_allowed(price: float, room_to_buy: float) -> int:
    """Calculate how many whole shares fit inside the position-limit room."""
    usable_cash = max(0.0, room_to_buy - HTMW_COMMISSION_PER_TRADE)
    if price <= 0 or usable_cash <= 0:
        return 0
    return int(usable_cash // price)


def setup_label(signal: str, trend: str, volatility: float, change: float) -> str:
    """Create a short scanner label that explains the kind of setup."""
    if signal == "BUY" and trend == "Uptrend" and volatility <= 4:
        return "Clean momentum"
    if signal == "BUY" and volatility > 4:
        return "High-risk pop"
    if change > BIG_MOVE_ALERT_PERCENT:
        return "Breakout watch"
    if change < -BIG_MOVE_ALERT_PERCENT:
        return "Dip risk"
    if signal == "SELL":
        return "Avoid/weak"
    return "Watchlist"


def leveraged_etf_type(symbol: str) -> str:
    """Label common leveraged ETF direction."""
    bear_symbols = {
        "SQQQ",
        "SPXU",
        "SOXS",
        "FNGD",
        "LABD",
        "TECS",
        "BERZ",
        "TZA",
        "SDOW",
        "FAZ",
        "DRIP",
        "DUST",
        "YANG",
        "EDZ",
        "TMV",
        "ERY",
    }
    bull_symbols = {
        "TQQQ",
        "UPRO",
        "SOXL",
        "FNGU",
        "LABU",
        "TECL",
        "BULZ",
        "DFEN",
        "DRN",
        "TNA",
        "UDOW",
        "FAS",
        "DPST",
        "NAIL",
        "RETL",
        "GUSH",
        "NUGT",
        "YINN",
        "EDC",
        "TMF",
        "ERX",
    }
    if symbol in bear_symbols:
        return "Bear"
    if symbol in bull_symbols:
        return "Bull"
    return "Leveraged"


# -----------------------------
# AI-style analysis
# -----------------------------

def analyze_stock(history: pd.DataFrame) -> Dict[str, object]:
    """
    Create a simple AI-style rating using common technical indicators.

    This is intentionally beginner friendly:
    - Moving averages show whether price is above or below recent averages.
    - Momentum checks whether price has moved up or down over recent days.
    - Trend analysis compares short-term and long-term moving averages.
    """
    if history.empty or len(history) < 60:
        return {
            "signal": "HOLD",
            "score": 0,
            "reason": "Not enough history for a confident technical read.",
            "ma20": 0.0,
            "ma50": 0.0,
            "ma200": 0.0,
            "momentum_5d": 0.0,
            "momentum_20d": 0.0,
            "trend": "Unknown",
        }

    closes = history["Close"]
    current = float(closes.iloc[-1])
    ma20 = float(closes.rolling(20).mean().iloc[-1])
    ma50 = float(closes.rolling(50).mean().iloc[-1])
    ma200_series = closes.rolling(200).mean()
    ma200 = float(ma200_series.iloc[-1]) if not pd.isna(ma200_series.iloc[-1]) else 0.0
    momentum_5d = ((current - float(closes.iloc[-6])) / float(closes.iloc[-6])) * 100
    momentum_20d = ((current - float(closes.iloc[-21])) / float(closes.iloc[-21])) * 100

    score = 0
    reasons: List[str] = []

    if current > ma20:
        score += 1
        reasons.append("price is above the 20-day average")
    else:
        score -= 1
        reasons.append("price is below the 20-day average")

    if ma20 > ma50:
        score += 1
        reasons.append("short-term trend is above the 50-day trend")
    else:
        score -= 1
        reasons.append("short-term trend is below the 50-day trend")

    if ma200 and current > ma200:
        score += 1
        reasons.append("price is above the 200-day long-term trend")
    elif ma200:
        score -= 1
        reasons.append("price is below the 200-day long-term trend")

    if momentum_5d > 2:
        score += 1
        reasons.append("5-day momentum is strong")
    elif momentum_5d < -2:
        score -= 1
        reasons.append("5-day momentum is weak")
    else:
        reasons.append("5-day momentum is neutral")

    if momentum_20d > 5:
        score += 1
        reasons.append("20-day momentum is strong")
    elif momentum_20d < -5:
        score -= 1
        reasons.append("20-day momentum is weak")
    else:
        reasons.append("20-day momentum is neutral")

    if score >= 2:
        signal = "BUY"
    elif score <= -2:
        signal = "SELL"
    else:
        signal = "HOLD"

    if current > ma20 > ma50:
        trend = "Uptrend"
    elif current < ma20 < ma50:
        trend = "Downtrend"
    else:
        trend = "Mixed"

    return {
        "signal": signal,
        "score": score,
        "reason": "; ".join(reasons) + ".",
        "ma20": ma20,
        "ma50": ma50,
        "ma200": ma200,
        "momentum_5d": momentum_5d,
        "momentum_20d": momentum_20d,
        "trend": trend,
    }


# -----------------------------
# Dashboard sections
# -----------------------------

def build_portfolio_rows(
    all_data: pd.DataFrame,
    portfolio: Dict[str, float],
) -> Tuple[List[Dict[str, object]], float, float]:
    """Create reusable portfolio rows for display and CSV export."""
    rows: List[Dict[str, object]] = []
    tracked_value = 0.0
    daily_pl_total = 0.0

    for symbol, shares in portfolio.items():
        history = get_symbol_history(all_data, symbol)
        price = latest_price(history)
        change = daily_change_percent(history)
        daily_pl = daily_profit_loss(history, shares)
        analysis = analyze_stock(history)
        risk = calculate_risk_metrics(history)
        value = shares * price

        tracked_value += value
        daily_pl_total += daily_pl

        rows.append(
            {
                "symbol": symbol,
                "shares": shares,
                "price": price,
                "change": change,
                "daily_pl": daily_pl,
                "value": value,
                "analysis": analysis,
                "risk": risk,
            }
        )

    for row in rows:
        row["allocation"] = (
            (float(row["value"]) / tracked_value) * 100 if tracked_value else 0.0
        )

    return rows, tracked_value, daily_pl_total


def show_contest_summary() -> None:
    """Print a contest-focused summary instead of an account/portfolio box."""
    print_title("HTMW Contest Summary")
    cards = [
        metric_card("Contest Size", money(HTMW_STARTING_CASH), Fore.WHITE + Style.BRIGHT),
        metric_card("Max Holding", money(max_position_value(HTMW_STARTING_CASH)), Fore.WHITE),
        metric_card("Daily Symbols", str(len(set(WATCHLIST) | set(THREE_X_ETFS))), Fore.WHITE),
        metric_card("Refresh", f"{REFRESH_SECONDS}s", Fore.WHITE),
    ]
    print(" ".join(cards))
    print(Fore.WHITE + f"HTMW CSV import: {'on' if HTMW_PORTFOLIO_CSV.exists() else 'not found'}")


def show_portfolio(rows: List[Dict[str, object]]) -> None:
    """Print portfolio positions with allocation, risk, and suggestions."""
    print_title("Portfolio Tracker")
    print(
        Style.BRIGHT
        + f"{'Ticker':<7}{'Shares':>8}{'Price':>11}{'Day %':>9}"
        + f"{'P/L':>11}{'Value':>13}{'Alloc':>8}{'Risk':>11}{'Signal':>11}"
    )
    print(Fore.WHITE + "-" * terminal_width())

    for row in rows:
        symbol = str(row["symbol"])
        shares = float(row["shares"])
        price = float(row["price"])
        change = float(row["change"])
        daily_pl = float(row["daily_pl"])
        value = float(row["value"])
        allocation = float(row["allocation"])
        analysis = row["analysis"]
        risk = row["risk"]
        change_color = color_for_change(change)
        pl_color = color_for_change(daily_pl)
        signal = str(analysis["signal"])
        signal_color = color_for_signal(signal)
        risk_label = str(risk["risk_label"])

        print(
            f"{symbol:<8}"
            f"{shares:>7.2f}"
            f"{money(price):>11}"
            f"{change_color}{pct(change):>9}{Style.RESET_ALL}"
            f"{pl_color}{money(daily_pl):>11}{Style.RESET_ALL}"
            f"{money(value):>13}"
            f"{allocation:>7.1f}%"
            f"  {risk_badge(risk_label):<7}"
            f"  {signal_badge(signal):<6}"
        )

        insight = (
            f"{analysis['trend']} | score {analysis['score']} | "
            f"5D {pct(float(analysis['momentum_5d']))} | "
            f"20D {pct(float(analysis['momentum_20d']))} | "
            f"vol {pct(float(risk['volatility']))}"
        )
        levels = (
            f"stop {money(float(risk['stop_loss']))} | "
            f"target {money(float(risk['take_profit']))} | "
            f"sup {money(float(risk['support']))} | "
            f"res {money(float(risk['resistance']))}"
        )
        print(
            Fore.WHITE
            + f"  {trim_text(insight, 58):<58} {trim_text(levels, 58)}"
        )


def show_top_movers(all_data: pd.DataFrame, watchlist: List[str]) -> None:
    """Print the strongest daily gainers and losers from the watchlist."""
    print_title("Top Movers Scanner")

    movers: List[Dict[str, object]] = []
    for symbol in watchlist:
        history = get_symbol_history(all_data, symbol)
        price = latest_price(history)
        change = daily_change_percent(history)
        if price > 0:
            analysis = analyze_stock(history)
            risk = calculate_risk_metrics(history)
            movers.append(
                {
                    "symbol": symbol,
                    "price": price,
                    "change": change,
                    "trend": analysis["trend"],
                    "signal": analysis["signal"],
                    "volatility": risk["volatility"],
                }
            )

    if not movers:
        print(Fore.YELLOW + "No mover data available yet.")
        return

    movers.sort(key=lambda item: abs(float(item["change"])), reverse=True)
    print(
        Style.BRIGHT
        + f"{'Rank':<6}{'Ticker':<8}{'Price':>12}{'Day %':>10}"
        + f"{'Trend':>12}{'Vol':>9}{'Signal':>9}{'Move Bar':>16}"
    )
    print(Fore.WHITE + "-" * terminal_width())

    for rank, item in enumerate(movers[:TOP_MOVERS_TO_SHOW], start=1):
        symbol = str(item["symbol"])
        price = float(item["price"])
        change = float(item["change"])
        change_color = color_for_change(change)
        bar = "#" * max(1, min(14, int(abs(change) * 2)))
        print(
            f"{rank:<6}{symbol:<8}{money(price):>12}"
            f"{change_color}{pct(change):>10}{Style.RESET_ALL}"
            f"{str(item['trend']):>12}"
            f"{pct(float(item['volatility'])):>9}"
            f"{signal_badge(str(item['signal'])):>9}  {bar}"
        )


def show_three_x_etfs(all_data: pd.DataFrame) -> None:
    """Show a dedicated scanner for leveraged ETF contest ideas."""
    print_title("3x ETF Watchlist")
    ideas: List[Dict[str, object]] = []

    for symbol in THREE_X_ETFS:
        history = get_symbol_history(all_data, symbol)
        if history.empty:
            continue

        price = latest_price(history)
        change = daily_change_percent(history)
        analysis = analyze_stock(history)
        risk = calculate_risk_metrics(history)
        price = latest_price(history)
        shares_allowed = max_new_shares_allowed(price, max_position_value(HTMW_STARTING_CASH))

        ideas.append(
            {
                "symbol": symbol,
                "price": price,
                "change": change,
                "signal": analysis["signal"],
                "score": analysis["score"],
                "trend": analysis["trend"],
                "volatility": risk["volatility"],
                "type": leveraged_etf_type(symbol),
                "shares_allowed": shares_allowed,
                "setup": setup_label(
                    str(analysis["signal"]),
                    str(analysis["trend"]),
                    float(risk["volatility"]),
                    change,
                ),
            }
        )

    if not ideas:
        print(Fore.YELLOW + "No 3x ETF data available right now.")
        return

    ideas.sort(key=lambda item: abs(float(item["change"])), reverse=True)
    print(
        Style.BRIGHT
        + f"{'Rank':<6}{'ETF':<8}{'Price':>12}{'Day %':>10}"
        + f"{'Type':>8}{'Score':>8}{'Trend':>12}{'Vol':>9}"
        + f"{'Max Sh':>9}{'Signal':>9}{'Setup':>18}"
    )
    print(Fore.WHITE + "-" * terminal_width())

    for rank, item in enumerate(ideas[:TOP_CONTEST_IDEAS_TO_SHOW], start=1):
        change = float(item["change"])
        signal = str(item["signal"])
        print(
            f"{rank:<6}{str(item['symbol']):<8}"
            f"{money(float(item['price'])):>12}"
            f"{color_for_change(change)}{pct(change):>10}{Style.RESET_ALL}"
            f"{str(item['type']):>8}"
            f"{float(item['score']):>8.1f}"
            f"{str(item['trend']):>12}"
            f"{pct(float(item['volatility'])):>9}"
            f"{int(item['shares_allowed']):>9}"
            f"{signal_badge(signal):>9}"
            f"{str(item['setup']):>18}"
        )

    print(
        Fore.WHITE
        + "Note: leveraged ETFs are built for short-term moves and can lose value "
        + "fast. Check your contest rules before trading them."
    )


def show_fifteen_minute_lookback(
    intraday_data: pd.DataFrame,
    daily_data: pd.DataFrame,
    symbols: List[str],
) -> None:
    """
    Show what would have worked if you bought about 15 minutes ago.

    This is a hindsight scanner. It does not predict the future, but it can help
    reveal which tickers currently have short-term momentum.
    """
    print_title("15-Min Lookback: What Would Have Worked")
    lookback_rows: List[Dict[str, object]] = []

    for symbol in symbols:
        intraday_history = get_symbol_history(intraday_data, symbol)
        if intraday_history.empty or len(intraday_history) < 2:
            continue

        previous_price = float(intraday_history["Close"].iloc[-2])
        current_price = float(intraday_history["Close"].iloc[-1])
        if previous_price <= 0 or current_price <= 0:
            continue

        move_percent = ((current_price - previous_price) / previous_price) * 100
        move_dollars = current_price - previous_price
        daily_history = get_symbol_history(daily_data, symbol)
        analysis = analyze_stock(daily_history)
        risk = calculate_risk_metrics(daily_history)

        lookback_rows.append(
            {
                "symbol": symbol,
                "then": previous_price,
                "now": current_price,
                "move_percent": move_percent,
                "move_dollars": move_dollars,
                "signal": analysis["signal"],
                "trend": analysis["trend"],
                "score": analysis["score"],
                "setup": setup_label(
                    str(analysis["signal"]),
                    str(analysis["trend"]),
                    float(risk["volatility"]),
                    move_percent,
                ),
            }
        )

    if not lookback_rows:
        print(Fore.YELLOW + "No 15-minute intraday data available right now.")
        return

    lookback_rows.sort(key=lambda item: float(item["move_percent"]), reverse=True)
    print(
        Style.BRIGHT
        + f"{'Rank':<6}{'Ticker':<8}{'15m Ago':>12}{'Now':>12}"
        + f"{'Move $':>11}{'Move %':>10}{'Score':>8}{'Trend':>12}"
        + f"{'Signal':>9}{'Setup':>18}"
    )
    print(Fore.WHITE + "-" * terminal_width())

    for rank, item in enumerate(lookback_rows[:TOP_15_MIN_LOOKBACK_TO_SHOW], start=1):
        move_percent = float(item["move_percent"])
        move_dollars = float(item["move_dollars"])
        print(
            f"{rank:<6}{str(item['symbol']):<8}"
            f"{money(float(item['then'])):>12}"
            f"{money(float(item['now'])):>12}"
            f"{money(move_dollars):>11}"
            f"{color_for_change(move_percent)}{pct(move_percent):>10}{Style.RESET_ALL}"
            f"{float(item['score']):>8.1f}"
            f"{str(item['trend']):>12}"
            f"{signal_badge(str(item['signal'])):>9}"
            f"{str(item['setup']):>18}"
        )

    print(
        Fore.WHITE
        + "Use this as a momentum clue only. It shows recent winners, not a guaranteed next trade."
    )


def show_alerts(rows: List[Dict[str, object]]) -> None:
    """Print helpful alerts based on movement, volatility, and allocation."""
    print_title("Contest Alerts")
    alerts: List[Tuple[str, str, str]] = []

    for row in rows:
        symbol = str(row["symbol"])
        change = float(row["change"])
        allocation = float(row["allocation"])
        analysis = row["analysis"]
        risk = row["risk"]
        volatility = float(risk["volatility"])

        if abs(change) >= BIG_MOVE_ALERT_PERCENT:
            alerts.append(
                (
                    color_for_change(change),
                    symbol,
                    f"large daily move: {pct(change)}",
                )
            )
        if volatility >= HIGH_VOLATILITY_ALERT_PERCENT:
            alerts.append(
                (
                    Fore.YELLOW,
                    symbol,
                    f"high 30-day volatility: {pct(volatility)}",
                )
            )
        if allocation >= CONCENTRATION_WARNING_PERCENT:
            alerts.append(
                (
                    Fore.YELLOW,
                    symbol,
                    f"large portfolio concentration: {allocation:.1f}%",
                )
            )
        if analysis["signal"] == "SELL":
            alerts.append((Fore.RED, symbol, "technical model says SELL"))

    if not alerts:
        print(Fore.WHITE + "OK  No major alerts right now.")
        return

    for color, symbol, message in alerts:
        print(Fore.WHITE + f"!   {symbol:<6} {message}")


def show_htmw_rules() -> None:
    """Show the HowTheMarketWorks rule settings the helper is using."""
    print_title("HowTheMarketWorks Rule Check")
    days_left = trading_days_until_contest_end()
    day_trading = "Yes" if HTMW_DAY_TRADING_ALLOWED else "No"
    shorting = "Yes" if HTMW_SHORT_SELLING_ALLOWED else "No"
    margin = "Yes" if HTMW_MARGIN_ALLOWED else "No"

    cards = [
        metric_card("Min Price", money(HTMW_MIN_BUY_PRICE), Fore.WHITE),
        metric_card("Commission", money(HTMW_COMMISSION_PER_TRADE), Fore.WHITE),
        metric_card("Position Limit", f"{HTMW_POSITION_LIMIT_PERCENT:.0f}%", Fore.WHITE),
        metric_card("Max Holding", money(max_position_value(HTMW_STARTING_CASH)), Fore.WHITE),
    ]
    print(" ".join(cards))
    print(
        Fore.WHITE
        + f"Contest size setting: {money(HTMW_STARTING_CASH)} | "
        + f"Day trading: {day_trading} | Short selling: {shorting} | "
        + f"Margin: {margin} | Trading days left: "
        + (str(days_left) if days_left is not None else "not set")
    )


def show_position_limit_room(rows: List[Dict[str, object]]) -> None:
    """Show how much more can be bought before hitting the position limit."""
    print_title("Position Limit Room")
    limit_value = max_position_value(HTMW_STARTING_CASH)
    print(
        Style.BRIGHT
        + f"{'Ticker':<8}{'Current':>13}{'Limit':>13}{'Room':>13}"
        + f"{'More Shares':>14}{'Status':>12}"
    )
    print(Fore.WHITE + "-" * terminal_width())

    for row in sorted(rows, key=lambda item: float(item["allocation"]), reverse=True):
        symbol = str(row["symbol"])
        current_value = float(row["value"])
        price = float(row["price"])
        room = limit_value - current_value
        more_shares = max_new_shares_allowed(price, room)
        status = "OK" if room >= 0 else "OVER"
        status_color = Fore.WHITE
        print(
            f"{symbol:<8}{money(current_value):>13}{money(limit_value):>13}"
            f"{money(room):>13}{more_shares:>14}"
            f"{status_color}{status:>12}{Style.RESET_ALL}"
        )


def show_htmw_trade_plan(all_data: pd.DataFrame) -> None:
    """Show practical trade ideas sized for HowTheMarketWorks contest rules."""
    print_title("HTMW Trade Plan")
    trade_rows: List[Dict[str, object]] = []
    max_holding = max_position_value(HTMW_STARTING_CASH)

    for symbol in WATCHLIST:
        history = get_symbol_history(all_data, symbol)
        candidate = score_contest_candidate(symbol, history)
        if not candidate or str(candidate["signal"]) != "BUY":
            continue

        risk = calculate_risk_metrics(history)
        price = float(candidate["price"])
        shares = max_new_shares_allowed(price, max_holding)
        estimated_cost = shares * price + HTMW_COMMISSION_PER_TRADE
        if shares <= 0:
            continue

        trade_rows.append(
            {
                **candidate,
                "shares": shares,
                "estimated_cost": estimated_cost,
                "stop_loss": risk["stop_loss"],
                "take_profit": risk["take_profit"],
                "risk_label": risk["risk_label"],
            }
        )

    trade_rows.sort(key=lambda item: float(item["score"]), reverse=True)

    if not trade_rows:
        print(Fore.YELLOW + "No BUY-rated trade plan candidates passed the filters.")
        return

    print(
        Style.BRIGHT
        + f"{'Rank':<6}{'Ticker':<8}{'Price':>12}{'Shares':>9}"
        + f"{'Est Cost':>13}{'Stop':>12}{'Target':>12}{'Risk':>9}"
        + f"{'Score':>8}{'Setup':>18}"
    )
    print(Fore.WHITE + "-" * terminal_width())

    for rank, item in enumerate(trade_rows[:TOP_CONTEST_IDEAS_TO_SHOW], start=1):
        print(
            f"{rank:<6}{str(item['symbol']):<8}"
            f"{money(float(item['price'])):>12}"
            f"{int(item['shares']):>9}"
            f"{money(float(item['estimated_cost'])):>13}"
            f"{money(float(item['stop_loss'])):>12}"
            f"{money(float(item['take_profit'])):>12}"
            f"{str(item['risk_label']):>9}"
            f"{float(item['score']):>8.1f}"
            f"{str(item['setup']):>18}"
        )

    print(
        Fore.WHITE
        + "Trade plan uses your HTMW contest-size setting, commission, minimum price, "
        + "and position limit. Verify contest rules before placing orders."
    )


def score_contest_candidate(symbol: str, history: pd.DataFrame) -> Dict[str, object] | None:
    """
    Score one watchlist symbol for a fair HTMW-style contest idea list.

    This is not a promise that a stock will go up. It simply ranks symbols that
    have stronger trend/momentum, acceptable volatility, and enough room under
    the position limit to be tradable.
    """
    price = latest_price(history)
    if price <= 0 or price < HTMW_MIN_BUY_PRICE:
        return None

    analysis = analyze_stock(history)
    risk = calculate_risk_metrics(history)
    change = daily_change_percent(history)
    limit_room = max_position_value(HTMW_STARTING_CASH)
    shares_allowed = max_new_shares_allowed(price, limit_room)

    if shares_allowed <= 0:
        return None

    score = float(analysis["score"])
    score += min(2.0, max(-2.0, float(analysis["momentum_5d"]) / 3))
    score += min(2.0, max(-2.0, float(analysis["momentum_20d"]) / 8))
    score -= max(0.0, float(risk["volatility"]) - 4) * 0.5

    if abs(change) >= BIG_MOVE_ALERT_PERCENT:
        score += 0.5 if change > 0 else -0.5
    if analysis["signal"] == "SELL":
        score -= 2

    return {
        "symbol": symbol,
        "price": price,
        "change": change,
        "score": score,
        "signal": analysis["signal"],
        "trend": analysis["trend"],
        "volatility": risk["volatility"],
                "shares_allowed": shares_allowed,
                "setup": setup_label(
                    str(analysis["signal"]),
                    str(analysis["trend"]),
                    float(risk["volatility"]),
                    change,
                ),
            }


def show_contest_win_candidates(all_data: pd.DataFrame) -> None:
    """Rank stocks that may be useful in a HowTheMarketWorks contest."""
    print_title("Stocks That May Help In The Contest")
    candidates: List[Dict[str, object]] = []

    for symbol in WATCHLIST:
        candidate = score_contest_candidate(symbol, get_symbol_history(all_data, symbol))
        if candidate:
            candidates.append(candidate)

    candidates = [
        candidate
        for candidate in candidates
        if float(candidate["score"]) >= MIN_CONTEST_CANDIDATE_SCORE
    ]

    if not candidates:
        print(Fore.YELLOW + "No candidates passed the current contest filters.")
        return

    candidates.sort(key=lambda item: float(item["score"]), reverse=True)
    print(
        Style.BRIGHT
        + f"{'Rank':<6}{'Ticker':<8}{'Price':>12}{'Day %':>10}"
        + f"{'Score':>9}{'Trend':>12}{'Vol':>9}{'Max Sh':>9}"
        + f"{'Signal':>9}{'Setup':>18}"
    )
    print(Fore.WHITE + "-" * terminal_width())

    for rank, item in enumerate(candidates[:TOP_CONTEST_IDEAS_TO_SHOW], start=1):
        signal = str(item["signal"])
        change = float(item["change"])
        print(
            f"{rank:<6}{str(item['symbol']):<8}"
            f"{money(float(item['price'])):>12}"
            f"{color_for_change(change)}{pct(change):>10}{Style.RESET_ALL}"
            f"{float(item['score']):>9.1f}"
            f"{str(item['trend']):>12}"
            f"{pct(float(item['volatility'])):>9}"
            f"{int(item['shares_allowed']):>9}"
            f"{signal_badge(signal):>9}"
            f"{str(item['setup']):>18}"
        )

    if not HTMW_DAY_TRADING_ALLOWED:
        print(
            Fore.WHITE
            + "Tip: day trading is marked off, so avoid buying names you may need "
            + "to sell before the next market day."
        )
    print(
        Fore.WHITE
        + "These are fair-play candidates based on momentum, trend, volatility, "
        + "minimum price, commissions, and position-limit fit."
    )


def show_allocation(rows: List[Dict[str, object]]) -> None:
    """Print a simple text allocation view."""
    print_title("Portfolio Allocation")

    if not rows:
        print(Fore.YELLOW + "No portfolio positions to show.")
        return

    for row in sorted(rows, key=lambda item: float(item["allocation"]), reverse=True):
        symbol = str(row["symbol"])
        allocation = float(row["allocation"])
        bar = progress_bar(allocation)
        print(f"{symbol:<8}{allocation:>6.1f}%  {Fore.WHITE}{bar}")


def export_refresh_to_csv(rows: List[Dict[str, object]], tracked_value: float) -> None:
    """Save the latest refresh to a CSV file for later review."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    export_rows: List[Dict[str, object]] = []

    for row in rows:
        analysis = row["analysis"]
        risk = row["risk"]
        export_rows.append(
            {
                "timestamp": timestamp,
                "symbol": row["symbol"],
                "shares": row["shares"],
                "price": round(float(row["price"]), 2),
                "day_change_percent": round(float(row["change"]), 2),
                "day_profit_loss": round(float(row["daily_pl"]), 2),
                "position_value": round(float(row["value"]), 2),
                "allocation_percent": round(float(row["allocation"]), 2),
                "signal": analysis["signal"],
                "score": analysis["score"],
                "trend": analysis["trend"],
                "risk_label": risk["risk_label"],
                "volatility_percent": round(float(risk["volatility"]), 2),
                "stop_loss_idea": round(float(risk["stop_loss"]), 2),
                "take_profit_idea": round(float(risk["take_profit"]), 2),
                "tracked_portfolio_value": round(tracked_value, 2),
            }
        )

    if not export_rows:
        return

    new_data = pd.DataFrame(export_rows)
    file_exists = EXPORT_CSV_FILE.exists()
    new_data.to_csv(
        EXPORT_CSV_FILE,
        mode="a",
        header=not file_exists,
        index=False,
    )


def show_news(portfolio: Dict[str, float]) -> None:
    """Print recent news headlines for each portfolio stock."""
    print_title("Latest Stock News Headlines")

    for symbol in portfolio:
        try:
            news_items = yf.Ticker(symbol).news or []
        except Exception as exc:
            print(Fore.RED + f"{symbol}: could not load news ({exc})")
            continue

        print(Fore.WHITE + Style.BRIGHT + f"\n{symbol}")

        if not news_items:
            print(Fore.YELLOW + "  No headlines available from yfinance right now.")
            continue

        for item in news_items[:NEWS_HEADLINES_PER_STOCK]:
            # yfinance has used more than one news shape over time, so these
            # fallbacks keep the headlines readable across versions.
            content = item.get("content", {}) if isinstance(item, dict) else {}
            headline = item.get("title") or content.get("title") or "Untitled headline"
            publisher = (
                item.get("publisher")
                or content.get("provider", {}).get("displayName")
                or "Unknown source"
            )
            link = (
                item.get("link")
                or content.get("canonicalUrl", {}).get("url")
                or content.get("clickThroughUrl", {}).get("url")
                or ""
            )
            print(Fore.WHITE + f"  - {trim_text(headline, 92)}")
            print(Fore.WHITE + f"    Source: {publisher}")
            if link:
                print(Fore.WHITE + f"    {trim_text(link, 100)}")


def news_item_fields(item: Dict[str, object]) -> Tuple[str, str, str]:
    """Read headline, publisher, and link from old or new yfinance news shapes."""
    content = item.get("content", {}) if isinstance(item, dict) else {}
    headline = item.get("title") or content.get("title") or "Untitled headline"
    publisher = (
        item.get("publisher")
        or content.get("provider", {}).get("displayName")
        or "Unknown source"
    )
    link = (
        item.get("link")
        or content.get("canonicalUrl", {}).get("url")
        or content.get("clickThroughUrl", {}).get("url")
        or ""
    )
    return str(headline), str(publisher), str(link)


def score_headline(headline: str) -> int:
    """Score a headline for simple bullish/bearish catalyst language."""
    text = headline.lower()
    score = 0
    for keyword, value in NEWS_BREAKOUT_KEYWORDS.items():
        if keyword in text:
            score += value
    for keyword, value in NEWS_RISK_KEYWORDS.items():
        if keyword in text:
            score += value
    return score


def build_news_breakout_rows(all_data: pd.DataFrame) -> List[Dict[str, object]]:
    """Create ranked news breakout candidates from recent yfinance headlines."""
    rows: List[Dict[str, object]] = []
    symbols = list(dict.fromkeys(FAST_INTRADAY_SYMBOLS + WATCHLIST))[:NEWS_BREAKOUT_SYMBOL_LIMIT]

    for symbol in symbols:
        history = get_symbol_history(all_data, symbol)
        price = latest_price(history)
        if price <= 0:
            continue

        try:
            news_items = yf.Ticker(symbol).news or []
        except Exception:
            continue

        best_headline = ""
        best_publisher = ""
        best_link = ""
        catalyst_score = 0

        for item in news_items[:NEWS_HEADLINES_PER_STOCK + 2]:
            headline, publisher, link = news_item_fields(item)
            score = score_headline(headline)
            if abs(score) > abs(catalyst_score):
                catalyst_score = score
                best_headline = headline
                best_publisher = publisher
                best_link = link

        if catalyst_score == 0:
            continue

        analysis = analyze_stock(history)
        risk = calculate_risk_metrics(history)
        change = daily_change_percent(history)
        total_score = catalyst_score + float(analysis["score"])
        if change > BIG_MOVE_ALERT_PERCENT:
            total_score += 1
        elif change < -BIG_MOVE_ALERT_PERCENT:
            total_score -= 1

        rows.append(
            {
                "symbol": symbol,
                "price": price,
                "change": change,
                "catalyst_score": catalyst_score,
                "total_score": total_score,
                "signal": analysis["signal"],
                "trend": analysis["trend"],
                "volatility": risk["volatility"],
                "headline": best_headline,
                "publisher": best_publisher,
                "link": best_link,
            }
        )

    rows.sort(key=lambda item: float(item["total_score"]), reverse=True)
    return rows[:TOP_CONTEST_IDEAS_TO_SHOW]


def show_news_breakout_picks(all_data: pd.DataFrame) -> None:
    """Show stocks that may have news-driven breakout catalysts."""
    print_title("News Breakout Picks")

    if not SHOW_NEWS_BREAKOUTS:
        print(Fore.WHITE + "News breakout scanning is off. Set SHOW_NEWS_BREAKOUTS = True to enable it.")
        return

    rows = build_news_breakout_rows(all_data)
    if not rows:
        print(Fore.YELLOW + "No strong news breakout headlines found in the current scan.")
        return

    print(
        Style.BRIGHT
        + f"{'Rank':<6}{'Ticker':<8}{'Price':>12}{'Day %':>10}"
        + f"{'News':>7}{'Total':>8}{'Trend':>12}{'Signal':>9}{'Headline':>22}"
    )
    print(Fore.WHITE + "-" * terminal_width())

    for rank, item in enumerate(rows, start=1):
        signal = str(item["signal"])
        print(
            f"{rank:<6}{str(item['symbol']):<8}"
            f"{money(float(item['price'])):>12}"
            f"{pct(float(item['change'])):>10}"
            f"{int(item['catalyst_score']):>7}"
            f"{float(item['total_score']):>8.1f}"
            f"{str(item['trend']):>12}"
            f"{signal_badge(signal):>9}"
            f"  {trim_text(str(item['headline']), 48)}"
        )

    print(
        Fore.WHITE
        + "News score is keyword-based, so confirm the headline before trading. "
        + "This is a catalyst scanner, not financial advice."
    )


def show_header() -> None:
    """Print the dashboard header."""
    now = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
    width = terminal_width()
    title = "ULTIMATE MARKET HELPER"
    subtitle = f"Updated {now} | Refresh {REFRESH_SECONDS}s | CSV {EXPORT_CSV_FILE}"

    print(dashboard_rule(Fore.WHITE))
    print(Fore.WHITE + Style.BRIGHT + title.center(width))
    print(Fore.WHITE + subtitle.center(width))
    print(Fore.WHITE + "Educational tool only - not financial advice.".center(width))
    print(dashboard_rule(Fore.WHITE))


def portfolio_source_label() -> str:
    """Describe where the current portfolio data came from."""
    if LOAD_HTMW_PORTFOLIO_CSV and HTMW_PORTFOLIO_CSV.exists():
        return f"HTMW CSV: {HTMW_PORTFOLIO_CSV}"
    return "Manual PORTFOLIO setting in script"


def debug_step(message: str) -> None:
    """Print progress messages only when --debug is used."""
    if "--debug" in sys.argv:
        print(Fore.LIGHTBLACK_EX + f"[debug] {message}")


def run_one_refresh() -> None:
    """Run one complete dashboard refresh."""
    portfolio = active_portfolio()
    symbols = sorted(set(portfolio.keys()) | set(WATCHLIST) | set(THREE_X_ETFS))
    intraday_symbols = symbols
    if FAST_REFRESH_MODE:
        intraday_symbols = sorted(set(portfolio.keys()) | set(FAST_INTRADAY_SYMBOLS))
    debug_step("clearing screen and showing header")
    clear_screen()
    show_header()

    debug_step("downloading market data")
    market_data = safe_download(
        symbols=symbols,
        period=HISTORY_PERIOD,
        interval=HISTORY_INTERVAL,
    )
    debug_step("downloading 15-minute intraday data")
    intraday_data = safe_download(
        symbols=intraday_symbols,
        period=INTRADAY_PERIOD,
        interval=INTRADAY_INTERVAL,
    )

    debug_step("building portfolio rows")
    portfolio_rows, tracked_value, daily_pl_total = build_portfolio_rows(
        market_data,
        portfolio,
    )

    debug_step("showing contest summary and HTMW rules")
    show_contest_summary()
    show_htmw_rules()
    debug_step("showing HTMW trade plan")
    show_htmw_trade_plan(market_data)
    debug_step("showing alerts")
    show_alerts(portfolio_rows)
    debug_step("showing contest win candidates and movers")
    show_contest_win_candidates(market_data)
    show_fifteen_minute_lookback(intraday_data, market_data, intraday_symbols)
    show_three_x_etfs(market_data)
    show_top_movers(market_data, WATCHLIST)
    debug_step("showing news breakout picks")
    show_news_breakout_picks(market_data)
    debug_step("exporting CSV")
    export_refresh_to_csv(portfolio_rows, tracked_value)


def run_dashboard() -> None:
    """Run the live dashboard forever until the user presses Ctrl+C."""
    while True:
        try:
            run_one_refresh()
        except Exception as exc:
            log_error(exc)
            print(Fore.WHITE + Style.BRIGHT + "\nSomething went wrong during refresh.")
            print(Fore.WHITE + f"Details were saved to: {ERROR_LOG_FILE}")
            print(Fore.WHITE + "The dashboard will try again on the next refresh.")

        print(
            Fore.CYAN
            + f"\nNext refresh in {REFRESH_SECONDS} seconds. "
            + "Press Ctrl+C to quit."
        )
        time.sleep(REFRESH_SECONDS)


if __name__ == "__main__":
    try:
        if "--once" in sys.argv:
            run_one_refresh()
            print(Fore.CYAN + "\nOne-time dashboard run complete.")
        else:
            run_dashboard()
    except KeyboardInterrupt:
        print(Fore.CYAN + "\nDashboard stopped. Good luck with the contest!")
    except Exception as exc:
        log_error(exc)
        print(Fore.RED + Style.BRIGHT + "\nThe dashboard hit an unexpected error.")
        print(Fore.WHITE + f"Details were saved to: {ERROR_LOG_FILE}")
        input("Press Enter to close...")
