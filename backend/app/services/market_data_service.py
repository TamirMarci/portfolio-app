"""
Market data service.

Responsibilities:
  - Fetch live prices from yfinance (one call per symbol via Ticker.fast_info)
  - Handle FX conversion for non-USD assets (e.g. OCO.V quoted in CAD → USD)
  - Write/read from the price_cache table
  - Return last known cached price (with stale=True) on fetch failure
  - Never crash the API due to a market data error

Design notes
------------
We intentionally use yf.Ticker(symbol).fast_info.last_price rather than
yf.download() for the following reasons:

  1. yf.download() returns a MultiIndex DataFrame whose column order
     (field, ticker) vs (ticker, field) has changed between yfinance releases,
     making batch column access fragile.

  2. Exchange-suffix tickers such as OCO.V (TSX Venture) can silently return
     all-NaN columns in a batch download while working correctly when fetched
     individually via Ticker.

  3. fast_info.last_price is a single-field fast path with no DataFrame
     parsing overhead, which is appropriate for the small number of holdings
     in this MVP.

FX ticker convention used by yfinance:
  CAD → USD : "CADUSD=X"  (how many USD per 1 CAD)
"""

import logging
import math
from datetime import datetime, timezone

import yfinance as yf
from sqlalchemy.orm import Session

from app.repositories import price_cache_repo
from app.schemas.price import RefreshResult, SymbolRefreshDetail

logger = logging.getLogger(__name__)

# Map: ISO currency code → yfinance FX ticker that gives (currency → USD) rate
FX_TICKERS: dict[str, str] = {
    "CAD": "CADUSD=X",
    # Add more as needed: "GBP": "GBPUSD=X", "EUR": "EURUSD=X"
}


def _fetch_fx_rates(non_usd_currencies: set[str]) -> dict[str, float]:
    """
    Fetch FX rates for all required currencies via yf.Ticker.fast_info.
    Returns {currency: rate_to_usd}. Falls back to 1.0 on any failure.
    """
    rates: dict[str, float] = {}
    for currency in non_usd_currencies:
        ticker_sym = FX_TICKERS.get(currency)
        if not ticker_sym:
            logger.warning(
                "FX | no ticker configured for currency=%s — using 1.0 (prices will be wrong for this currency)",
                currency,
            )
            rates[currency] = 1.0
            continue
        try:
            rate = yf.Ticker(ticker_sym).fast_info.last_price
            if rate and not math.isnan(rate) and rate > 0:
                rates[currency] = float(rate)
                logger.info("FX | %s → USD via %s = %.6f", currency, ticker_sym, rate)
            else:
                logger.warning(
                    "FX | %s returned invalid rate (%s) — using 1.0",
                    ticker_sym, rate,
                )
                rates[currency] = 1.0
        except Exception as exc:
            logger.error("FX | fetch failed for %s (%s): %s", currency, ticker_sym, exc)
            rates[currency] = 1.0
    return rates


def _fetch_symbol_price(symbol: str) -> float:
    """
    Fetch the latest price for a single symbol via yf.Ticker.fast_info.

    Returns the price as a float on success.
    Raises ValueError with a human-readable message on failure.
    """
    ticker = yf.Ticker(symbol)
    price = ticker.fast_info.last_price

    if price is None:
        raise ValueError("fast_info.last_price returned None — symbol may be delisted or invalid")

    if math.isnan(price):
        raise ValueError("fast_info.last_price returned NaN — no market data available")

    if price <= 0:
        raise ValueError(f"fast_info.last_price returned {price} — unexpected non-positive value")

    return float(price)


def refresh_prices(
    db: Session,
    symbols_with_currency: list[tuple[str, str]],  # [(symbol, currency), ...]
) -> RefreshResult:
    """
    Fetch live prices for all given symbols, convert to USD, and persist to cache.

    Each symbol is fetched individually via yf.Ticker.fast_info.last_price for
    maximum reliability across exchange-suffix tickers (e.g. OCO.V) and ETFs.

    Returns a RefreshResult with structured per-symbol details.
    """
    fetched_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")

    if not symbols_with_currency:
        return RefreshResult(
            total_attempted=0,
            succeeded=0,
            failed=0,
            per_symbol=[],
            fetched_at=fetched_at,
            message="No symbols to refresh.",
        )

    # Step 1: Fetch FX rates for any non-USD assets up front
    non_usd_currencies = {c for _, c in symbols_with_currency if c != "USD"}
    fx_rates = _fetch_fx_rates(non_usd_currencies) if non_usd_currencies else {}

    # Step 2: Fetch each symbol individually
    per_symbol: list[SymbolRefreshDetail] = []

    for symbol, currency in symbols_with_currency:
        fx_rate = fx_rates.get(currency, 1.0) if currency != "USD" else 1.0
        logger.info(
            "PRICE | fetching %s  currency=%s  fx_rate=%.6f",
            symbol, currency, fx_rate,
        )
        try:
            price_native = _fetch_symbol_price(symbol)
            price_usd = price_native * fx_rate

            price_cache_repo.upsert(
                db,
                symbol=symbol,
                price_usd=price_usd,
                price_native=price_native,
                native_currency=currency,
                fetched_at=fetched_at,
            )

            logger.info(
                "PRICE | %s OK  native=%.4f %s  fx=%.6f  usd=%.4f",
                symbol, price_native, currency, fx_rate, price_usd,
            )
            per_symbol.append(SymbolRefreshDetail(
                symbol=symbol,
                status="ok",
                currency=currency,
                price_native=price_native,
                price_usd=price_usd,
                error=None,
            ))

        except Exception as exc:
            reason = str(exc)
            logger.warning("PRICE | %s FAILED  currency=%s  reason: %s", symbol, currency, reason)
            per_symbol.append(SymbolRefreshDetail(
                symbol=symbol,
                status="failed",
                currency=currency,
                price_native=None,
                price_usd=None,
                error=reason,
            ))

    db.commit()

    succeeded = sum(1 for r in per_symbol if r.status == "ok")
    failed = sum(1 for r in per_symbol if r.status == "failed")
    total = len(per_symbol)

    logger.info(
        "PRICE | refresh complete — succeeded: %d  failed: %d  total: %d",
        succeeded, failed, total,
    )

    failed_names = [r.symbol for r in per_symbol if r.status == "failed"]
    return RefreshResult(
        total_attempted=total,
        succeeded=succeeded,
        failed=failed,
        per_symbol=per_symbol,
        fetched_at=fetched_at,
        message=(
            f"Refreshed {succeeded}/{total} symbols."
            + (f" Failed: {', '.join(failed_names)}." if failed_names else "")
        ),
    )


def get_fx_rate(currency: str) -> float:
    """
    Return the current FX rate for the given ISO currency code → USD.
    Returns 1.0 for USD or any currency not in FX_TICKERS.
    """
    if currency == "USD":
        return 1.0
    rates = _fetch_fx_rates({currency})
    return rates.get(currency, 1.0)


def fetch_asset_metadata(symbol: str) -> dict:
    """
    Fetch asset metadata from yfinance for a given symbol.

    Uses Ticker.info to retrieve: longName/shortName, currency, exchange, quoteType.
    Returns a dict with keys: symbol, name, currency, exchange, asset_type.
    Raises ValueError if the symbol cannot be resolved (missing name or currency).

    yfinance returns a near-empty dict (no name, no currency) for invalid/unknown
    symbols — we treat that as an unresolvable symbol.
    """
    try:
        info = yf.Ticker(symbol).info
    except Exception as exc:
        raise ValueError(f"Market data lookup failed for '{symbol}': {exc}") from exc

    name = info.get("longName") or info.get("shortName")
    currency = info.get("currency")
    exchange = info.get("exchange")
    quote_type = (info.get("quoteType") or "").upper()

    if not name or not currency:
        raise ValueError(
            f"Symbol '{symbol}' could not be resolved. "
            "Verify the ticker is correct and listed on a supported exchange."
        )

    asset_type = {"ETF": "ETF", "EQUITY": "STOCK", "MUTUALFUND": "ETF"}.get(quote_type, "STOCK")

    return {
        "symbol": symbol.upper(),
        "name": name,
        "currency": currency.upper(),
        "exchange": exchange,
        "asset_type": asset_type,
    }


def get_or_create_asset(db: Session, symbol: str):
    """
    Return the Asset row for the given symbol.

    Lookup order:
      1. DB lookup by symbol (fast path — no network call).
      2. If not found, resolve via yfinance and insert a new asset row.

    Raises ValueError if the symbol cannot be resolved by the provider.
    Holdings are NOT touched — this only creates/finds the asset record.
    """
    from app.repositories import asset_repo

    asset = asset_repo.get_by_symbol(db, symbol)
    if asset is not None:
        return asset

    logger.info("ASSET | '%s' not in DB — resolving via yfinance", symbol)
    metadata = fetch_asset_metadata(symbol)  # raises ValueError if unresolvable

    logger.info(
        "ASSET | creating '%s'  name='%s'  currency=%s  type=%s",
        metadata["symbol"], metadata["name"], metadata["currency"], metadata["asset_type"],
    )
    return asset_repo.upsert(
        db,
        symbol=metadata["symbol"],
        name=metadata["name"],
        asset_type=metadata["asset_type"],
        exchange=metadata["exchange"],
        currency=metadata["currency"],
    )


def get_cached_prices(db: Session, symbols: list[str]) -> dict[str, dict]:
    """
    Return cached price data for the given symbols.
    Format: {symbol: {price_usd, price_native, native_currency, fetched_at, stale}}
    """
    from app.config import settings
    from datetime import timedelta

    cache = price_cache_repo.get_by_symbols(db, symbols)
    now = datetime.now(timezone.utc)
    ttl = timedelta(minutes=settings.price_cache_ttl_minutes)

    result = {}
    for symbol in symbols:
        entry = cache.get(symbol)
        if entry:
            fetched = datetime.fromisoformat(entry.fetched_at).replace(tzinfo=timezone.utc)
            stale = (now - fetched) > ttl
            result[symbol] = {
                "price_usd": entry.price_usd,
                "price_native": entry.price_native,
                "native_currency": entry.native_currency,
                "fetched_at": entry.fetched_at,
                "stale": stale,
            }
        else:
            result[symbol] = {
                "price_usd": None,
                "price_native": None,
                "native_currency": None,
                "fetched_at": None,
                "stale": True,
            }
    return result
