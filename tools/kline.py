#!/usr/bin/env python3
"""K 线数据入库工具。

  add    CSV 转 Parquet，写入 data/<市场>/<周期>/<代码>.parquet，并更新索引和文档
  build  根据 files.csv 重新生成 README 覆盖表和各市场品种表
  check  校验全部数据，并报告容量预算
"""
import argparse
import csv
import re
import sys
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parent.parent

# GitHub 超过 50MB 警告、超过 100MB 拒收；仓库建议不超过 1GB，另一半留给 git 历史
FILE_BUDGET = 50 * 1024**2
DATA_BUDGET = 500 * 1024**2

PRICE_COLUMNS = ["open", "high", "low", "close", "volume"]
DAILY_COLUMNS = ["date", *PRICE_COLUMNS]
INTRADAY_COLUMNS = ["datetime", "timestamp", *PRICE_COLUMNS]
TIME_COLUMNS = {"date", "datetime", "close_time"}
LEVEL_PATTERN = re.compile(r"^(\d+)(m|h|d|w|mo)$")
LEVEL_MINUTES = {"m": 1, "h": 60, "d": 1440, "w": 10080, "mo": 43200}
LEVEL_NAMES = {"1d": "日线", "4h": "4小时", "1h": "1小时", "15m": "15分钟"}
FILE_FIELDS = ["path", "id", "level", "profile", "rows", "start", "end", "proxy"]


def required_columns(level):
    return DAILY_COLUMNS if level == "1d" else INTRADAY_COLUMNS


def level_key(level):
    match = LEVEL_PATTERN.match(level)
    return -int(match[1]) * LEVEL_MINUTES[match[2]]


def read_table(name):
    with open(ROOT / name, encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_table(name, rows, fields):
    # 保持原文件是否带 BOM，避免产生无意义的差异
    bom = (ROOT / name).read_bytes().startswith(b"\xef\xbb\xbf")
    with open(ROOT / name, "w", encoding="utf-8-sig" if bom else "utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def table_fields(name):
    with open(ROOT / name, encoding="utf-8-sig", newline="") as handle:
        return next(csv.reader(handle))


def load_csv(source, level):
    """读取 K 线 CSV，统一列类型。必需列之外的新列（如持仓量）按 float64 保留。"""
    frame = pd.read_csv(source)
    missing = set(required_columns(level)) - set(frame.columns)
    if missing:
        raise ValueError(f"{source}: 缺少列 {sorted(missing)}")
    for column in frame.columns:
        if column in TIME_COLUMNS:
            frame[column] = pd.to_datetime(frame[column], format="ISO8601").astype("datetime64[ms]")
        elif column == "timestamp":
            frame[column] = frame[column].astype("int64")
        else:
            frame[column] = pd.to_numeric(frame[column]).astype("float64")
    key = frame[required_columns(level)[0]]
    if frame[required_columns(level)].isna().any().any():
        raise ValueError(f"{source}: 必需列有空值")
    if not key.is_monotonic_increasing or key.duplicated().any():
        raise ValueError(f"{source}: 时间未严格递增")
    return pa.Table.from_pandas(frame, preserve_index=False)


def write_parquet(table, target):
    delta = {c: "DELTA_BINARY_PACKED" for c in table.column_names if c in TIME_COLUMNS or c == "timestamp"}
    target.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(
        table,
        target,
        compression="zstd",
        compression_level=19,
        use_dictionary=False,
        column_encoding=delta,
        row_group_size=100_000,
    )
    if not pq.read_table(target).equals(table):
        raise ValueError(f"{target}: 写入后回读不一致")


def time_range(table, level):
    column = table[required_columns(level)[0]].to_pandas()
    pattern = "%Y-%m-%d" if level == "1d" else "%Y-%m-%d %H:%M"
    return column.iloc[0].strftime(pattern), column.iloc[-1].strftime(pattern)


def add_bar_size(table_name, id_field, bar_field, symbol, level):
    rows = read_table(table_name)
    match = next((row for row in rows if row[id_field] == symbol), None)
    if match is None:
        raise ValueError(f"{table_name} 里没有 {symbol}，请先登记这个品种")
    sizes = [size for size in match[bar_field].split(";") if size]
    if level not in sizes:
        match[bar_field] = ";".join(sorted(sizes + [level], key=level_key))
        write_table(table_name, rows, table_fields(table_name))


def command_add(args):
    if not LEVEL_PATTERN.match(args.level):
        raise ValueError(f"周期格式不对：{args.level}，应类似 5m、1h、1d、1w、1mo")
    if args.market not in {row["market"] for row in read_table("markets.csv")}:
        raise ValueError(f"markets.csv 里没有市场 {args.market}，请先登记")
    if args.profile not in {row["口径"] for row in read_table("profiles.zh.csv")}:
        raise ValueError(f"profiles.zh.csv 里没有口径 {args.profile}，请先登记")

    files = read_table("files.csv")
    for source in map(Path, args.csv):
        symbol = source.stem
        table = load_csv(source, args.level)
        add_bar_size("instruments.zh.csv", "代码", "周期", symbol, args.level)
        add_bar_size("instruments.en.csv", "id", "bar_sizes", symbol, args.level)
        path = f"data/{args.market}/{args.level}/{symbol}.parquet"
        write_parquet(table, ROOT / path)
        start, end = time_range(table, args.level)
        record = dict(zip(FILE_FIELDS, [path, symbol, args.level, args.profile, table.num_rows, start, end, args.proxy]))
        current = next((row for row in files if row["path"] == path), None)
        if current is None:
            files.append(record)
        else:
            current.update(record)
        print(f"{path}  {table.num_rows} 行  {(ROOT / path).stat().st_size / 1024:.0f} KB")
    write_table("files.csv", files, FILE_FIELDS)
    build_docs()


def coverage_table(files, markets, language):
    if language == "zh":
        header = "| 市场 | 目录 | 品种 | 文件 | K线 | 周期 | 起止 |"
    else:
        header = "| Market | Folder | Symbols | Files | Bars | Bar sizes | Range |"
    lines = [header, "|---|---|---:|---:|---:|---|---|"]
    for market in markets:
        rows = [row for row in files if row["path"].split("/")[1] == market["market"]]
        if not rows:
            continue
        levels = sorted({row["level"] for row in rows}, key=level_key)
        lines.append(
            f"| {market[language]} | [`{market['market']}`](data/{market['market']}/{'README.md' if language == 'zh' else 'README.en.md'}) "
            f"| {len({row['id'] for row in rows})} | {len(rows)} | {sum(int(row['rows']) for row in rows):,} "
            f"| {' '.join(levels)} | {min(row['start'] for row in rows)[:10]} – {max(row['end'] for row in rows)[:10]} |"
        )
    total = "合计" if language == "zh" else "Total"
    lines.append(
        f"| **{total}** | | **{len({row['id'] for row in files})}** | **{len(files)}** "
        f"| **{sum(int(row['rows']) for row in files):,}** | | |"
    )
    return "\n".join(lines)


def market_page(market, files, instruments, language):
    if language == "zh":
        switch = "**简体中文** | [English](README.en.md)"
        header = "| 代码 | 名称 | 交易所 | 周期 |"
        fields = ("代码", "名称", "交易所")
    else:
        switch = "[简体中文](README.md) | **English**"
        header = "| ID | Name | Exchange | Bar sizes |"
        fields = ("id", "name", "exchange")
    lines = [f"# {market[language]}", "", switch, "", header, "|---|---|---|---|"]
    by_id = {}
    for row in files:
        if row["path"].split("/")[1] == market["market"]:
            by_id.setdefault(row["id"], []).append(row)
    for item in instruments:
        symbol, name, exchange = (item[field] for field in fields)
        if symbol not in by_id:
            continue
        links = []
        for row in sorted(by_id[symbol], key=lambda r: level_key(r["level"])):
            label = LEVEL_NAMES.get(row["level"], row["level"]) if language == "zh" else row["level"]
            links.append(f"[{label}]({row['level']}/{symbol}.parquet)")
        lines.append(f"| `{symbol}` | {name} | {exchange} | {' '.join(links)} |")
    return "\n".join(lines) + "\n"


def build_docs():
    files = read_table("files.csv")
    markets = read_table("markets.csv")
    for language, readme, table in (("zh", "README.md", "instruments.zh.csv"), ("en", "README.en.md", "instruments.en.csv")):
        text = (ROOT / readme).read_text(encoding="utf-8")
        block = f"<!-- coverage:start -->\n{coverage_table(files, markets, language)}\n<!-- coverage:end -->"
        text, count = re.subn(r"<!-- coverage:start -->.*<!-- coverage:end -->", lambda _: block, text, flags=re.S)
        if count != 1:
            raise ValueError(f"{readme}: 找不到覆盖表标记")
        (ROOT / readme).write_text(text, encoding="utf-8")
        instruments = read_table(table)
        for market in markets:
            if any(row["path"].split("/")[1] == market["market"] for row in files):
                page = ROOT / "data" / market["market"] / readme
                page.parent.mkdir(parents=True, exist_ok=True)
                page.write_text(market_page(market, files, instruments, language), encoding="utf-8")


def command_check(_):
    errors = []
    files = read_table("files.csv")
    known_markets = {row["market"] for row in read_table("markets.csv")}
    known_profiles = {row["口径"] for row in read_table("profiles.zh.csv")}
    symbols_zh = {row["代码"] for row in read_table("instruments.zh.csv")}
    symbols_en = {row["id"] for row in read_table("instruments.en.csv")}
    listed = {row["path"] for row in files}
    on_disk = {str(path.relative_to(ROOT)) for path in (ROOT / "data").rglob("*.parquet")}
    errors += [f"files.csv 有记录但文件不存在：{path}" for path in sorted(listed - on_disk)]
    errors += [f"文件未登记到 files.csv：{path}" for path in sorted(on_disk - listed)]
    errors += [f"残留 CSV：{path.relative_to(ROOT)}" for path in (ROOT / "data").rglob("*.csv")]

    total = 0
    largest = (0, "")
    for row in files:
        path = ROOT / row["path"]
        if not path.exists():
            continue
        size = path.stat().st_size
        total += size
        largest = max(largest, (size, row["path"]))
        if size > FILE_BUDGET:
            errors.append(f"{row['path']}: {size / 1024**2:.1f} MB，超过单文件预算")
        if row["path"].split("/")[1] not in known_markets:
            errors.append(f"{row['path']}: 市场未登记")
        if row["profile"] not in known_profiles:
            errors.append(f"{row['path']}: 口径未登记")
        if row["id"] not in symbols_zh or row["id"] not in symbols_en:
            errors.append(f"{row['path']}: 品种未登记")
        parquet = pq.ParquetFile(path)
        metadata = parquet.metadata
        columns = parquet.schema_arrow.names
        if metadata.num_rows != int(row["rows"]):
            errors.append(f"{row['path']}: 行数 {metadata.num_rows} 与 files.csv 的 {row['rows']} 不符")
        if not set(required_columns(row["level"])) <= set(columns):
            errors.append(f"{row['path']}: 缺少必需列")
        for group in range(metadata.num_row_groups):
            group_data = metadata.row_group(group)
            for index in range(group_data.num_columns):
                if group_data.column(index).compression != "ZSTD":
                    errors.append(f"{row['path']}: 列未使用 Zstd")
        table = parquet.read(columns=required_columns(row["level"])[:1])
        if time_range(table, row["level"]) != (row["start"], row["end"]):
            errors.append(f"{row['path']}: 起止时间与 files.csv 不符")
        key = table.column(0).to_pandas()
        if not key.is_monotonic_increasing or key.duplicated().any():
            errors.append(f"{row['path']}: 时间未严格递增")

    print(f"文件 {len(files)} 个，K 线 {sum(int(row['rows']) for row in files):,} 根")
    print(f"数据 {total / 1024**2:.1f} MB / 预算 {DATA_BUDGET / 1024**2:.0f} MB，已用 {total / DATA_BUDGET:.0%}")
    print(f"最大文件 {largest[1]}：{largest[0] / 1024**2:.1f} MB / 预算 {FILE_BUDGET / 1024**2:.0f} MB")
    if total > DATA_BUDGET:
        errors.append("数据总量超过预算")
    for error in errors:
        print("错误:", error, file=sys.stderr)
    if errors:
        sys.exit(1)
    print("校验通过")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    add = commands.add_parser("add", help="CSV 转 Parquet 并入库，文件名即代码")
    add.add_argument("csv", nargs="+")
    add.add_argument("--market", required=True)
    add.add_argument("--level", required=True)
    add.add_argument("--profile", required=True)
    add.add_argument("--proxy", default="")
    add.set_defaults(run=command_add)
    commands.add_parser("build", help="重新生成文档").set_defaults(run=lambda _: build_docs())
    commands.add_parser("check", help="校验数据和容量预算").set_defaults(run=command_check)
    args = parser.parse_args()
    try:
        args.run(args)
    except ValueError as error:
        sys.exit(f"错误: {error}")


if __name__ == "__main__":
    main()
