"""
Phone-friendly Ultimate Market Helper.

Run on your computer:
    streamlit run phone_market_helper.py --server.address 0.0.0.0 --server.port 8501

Then open the shown URL on your phone. Your phone and computer usually need to
be on the same Wi-Fi network.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, Iterable, List

import pandas as pd
import streamlit as st

import ultimate_market_helper as helper


st.set_page_config(
    page_title="Market Helper Mobile",
    page_icon="MH",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1rem;
        padding-left: 0.8rem;
        padding-right: 0.8rem;
        max-width: 760px;
    }
    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #dddddd;
        border-radius: 10px;
        padding: 10px;
    }
    .pick-card {
        background: #ffffff;
        border: 1px solid #dddddd;
        border-radius: 10px;
        padding: 12px 14px;
        margin: 10px 0;
    }
    .pick-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #111111;
        margin-bottom: 4px;
    }
    .pick-line {
        color: #333333;
        font-size: 0.95rem;
        line-height: 1.45;
    }
    .small-note {
        color: #666666;
        font-size: 0.86rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def money(value: float) -> str:
    return f"${value:,.2f}"


def pct(value: float) -> str:
    return f"{value:+.2f}%"


@st.cache_data(ttl=30, show_spinner=False)
def load_data(symbols: tuple[str, ...], period: str, interval: str) -> pd.DataFrame:
    return helper.safe_download(symbols, period, interval)


def render_card(title: str, lines: Iterable[str]) -> None:
    body = "".join(f"<div class='pick-line'>{line}</div>" for line in lines)
    st.markdown(
        f"""
        <div class="pick-card">
            <div class="pick-title">{title}</div>
            {body}
        </div>
        """,
        unsafe_allow_html=True,
    )


def build_trade_plan(market_data: pd.DataFrame, limit: int = 10) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    max_holding = helper.max_position_value(helper.HTMW_STARTING_CASH)

    for symbol in helper.WATCHLIST:
        history = helper.get_symbol_history(market_data, symbol)
        candidate = helper.score_contest_candidate(symbol, history)
        if not candidate or str(candidate["signal"]) != "BUY":
            continue

        risk = helper.calculate_risk_metrics(history)
        price = float(candidate["price"])
        shares = helper.max_new_shares_allowed(price, max_holding)
        if shares <= 0:
            continue

        rows.append(
            {
                **candidate,
                "shares": shares,
                "estimated_cost": shares * price + helper.HTMW_COMMISSION_PER_TRADE,
                "stop": risk["stop_loss"],
                "target": risk["take_profit"],
                "risk": risk["risk_label"],
            }
        )

    rows.sort(key=lambda item: float(item["score"]), reverse=True)
    return rows[:limit]


def build_lookback(
    intraday_data: pd.DataFrame,
    daily_data: pd.DataFrame,
    symbols: List[str],
    limit: int = 10,
) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []

    for symbol in symbols:
        intraday_history = helper.get_symbol_history(intraday_data, symbol)
        if intraday_history.empty or len(intraday_history) < 2:
            continue

        previous = float(intraday_history["Close"].iloc[-2])
        current = float(intraday_history["Close"].iloc[-1])
        if previous <= 0 or current <= 0:
            continue

        move_percent = ((current - previous) / previous) * 100
        daily_history = helper.get_symbol_history(daily_data, symbol)
        analysis = helper.analyze_stock(daily_history)
        risk = helper.calculate_risk_metrics(daily_history)

        rows.append(
            {
                "symbol": symbol,
                "previous": previous,
                "current": current,
                "move_percent": move_percent,
                "move_dollars": current - previous,
                "signal": analysis["signal"],
                "trend": analysis["trend"],
                "setup": helper.setup_label(
                    str(analysis["signal"]),
                    str(analysis["trend"]),
                    float(risk["volatility"]),
                    move_percent,
                ),
            }
        )

    rows.sort(key=lambda item: float(item["move_percent"]), reverse=True)
    return rows[:limit]


def build_etfs(market_data: pd.DataFrame, limit: int = 10) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []

    for symbol in helper.THREE_X_ETFS:
        history = helper.get_symbol_history(market_data, symbol)
        price = helper.latest_price(history)
        if price <= 0:
            continue

        analysis = helper.analyze_stock(history)
        risk = helper.calculate_risk_metrics(history)
        change = helper.daily_change_percent(history)
        rows.append(
            {
                "symbol": symbol,
                "price": price,
                "change": change,
                "type": helper.leveraged_etf_type(symbol),
                "score": analysis["score"],
                "trend": analysis["trend"],
                "volatility": risk["volatility"],
                "signal": analysis["signal"],
                "setup": helper.setup_label(
                    str(analysis["signal"]),
                    str(analysis["trend"]),
                    float(risk["volatility"]),
                    change,
                ),
            }
        )

    rows.sort(key=lambda item: abs(float(item["change"])), reverse=True)
    return rows[:limit]


def build_breakouts(market_data: pd.DataFrame, limit: int = 10) -> List[Dict[str, object]]:
    return helper.build_news_breakout_rows(market_data)[:limit]


st.title("Market Helper")
st.caption("Phone-friendly contest scanner. Educational only, not financial advice.")

portfolio = helper.active_portfolio()
daily_symbols = sorted(set(portfolio) | set(helper.WATCHLIST) | set(helper.THREE_X_ETFS))
intraday_symbols = sorted(set(portfolio) | set(helper.FAST_INTRADAY_SYMBOLS))

col1, col2 = st.columns(2)
col1.metric("Contest Size", money(helper.HTMW_STARTING_CASH))
col2.metric("Max Holding", money(helper.max_position_value(helper.HTMW_STARTING_CASH)))

if st.button("Refresh Now", use_container_width=True):
    st.cache_data.clear()

with st.spinner("Loading market data..."):
    market_data = load_data(tuple(daily_symbols), helper.HISTORY_PERIOD, helper.HISTORY_INTERVAL)
    intraday_data = load_data(tuple(intraday_symbols), helper.INTRADAY_PERIOD, helper.INTRADAY_INTERVAL)

st.caption(f"Last loaded: {datetime.now().strftime('%I:%M:%S %p')}")

section = st.radio(
    "Scanner",
    ["Trade Plan", "15-Min Lookback", "3x ETFs", "News Breakouts"],
    horizontal=False,
)

if section == "Trade Plan":
    st.subheader("HTMW Trade Plan")
    for index, item in enumerate(build_trade_plan(market_data), start=1):
        render_card(
            f"{index}. {item['symbol']} - {item['setup']}",
            [
                f"Price: {money(float(item['price']))} | Score: {float(item['score']):.1f} | Risk: {item['risk']}",
                f"Shares: {int(item['shares'])} | Est cost: {money(float(item['estimated_cost']))}",
                f"Stop: {money(float(item['stop']))} | Target: {money(float(item['target']))}",
            ],
        )

elif section == "15-Min Lookback":
    st.subheader("15-Min Lookback")
    for index, item in enumerate(build_lookback(intraday_data, market_data, intraday_symbols), start=1):
        render_card(
            f"{index}. {item['symbol']} - {pct(float(item['move_percent']))}",
            [
                f"15m ago: {money(float(item['previous']))} | Now: {money(float(item['current']))}",
                f"Move: {money(float(item['move_dollars']))} | Trend: {item['trend']} | Signal: {item['signal']}",
                f"Setup: {item['setup']}",
            ],
        )

elif section == "3x ETFs":
    st.subheader("3x ETFs")
    for index, item in enumerate(build_etfs(market_data), start=1):
        render_card(
            f"{index}. {item['symbol']} - {item['type']}",
            [
                f"Price: {money(float(item['price']))} | Day: {pct(float(item['change']))}",
                f"Score: {float(item['score']):.1f} | Trend: {item['trend']} | Signal: {item['signal']}",
                f"Vol: {pct(float(item['volatility']))} | Setup: {item['setup']}",
            ],
        )

else:
    st.subheader("News Breakouts")
    for index, item in enumerate(build_breakouts(market_data), start=1):
        render_card(
            f"{index}. {item['symbol']} - news score {int(item['catalyst_score'])}",
            [
                f"Price: {money(float(item['price']))} | Day: {pct(float(item['change']))} | Signal: {item['signal']}",
                f"Total score: {float(item['total_score']):.1f} | Trend: {item['trend']}",
                f"Headline: {str(item['headline'])[:130]}",
            ],
        )

st.markdown("<div class='small-note'>Tip: add this page to your phone home screen from the browser share menu.</div>", unsafe_allow_html=True)
