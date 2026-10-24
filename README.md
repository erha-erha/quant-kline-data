# 多市场 K 线数据集 · Multi-Market K-line Dataset

[中文](#中文) · [English](#english)

<a id="中文"></a>

## 中文

覆盖 A 股、国内期货、指数、美股、海外期货、加密货币、外汇的 K 线数据，共 **313 个品种、439 个文件、5,424,391 根 K 线**，数据截至 2026 年 9 月。全部是普通 CSV，一个文件对应一个品种的一个周期，用 Excel、pandas 或任何语言都能直接读，不依赖任何软件。可以用来做量化研究、回测、因子与机器学习实验。

### 覆盖范围

| 市场 | 文件夹 | 品种 | 文件 | K线根数 | 周期 | 起止 | 主要内容 |
|---|---|---:|---:|---:|---|---|---|
| A股 | `cn_stock` | 111 | 143 | 522,952 | 1d 4h 1h | 2005-01-04 – 2026-09-24 | 沪深大盘股，如贵州茅台、宁德时代 |
| 国内期货 | `cn_futures` | 77 | 107 | 259,610 | 1d 4h 1h | 2005-01-04 – 2026-09-24 | 五家期货交易所 62 个品种的主力连续，另有 15 个新浪连续合约 |
| 指数 | `index` | 3 | 3 | 337,304 | 1d 15m | 1997-07-02 – 2026-09-04 | 上证综指日线；富时中国A50、恒生指数 15 分钟 CFD |
| 美股 | `us_stock` | 72 | 116 | 2,294,263 | 1d 1h 15m | 1980-12-12 – 2026-09-24 | 标普500大盘股，及 SPY、QQQ、GLD、TLT 等 ETF |
| 海外期货 | `global_futures` | 26 | 32 | 1,710,915 | 1d 15m | 2005-01-03 – 2026-09-24 | 美国股指、国债、美元指数、能源、金属、农产品期货 |
| 加密货币 | `crypto` | 16 | 30 | 265,838 | 1d 4h 1h | 2014-09-17 – 2026-09-05 | BTC、ETH 等 15 个 Binance USDT 交易对，及 Yahoo BTC-USD |
| 外汇 | `forex` | 8 | 8 | 33,509 | 1d | 2010-01-01 – 2026-09-04 | 8 个主要货币对 |
| **合计** | | **313** | **439** | **5,424,391** | | | |

周期：`1d` 日线、`4h` 4 小时、`1h` 1 小时、`15m` 15 分钟。每个品种有哪些周期、每个文件的起止时间见 `files.csv`。

### 目录结构

```
data/<市场>/<周期>/<代码>.csv    K 线，例如 data/cn_stock/1d/CNS_600519.csv
instruments.csv                 品种表：代码、中英文名称、交易所、时区、周期、备注
files.csv                       文件清单：路径、代码、周期、数据口径 profile、行数、起止时间、代理 ETF
profiles.csv                    数据口径表（中英文）：来源、复权方式、时间口径、成交量单位
```

### 文件格式

日线，例如 `data/cn_stock/1d/CN600519.csv`：

```
date,open,high,low,close,volume
2026-09-04,1295.88,1338.86,1295.6,1330,45416
```

日内（15m / 1h / 4h），例如 `data/us_stock/15m/US_AAPL.csv` 和 `data/cn_stock/1h/CN600519.csv`：

```
datetime,timestamp,open,high,low,close,volume
2026-08-31 15:45,1788205500,316.426,317.437,315.717,316.726,40.428
```

```
datetime,timestamp,open,high,low,close,volume,close_time
2026-09-04 14:00,1788501600,1329.08,1334,1328.62,1330,860217,2026-09-04 15:00
```

| 字段 | 含义 |
|---|---|
| `date` | 交易日；国内期货的夜盘计入下一交易日，外汇以伦敦时间零点切日 |
| `datetime` | K 线开始时间，交易所当地时间（不带时区）；时区见 `instruments.csv` 的 `timezone` 列 |
| `timestamp` | K 线开始时间的 Unix 时间戳（秒），与时区无关，跨夏令时计算时用它 |
| `open` `high` `low` `close` | 开盘、最高、最低、收盘价 |
| `volume` | 成交量，单位随来源不同，见下表 |
| `close_time` | 来源给出的 K 线结束时间（当地时间），只有新浪 1h / 4h（A 股、国内期货）和 Yahoo 1h（美股）文件有 |

价格和成交量保留来源原值，没有四舍五入，所以部分来源的数字带有较长的小数尾数（如 Yahoo 的 `1.1621150970458984`）。

### 数据口径

`files.csv` 的 `profile` 列说明每个文件属于哪一类，同样的内容也在 `profiles.csv` 里：

| profile | 文件 | 内容 | 来源 | 复权 / 调整 | 时间 | 成交量单位 |
|---|---|---|---|---|---|---|
| `baostock_daily_hfq` | CNS_* | A股日线（后复权） | BaoStock | 后复权：最早的价格保持原值，此后按分红送转逐次放大；价格不等于当时的报价，但涨跌幅即含分红再投资的真实收益 | 交易日日期 | 股 |
| `tencent_daily_raw` | CN###### 1d | A股日线（不复权） | 腾讯财经 | 不复权：除权除息日会出现价格跳空 | 交易日日期 | 手（1手=100股） |
| `sina_intraday_stock` | CN###### 1h / 4h | A股小时线（不复权） | 新浪财经 | 不复权 | 1h：每天4根（09:30、10:30、13:00、14:00 开始）；4h：来源的240分钟线，每个交易日1根（09:30–15:00）。datetime 由「结束时间减周期」得到，close_time 为来源给出的结束时间 | 股 |
| `cn_futures_main_continuous` | CNF_* | 国内期货主力连续（比例后复权） | 上期所、能源中心、大商所、郑商所、中金所逐合约日线（经 AKShare 获取） | 主力合约 = 当日持仓量最大且不回到更早到期月的合约；第 t 日收盘决定换月、t 日之后生效，换月前的历史按 新合约收盘/旧合约收盘 等比例调整。连续序列的涨跌即滚动持有的收益，但早期价格不是当时可成交的价格 | 交易日日期（夜盘计入下一交易日） | 手（主力合约） |
| `sina_futures_continuous_daily` | CN_* 1d | 国内期货连续（新浪 XX0，不复权） | 新浪财经 | 新浪连续合约，换月不调整、会有跳空；换月规则与成交量口径以新浪为准，未经审计 | 交易日日期 | 手 |
| `sina_intraday_futures` | CN_* 1h / 4h | 国内期货小时线（新浪连续，不复权） | 新浪财经 | 新浪连续合约，换月不调整 | 按来源的结束时间切分：一根K线覆盖结束时间之前的 1 或 4 个交易小时，可能跨午休、夜盘和次日早盘。datetime 是「结束时间减周期」的名义值，以 close_time 为准 | 手 |
| `yahoo_daily_adjusted` | US_* 1d | 美股日线（复权，总回报） | Yahoo Finance（复权价） | 按拆股和现金分红向前复权（Yahoo 复权收盘价口径），涨跌幅为总回报 | 交易日日期 | 股（按拆股调整） |
| `dukascopy_stock_15m` | US_* 15m | 美股15分钟线（Dukascopy 股票 CFD，复权） | Dukascopy（BID 1 分钟线合成 15 分钟） | 按 Yahoo 的拆股和分红事件向前复权（与 Yahoo 复权收盘价同一方法），涨跌幅为总回报 | 常规交易时段（美东 09:30–16:00），K线开始时间 | Dukascopy CFD 成交量，不是交易所成交量 |
| `yahoo_daily` | AAPL … XOM, SPY, QQQ, GLD, TLT, SSE, BTC-USD 1d | Yahoo 日线 | Yahoo Finance | Yahoo 原始价格：已按拆股调整，未按分红调整 | 交易日日期 | 股 / 份额；BTC-USD 为美元成交额；SSE 的成交量早期为 0、口径不稳定，不建议使用 |
| `yahoo_1h` | AAPL … XOM, SPY, QQQ, GLD, TLT 1h | 美股小时线（常规交易时段） | Yahoo Finance | Yahoo 原始价格：已按拆股调整，未按分红调整 | 美东时间 09:30–16:00，每天最后一根为 15:30–16:00 半小时；提前收盘日更短。close_time 为结束时间 | 股 |
| `etf_proxy_daily` | USF_* 1d | 美国期货的 ETF 代理日线（复权） | Yahoo Finance（复权价） | 价格是对应 ETF（见 files.csv 的 proxy 列）的复权价，不是期货价格；没有换月跳空，做空 ETF 的借券成本未计入 | 交易日日期 | ETF 份额 |
| `dukascopy_cfd_15m` | USF_* 15m, IDX_A50, IDX_HSI | 期货 / 指数 15分钟线（Dukascopy CFD） | Dukascopy（BID 1 分钟线合成 15 分钟） | CFD 报价，未调整；可作为对应期货或指数的日内代理，价格水平与期货不完全相同 | 近 24 小时交易，K线开始时间 | Dukascopy CFD 成交量，不是交易所成交量 |
| `yahoo_futures_daily` | *_FUT | 海外期货近月连续日线 | Yahoo Finance（=F 代码） | Yahoo 近月连续合约，换月不调整、会有跳空，不能直接当作持有收益 | 交易日日期 | 手 |
| `binance_spot` | *USDT | 加密货币现货（Binance） | Binance 公开行情 | 无调整 | UTC 时间，K线开始时间 | 基础币数量（如 BTCUSDT 为 BTC 个数） |
| `yahoo_fx_daily` | EURUSD … | 外汇日线 | Yahoo Finance（=X 代码） | 报价，无调整 | 交易日日期（以伦敦时间零点切日） | 无（多为 0） |

### 使用前必读

1. **同一个标的可能有两份数据，口径不同。** `CNS_600519` 是 BaoStock 后复权日线（成交量单位为股），`CN600519` 是腾讯不复权日线（单位为手，另有新浪小时线）；`US_AAPL` 是 Yahoo 复权（总回报）日线加 Dukascopy 15 分钟线，`AAPL` 是 Yahoo 未按分红调整的日线加小时线；`CNF_AU` 是比例后复权的主力连续，`CN_AU` 是新浪 AU0 连续（不复权，日线到 2024-07-17）。算收益用复权数据，看历史报价用不复权数据。
2. **`USF_*` 的日线不是期货价格**，而是对应 ETF 的复权价格（例如 `USF_ES` 是 SPY、`USF_GC` 是 GLD、`USF_ZC` 是 CORN），ETF 代码见 `files.csv` 的 `proxy` 列。标普500、原油、黄金、白银、铜、天然气另有真实的期货近月连续价格，在 `*_FUT` 文件里（Yahoo `ES=F` 等）。
3. **15 分钟线来自 Dukascopy 的 CFD 报价**（BID 价），不是交易所成交数据；价格水平与期货不完全相同，成交量是 CFD 成交量。美股 CFD 已按 Yahoo 的拆股分红事件复权。
4. **连续合约不能直接当作可交易合约。** 后复权的主力连续（`CNF_*`）涨跌等于滚动持有的收益，但早期价格不是当时的成交价；不复权的连续（`CN_*`、`*_FUT`）在换月处有跳空。
5. **新浪小时线按结束时间切分。** 国内期货的 1h / 4h 一根 K 线可能跨午休、夜盘和次日早盘，`datetime` 只是「结束时间减周期」的名义值，请以 `close_time` 为准。A 股的 4h 是新浪 240 分钟线，每个交易日一根。
6. **历史长度不一。** 新浪小时线只提供最近约 1000 根，所以 1h 一般不到一年、4h 两到四年；Yahoo 小时线约两年；Dukascopy 15 分钟线从 2017 年起。每个文件的起止时间见 `files.csv`。
7. **整理时的处理**：按时间排序；同一时间戳出现两次时保留后一条；4 个外汇日线文件（EURJPY、EURUSD、GBPUSD、USDJPY）最后一个交易日各有两条记录，保留了时间较晚的那条（收盘后的最终值）。没有剔除、修改或插补任何价格。
8. 某个品种没有 1 小时或 4 小时线时，可以从 15 分钟线自己重采样（见下面的例子）。

### 快速开始

```python
import pandas as pd

# 本地读取
daily = pd.read_csv("data/cn_stock/1d/CNS_600519.csv", parse_dates=["date"], index_col="date")

# 不下载仓库，直接读 GitHub 上的文件
url = "https://raw.githubusercontent.com/erha-erha/quant-kline-data/main/data/crypto/1d/BTCUSDT.csv"
btc = pd.read_csv(url, parse_dates=["date"], index_col="date")

# 日内文件：datetime 是当地时间；需要带时区的时间时用 timestamp 换算
m15 = pd.read_csv("data/us_stock/15m/US_AAPL.csv", parse_dates=["datetime"], index_col="datetime")
m15["utc"] = pd.to_datetime(m15["timestamp"], unit="s", utc=True)

# 15 分钟线重采样为 1 小时线（美股常规时段从 09:30 开始，所以偏移 30 分钟）
h1 = m15.resample("1h", offset="30min").agg(
    {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}
).dropna(subset=["open"])

# 按市场、名称筛选品种
instruments = pd.read_csv("instruments.csv")
print(instruments[instruments["market_en"] == "China futures"][["id", "name_zh", "name_en", "exchange"]])
```

### 下载

- 整个数据集：`git clone https://github.com/erha-erha/quant-kline-data.git`，或页面上的 **Code → Download ZIP**；Releases 里也有打包好的 zip。
- 单个文件：在文件页面点 **Raw**，或用 `https://raw.githubusercontent.com/erha-erha/quant-kline-data/main/data/<市场>/<周期>/<代码>.csv`。

### 数据来源

BaoStock（A 股后复权日线）、腾讯财经（A 股不复权日线）、新浪财经（A 股与国内期货小时线、国内期货连续日线）、上期所 / 上海国际能源交易中心 / 大商所 / 郑商所 / 中金所逐合约日线（经 AKShare 获取，自行拼接主力连续）、Yahoo Finance（美股、ETF、外汇、海外期货、上证综指、BTC-USD）、Dukascopy（15 分钟 CFD）、Binance（加密货币）。

### 免责声明

数据来自上述公开来源，版权归原数据提供方所有。本仓库只做了整理和格式转换，仅供个人学习与研究使用，不保证准确、完整、及时，不构成任何投资建议。使用时请遵守各数据源的使用条款；如果权利人认为某些数据不应公开，请提 Issue，会尽快删除。

---

<a id="english"></a>

## English

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

### Layout

```
data/<market>/<bar size>/<id>.csv   bars, e.g. data/cn_stock/1d/CNS_600519.csv
instruments.csv                     instruments: id, Chinese / English names, exchange, time zone, bar sizes, notes
files.csv                           files: path, id, bar size, data profile, rows, first / last bar, proxy ETF
profiles.csv                        data profiles (Chinese / English): source, adjustment, time convention, volume unit
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
| `datetime` | bar start in the exchange's local time (no offset); the time zone is the `timezone` column of `instruments.csv` |
| `timestamp` | bar start as a Unix timestamp (seconds), independent of time zones; use it for arithmetic across daylight-saving changes |
| `open` `high` `low` `close` | open, high, low and close prices |
| `volume` | volume; its unit depends on the source, see the table below |
| `close_time` | the bar end given by the source (local time); only in Sina 1h / 4h (A-shares, China futures) and Yahoo 1h (US stocks) files |

Prices and volumes are kept exactly as the sources gave them, without rounding, so some values have long decimal tails (e.g. Yahoo's `1.1621150970458984`).

### Data profiles

The `profile` column of `files.csv` tells which group a file belongs to; `profiles.csv` holds the same table:

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
instruments = pd.read_csv("instruments.csv")
print(instruments[instruments["market_en"] == "China futures"][["id", "name_zh", "name_en", "exchange"]])
```

### Download

- Whole dataset: `git clone https://github.com/erha-erha/quant-kline-data.git`, or **Code → Download ZIP** on this page; Releases also carry a zip.
- Single file: the **Raw** button on a file page, or `https://raw.githubusercontent.com/erha-erha/quant-kline-data/main/data/<market>/<bar size>/<id>.csv`.

### Sources

BaoStock (back-adjusted A-share daily), Tencent Finance (unadjusted A-share daily), Sina Finance (A-share and China futures intraday, China futures continuous daily), per-contract daily data of SHFE / INE / DCE / CZCE / CFFEX (fetched with AKShare; main continuous series built here), Yahoo Finance (US stocks, ETFs, forex, global futures, SSE Composite, BTC-USD), Dukascopy (15-minute CFDs) and Binance (crypto).

### Disclaimer

The data comes from the public sources above, whose owners keep all rights. This repository only organizes and reformats it for personal study and research; it is provided without any guarantee of accuracy, completeness or timeliness and is not investment advice. Follow each source's terms of use. If you own rights to any of this data and want it removed, please open an issue.
