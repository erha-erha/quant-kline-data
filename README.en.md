# Multi-market K-line dataset

[简体中文](README.md) | **English**

K-line data for China A-shares, China futures, indices, US stocks, global futures, crypto and forex, stored as Parquet + Zstd. One file holds one symbol at one bar size.

<!-- coverage:start -->
| Market | Folder | Symbols | Files | Bars | Bar sizes | Range |
|---|---|---:|---:|---:|---|---|
| China A-shares | [`cn_stock`](data/cn_stock/README.en.md) | 111 | 143 | 522,952 | 1d 4h 1h | 2005-01-04 – 2026-09-24 |
| China futures | [`cn_futures`](data/cn_futures/README.en.md) | 77 | 107 | 259,610 | 1d 4h 1h | 2005-01-04 – 2026-09-24 |
| Indices | [`index`](data/index/README.en.md) | 3 | 3 | 337,304 | 1d 15m | 1997-07-02 – 2026-09-04 |
| US stocks & ETFs | [`us_stock`](data/us_stock/README.en.md) | 72 | 116 | 2,294,263 | 1d 1h 15m | 1980-12-12 – 2026-09-24 |
| Global futures | [`global_futures`](data/global_futures/README.en.md) | 26 | 32 | 1,710,915 | 1d 15m | 2005-01-03 – 2026-09-24 |
| Crypto | [`crypto`](data/crypto/README.en.md) | 16 | 30 | 265,838 | 1d 4h 1h | 2014-09-17 – 2026-09-05 |
| Forex | [`forex`](data/forex/README.en.md) | 8 | 8 | 33,509 | 1d | 2010-01-01 – 2026-09-04 |
| **Total** | | **313** | **439** | **5,424,391** | | |
<!-- coverage:end -->

Open a folder to look up symbols by name.

## Usage

```bash
pip install pandas pyarrow
```

```python
import pandas as pd

df = pd.read_parquet("data/cn_stock/1d/CNS_600519.parquet")

# Read directly, without downloading the repo
url = "https://raw.githubusercontent.com/erha-erha/quant-kline-data/main/data/crypto/1d/BTCUSDT.parquet"
btc = pd.read_parquet(url)
```

## Fields

| Field | Meaning |
|---|---|
| `date` | Trading date (daily) |
| `datetime` | Bar open time, exchange local time (intraday) |
| `timestamp` | Bar open time in Unix seconds (intraday) |
| `open` `high` `low` `close` `volume` | OHLC and volume |
| `close_time` | Bar close time, only in some hourly files |

## Read before use

1. **One underlying may have two datasets. Use adjusted data for returns and unadjusted data for historical quotes.** Adjusted: `CNS_600519`, `US_AAPL`, `CNF_AU`. Unadjusted or not dividend-adjusted: `CN600519`, `AAPL`, `CN_AU`.
2. **`USF_*` daily bars are not futures prices.** They are adjusted prices of a proxy ETF (see the `proxy` column in `files.csv`). Real futures prices are in `*_FUT`.
3. **15-minute bars are CFD quotes.** Prices differ somewhat from futures, and volume is not exchange volume.
4. **Continuous contracts are not tradable contracts.** Early `CNF_*` prices are not historical trade prices; `CN_*` and `*_FUT` gap at rollovers.
5. **For China futures 1h / 4h bars, rely on `close_time`.** One bar can span the lunch break and night session.
6. **Volume units and history length vary by file**, so do not compare across profiles directly. See `files.csv` and `profiles.en.csv` for each file's profile and date range.

## Layout

```
data/<market>/<bar size>/<id>.parquet   K-lines
files.csv                               File list: profile, rows, date range
instruments.en.csv                      Symbols: name, exchange, timezone
profiles.en.csv                         Profiles: adjustment, time, volume unit
markets.csv                             Markets
tools/kline.py                          Ingest and check tool
```

## Adding data

Register a new market in `markets.csv`, a new profile in `profiles.*.csv` and a new symbol in `instruments.*.csv`. Then:

```bash
python tools/kline.py add ID.csv --market cn_stock --level 5m --profile PROFILE
python tools/kline.py check
```

The file name is the symbol ID. New bar sizes (such as `5m`, `1w`) and new columns (such as open interest) can be added directly; the file list and docs update automatically.

**Capacity budget:** at most 50 MB per file and 500 MB for `data/`, leaving the other half of the space for git history; `check` reports usage. Adding a symbol costs only its own file, but rewriting a file keeps the old version in git history permanently, so keep full refreshes rare.

For study and research only. No guarantee of accuracy or completeness. Not investment advice.
