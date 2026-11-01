# 多市场 K 线数据集

**简体中文** | [English](README.en.md)

A 股、国内期货、指数、美股、海外期货、加密货币、外汇的 K 线数据，Parquet + Zstd 格式，一个文件对应一个品种的一个周期。

<!-- coverage:start -->
| 市场 | 目录 | 品种 | 文件 | K线 | 周期 | 起止 |
|---|---|---:|---:|---:|---|---|
| A股 | [`cn_stock`](data/cn_stock/README.md) | 111 | 143 | 522,952 | 1d 4h 1h | 2005-01-04 – 2026-09-24 |
| 国内期货 | [`cn_futures`](data/cn_futures/README.md) | 77 | 107 | 259,610 | 1d 4h 1h | 2005-01-04 – 2026-09-24 |
| 指数 | [`index`](data/index/README.md) | 3 | 3 | 337,304 | 1d 15m | 1997-07-02 – 2026-09-04 |
| 美股 | [`us_stock`](data/us_stock/README.md) | 72 | 116 | 2,294,263 | 1d 1h 15m | 1980-12-12 – 2026-09-24 |
| 海外期货 | [`global_futures`](data/global_futures/README.md) | 26 | 32 | 1,710,915 | 1d 15m | 2005-01-03 – 2026-09-24 |
| 加密货币 | [`crypto`](data/crypto/README.md) | 16 | 30 | 265,838 | 1d 4h 1h | 2014-09-17 – 2026-09-05 |
| 外汇 | [`forex`](data/forex/README.md) | 8 | 8 | 33,509 | 1d | 2010-01-01 – 2026-09-04 |
| **合计** | | **313** | **439** | **5,424,391** | | |
<!-- coverage:end -->

点目录可按中文名查品种。

## 使用

```bash
pip install pandas pyarrow
```

```python
import pandas as pd

df = pd.read_parquet("data/cn_stock/1d/CNS_600519.parquet")

# 不下载仓库，直接读取
url = "https://raw.githubusercontent.com/erha-erha/quant-kline-data/main/data/crypto/1d/BTCUSDT.parquet"
btc = pd.read_parquet(url)
```

## 字段

| 字段 | 含义 |
|---|---|
| `date` | 交易日（日线） |
| `datetime` | K 线开始时间，交易所当地时间（日内） |
| `timestamp` | K 线开始时间的 Unix 秒（日内） |
| `open` `high` `low` `close` `volume` | 开高低收、成交量 |
| `close_time` | K 线结束时间，部分小时线才有 |

## 使用前必看

1. **同一标的可能有两份数据，算收益用复权，看历史报价用不复权。** 复权：`CNS_600519`、`US_AAPL`、`CNF_AU`；不复权或未按分红调整：`CN600519`、`AAPL`、`CN_AU`。
2. **`USF_*` 的日线不是期货价格**，而是对应 ETF 的复权价（见 `files.csv` 的 `proxy` 列）。真实期货价格在 `*_FUT`。
3. **15 分钟线是差价合约报价**，价格与期货不完全相同，成交量也不是交易所成交量。
4. **连续合约不等于可交易合约。** `CNF_*` 的早期价格不是当时的成交价；`CN_*`、`*_FUT` 在换月处有跳空。
5. **国内期货 1h / 4h 的时间以 `close_time` 为准**，一根 K 线可能跨午休和夜盘。
6. **成交量单位和历史长度因文件而异**，不能跨口径直接比较。每个文件的口径和起止时间见 `files.csv`、`profiles.zh.csv`。

## 目录

```
data/<市场>/<周期>/<代码>.parquet   K 线
files.csv                           文件清单：口径、行数、起止时间
instruments.zh.csv                  品种表：名称、交易所、时区
profiles.zh.csv                     口径表：复权方式、时间、成交量单位
markets.csv                         市场表
tools/kline.py                      入库和校验工具
```

## 新增数据

新市场先登记到 `markets.csv`，新口径登记到 `profiles.*.csv`，新品种登记到 `instruments.*.csv`。然后：

```bash
python tools/kline.py add 代码.csv --market cn_stock --level 5m --profile 口径名
python tools/kline.py check
```

文件名就是代码。新周期（如 `5m`、`1w`）、新列（如持仓量）都可以直接加，清单和文档会自动更新。

**容量预算：** 单文件不超过 50 MB，`data/` 总量不超过 500 MB，另一半空间留给 git 历史；`check` 会报告用量。新增品种的增量只有文件本身，但重写已有文件时，旧版本会永久留在 git 历史里，所以全量刷新要少做。

数据仅供学习研究，不保证准确完整，不构成投资建议。
