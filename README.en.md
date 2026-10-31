# Multi-Market K-line Dataset

[简体中文](README.md) | **English**

K-line (OHLCV candlestick) data for China A-shares, China futures, indices, US stocks, global futures, crypto and forex: **313 instruments, 439 files and 5,424,391 bars** up to September 2026. Everything is plain CSV, one file per instrument and bar size, readable with Excel, pandas or any language and independent of any software. Use it for quantitative research, backtests, factor and machine-learning experiments.

### Coverage

| Market | Folder | Instruments | Files | Bars | Bar sizes | From – to | Contents |
|---|---|---:|---:|---:|---|---|---|
| China A-shares | `cn_stock` | 111 | 143 | 522,952 | 1d 4h 1h | 2005-01-04 – 2026-09-24 | Shanghai and Shenzhen large caps such as Kweichow Moutai and CATL |
| China futures | `cn_futures` | 77 | 107 | 259,610 | 1d 4h 1h | 2005-01-04 – 2026-09-24 | main continuous contracts of 62 products on the five Chinese futures exchanges, plus 15 Sina continuous contracts |
| Indices | `index` | 3 | 3 | 337,304 | 1d 15m | 1997-07-02 – 2026-09-04 | SSE Composite daily; FTSE China A50 and Hang Seng 15-minute CFDs |
| US stocks & ETFs | `us_stock` | 72 | 116 | 2,294,263 | 1d 1h 15m | 1980-12-12 – 2026-09-24 | S&P 500 large caps plus ETFs such as SPY, QQQ, GLD and TLT |
| Global futures | `global_futures` | 26 | 32 | 1,710,915 | 1d 15m | 2005-01-03 – 2026-09-24 | US index, Treasury, dollar-index, energy, metal and agricultural futures |
| Crypto | `crypto` | 16 | 30 | 265,838 | 1d 4h 1h | 2014-09-17 – 2026-09-05 | 15 Binance USDT pairs such as BTC and ETH, plus Yahoo BTC-USD |
| Forex | `forex` | 8 | 8 | 33,509 | 1d | 2010-01-01 – 2026-09-04 | 8 major currency pairs |
| **Total** | | **313** | **439** | **5,424,391** | | | |

Bar sizes: `1d` daily, `4h` four-hour, `1h` hourly, `15m` fifteen-minute. `files.csv` lists the bar sizes of every instrument and the first and last bar of every file.

**Find an instrument by name:** [China A-shares](data/cn_stock/README.en.md) · [China futures](data/cn_futures/README.en.md) · [Indices](data/index/README.en.md) · [US stocks & ETFs](data/us_stock/README.en.md) · [Global futures](data/global_futures/README.en.md) · [Crypto](data/crypto/README.en.md) · [Forex](data/forex/README.en.md). Each page lists every instrument of that market with links to its CSV files.

### Layout

```
data/<market>/<bar size>/<id>.csv   bars, e.g. data/cn_stock/1d/CNS_600519.csv
instruments.en.csv                  instruments: id, name, exchange, time zone, bar sizes, notes
files.csv                           files: path, id, bar size, data profile, rows, first / last bar, proxy ETF
profiles.en.csv                     data profiles: source, adjustment, time convention, volume unit
```

### File format

Daily, e.g. `data/cn_stock/1d/CN600519.csv`:

```
date,open,high,low,close,volume
2026-09-04,1295.88,1338.86,1295.6,1330,45416
```

Intraday (15m / 1h / 4h), e.g. `data/us_stock/15m/US_AAPL.csv` and `data/cn_stock/1h/CN600519.csv`:

```
datetime,timestamp,open,high,low,close,volume
2026-08-31 15:45,1788205500,316.426,317.437,315.717,316.726,40.428
```

```
datetime,timestamp,open,high,low,close,volume,close_time
2026-09-04 14:00,1788501600,1329.08,1334,1328.62,1330,860217,2026-09-04 15:00
```

| Column | Meaning |
|---|---|
| `date` | trading date; China futures night sessions belong to the next trading day, forex days start at midnight London time |
| `datetime` | bar start in the exchange's local time (no offset); the time zone is the `timezone` column of `instruments.en.csv` |
| `timestamp` | bar start as a Unix timestamp (seconds), independent of time zones; use it for arithmetic across daylight-saving changes |
| `open` `high` `low` `close` | open, high, low and close prices |
| `volume` | volume; its unit depends on the source, see the table below |
| `close_time` | the bar end given by the source (local time); only in Sina 1h / 4h (A-shares, China futures) and Yahoo 1h (US stocks) files |

Prices and volumes are kept exactly as the sources gave them, without rounding, so some values have long decimal tails (e.g. Yahoo's `1.1621150970458984`).

### Data profiles

The `profile` column of `files.csv` tells which group a file belongs to; `profiles.en.csv` holds the same table:

| profile | Files | Contents | Source | Adjustment | Time | Volume unit |
|---|---|---|---|---|---|---|
| `baostock_daily_hfq` | CNS_* | A-share daily, back-adjusted | BaoStock | Back-adjusted (hfq): the earliest prices keep their quoted values and later prices are scaled up for every dividend and split, so returns are total returns but prices differ from historical quotes | trading date | shares |
| `tencent_daily_raw` | CN###### 1d | A-share daily, unadjusted | Tencent | Unadjusted: prices gap on ex-dividend / ex-rights dates | trading date | lots (1 lot = 100 shares) |
| `sina_intraday_stock` | CN###### 1h / 4h | A-share intraday, unadjusted | Sina Finance | Unadjusted | 1h: four bars per day starting 09:30, 10:30, 13:00 and 14:00; 4h: the provider's 240-minute bar, one per trading day (09:30-15:00). datetime is the provider's end time minus the period; close_time is the provider's end time | shares |
| `cn_futures_main_continuous` | CNF_* | China futures main continuous, ratio back-adjusted | Exchange daily data per contract (SHFE, INE, DCE, CZCE, CFFEX) via AKShare | Main contract = the contract with the largest open interest that never rolls back to an earlier expiry; a roll decided at day t's close takes effect after t and earlier history is scaled by close_new(t) / close_old(t). Returns equal those of a roller; earlier prices are not the prices that traded then | trading date (night sessions belong to the next trading day) | contracts (main contract) |
| `sina_futures_continuous_daily` | CN_* 1d | China futures continuous (Sina XX0), unadjusted | Sina Finance | Sina's continuous contract without roll adjustment (roll gaps remain); roll rule and volume convention follow Sina and are not audited | trading date | contracts |
| `sina_intraday_futures` | CN_* 1h / 4h | China futures intraday (Sina continuous), unadjusted | Sina Finance | Sina continuous contract, no roll adjustment | Bars follow the provider's end times: each covers the 1 or 4 trading hours before its end and may span the lunch break, the night session and the next morning. datetime is the nominal end minus the period; use close_time | contracts |
| `yahoo_daily_adjusted` | US_* 1d | US stock daily, total-return adjusted | Yahoo Finance (auto_adjust) | Adjusted for splits and cash dividends (Yahoo adjusted-close method); returns are total returns | trading date | shares (split-adjusted) |
| `dukascopy_stock_15m` | US_* 15m | US stock 15-minute (Dukascopy stock CFD), adjusted | Dukascopy (BID 1-minute bars aggregated to 15 minutes) | Back-adjusted with Yahoo's split and dividend events (same method as Yahoo's adjusted close); returns are total returns | regular session (09:30-16:00 New York), bar start time | Dukascopy CFD volume, not exchange volume |
| `yahoo_daily` | AAPL … XOM, SPY, QQQ, GLD, TLT, SSE, BTC-USD 1d | Yahoo daily | Yahoo Finance | Yahoo's regular prices: split-adjusted, not dividend-adjusted | trading date | shares; US dollars for BTC-USD; SSE volume is 0 in early years and inconsistent, avoid it |
| `yahoo_1h` | AAPL … XOM, SPY, QQQ, GLD, TLT 1h | US stock hourly, regular session | Yahoo Finance | Yahoo's regular prices: split-adjusted, not dividend-adjusted | 09:30-16:00 New York time; the last bar of a day is the half hour 15:30-16:00, shorter on early-close days. close_time is the bar end | shares |
| `etf_proxy_daily` | USF_* 1d | ETF proxy of a US future, daily, adjusted | Yahoo Finance (auto_adjust) | Prices are the adjusted prices of the ETF named in the proxy column of files.csv, not futures prices; no roll gaps, short-borrow costs not included | trading date | ETF shares |
| `dukascopy_cfd_15m` | USF_* 15m, IDX_A50, IDX_HSI | Futures / index 15-minute (Dukascopy CFD) | Dukascopy (BID 1-minute bars aggregated to 15 minutes) | CFD quotes, unadjusted; an intraday proxy of the future or index, whose price level differs from the futures price | nearly 24-hour trading, bar start time | Dukascopy CFD volume, not exchange volume |
| `yahoo_futures_daily` | *_FUT | Global futures front-month continuous daily | Yahoo Finance (=F tickers) | Yahoo's front-month continuous contract without roll adjustment; roll gaps remain and returns are not holding returns | trading date | contracts |
| `binance_spot` | *USDT | Crypto spot (Binance) | Binance public market data | No adjustment | UTC, bar start time | base asset units (BTC for BTCUSDT) |
| `yahoo_fx_daily` | EURUSD … | Forex daily | Yahoo Finance (=X tickers) | Quotes, no adjustment | trading date (days start at midnight London time) | not available (mostly 0) |

### Read before use

1. **Some instruments come twice, with different conventions.** `CNS_600519` is BaoStock back-adjusted daily (volume in shares), `CN600519` is Tencent unadjusted daily (volume in lots of 100 shares, plus Sina hourly bars); `US_AAPL` is Yahoo total-return adjusted daily plus Dukascopy 15-minute bars, `AAPL` is Yahoo daily without dividend adjustment plus hourly bars; `CNF_AU` is a ratio back-adjusted main continuous contract, `CN_AU` is Sina's AU0 continuous contract (unadjusted, daily bars end on 2024-07-17). Use adjusted data for returns and unadjusted data for historical quotes.
2. **Daily `USF_*` bars are not futures prices** but adjusted prices of an ETF (`USF_ES` is SPY, `USF_GC` is GLD, `USF_ZC` is CORN, ...); the ETF is in the `proxy` column of `files.csv`. Actual front-month futures prices of the S&P 500, crude oil, gold, silver, copper and natural gas are in the `*_FUT` files (Yahoo `ES=F` etc.).
3. **15-minute bars are Dukascopy CFD quotes** (BID), not exchange trades; their price level differs from the futures and their volume is CFD volume. US stock CFDs are adjusted with Yahoo's split and dividend events.
4. **Continuous contracts are not tradable contracts.** Returns of the back-adjusted main continuous series (`CNF_*`) equal those of a roller, but early prices are not the prices that traded then; unadjusted continuous series (`CN_*`, `*_FUT`) jump at rolls.
5. **Sina hourly bars follow the provider's end times.** A China futures 1h / 4h bar may span the lunch break, the night session and the next morning; its `datetime` is only the end minus the period, so rely on `close_time`. A-share 4h bars are Sina's 240-minute bars, one per trading day.
6. **History lengths differ.** Sina serves only the latest ~1000 bars, so its 1h files usually cover less than a year and its 4h files two to four years; Yahoo hourly files cover about two years; Dukascopy 15-minute files start in 2017. `files.csv` has the first and last bar of every file.
7. **Processing**: bars are sorted by time; a repeated timestamp keeps the later record; the last trading day of four forex files (EURJPY, EURUSD, GBPUSD, USDJPY) had two records each and the later one (the final value after the close) was kept. No price was removed, changed or filled in.
8. When an instrument has no 1h or 4h file, resample its 15-minute bars (see the example below).

### Quick start

```python
import pandas as pd

# read a local file
daily = pd.read_csv("data/cn_stock/1d/CNS_600519.csv", parse_dates=["date"], index_col="date")

# read straight from GitHub without cloning
url = "https://raw.githubusercontent.com/erha-erha/quant-kline-data/main/data/crypto/1d/BTCUSDT.csv"
btc = pd.read_csv(url, parse_dates=["date"], index_col="date")

# intraday files: datetime is local time; convert timestamp for time-zone-aware times
m15 = pd.read_csv("data/us_stock/15m/US_AAPL.csv", parse_dates=["datetime"], index_col="datetime")
m15["utc"] = pd.to_datetime(m15["timestamp"], unit="s", utc=True)

# resample 15-minute bars to hourly bars (the US regular session starts at 09:30, hence the 30-minute offset)
h1 = m15.resample("1h", offset="30min").agg(
    {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}
).dropna(subset=["open"])

# find instruments by market or name
instruments = pd.read_csv("instruments.en.csv")
print(instruments[instruments["market"] == "China futures"][["id", "name", "exchange"]])
```

### Download

- Whole dataset: `git clone https://github.com/erha-erha/quant-kline-data.git`, or **Code → Download ZIP** on this page; [Releases](https://github.com/erha-erha/quant-kline-data/releases/latest) also carry a zip.
- Single file: the **Raw** button on a file page, or `https://raw.githubusercontent.com/erha-erha/quant-kline-data/main/data/<market>/<bar size>/<id>.csv`.

### Sources

BaoStock (back-adjusted A-share daily), Tencent Finance (unadjusted A-share daily), Sina Finance (A-share and China futures intraday, China futures continuous daily), per-contract daily data of SHFE / INE / DCE / CZCE / CFFEX (fetched with AKShare; main continuous series built here), Yahoo Finance (US stocks, ETFs, forex, global futures, SSE Composite, BTC-USD), Dukascopy (15-minute CFDs) and Binance (crypto).

### Disclaimer

The data comes from the public sources above, whose owners keep all rights. This repository only organizes and reformats it for personal study and research; it is provided without any guarantee of accuracy, completeness or timeliness and is not investment advice. Follow each source's terms of use. If you own rights to any of this data and want it removed, please open an issue.
