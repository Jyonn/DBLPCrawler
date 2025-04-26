# DBLP 论文爬取工具 (2025)

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

爬取历年 WWW 和 SIGKDD 的论文：

```bash
python worker.py --venues www+sigkdd
```

运行成功后，2025年的 WWW 会议文章信息已被解析在 `data/conf-www/www2025.yaml` 中。

## Arguments

| 参数              | 说明                                                       |
|-----------------|----------------------------------------------------------|
| --venues        | 需要爬取的会议名称，多个会议用 + 连接，会议简称可以查阅 [venue.yaml](venue.yaml)   |
| --skip-parse    | 含有此参数只会爬取数据，不会解析                                         |
| --strict-prefix | 严格解析当前 Venue 的文章。例如，ACL列表中包含1984年 COLING会议的连接，含有此参数会自动跳过 |
| --always-update | 含有此参数，如果数据已经存在，会强制更新，重新下载并解析                             |

## Examples

```bash
python worker.py --venues acl --skip-parse  # 只爬取数据，不解析
python worker.py --venues acl  # 数据已经在前一步爬取，仅解析数据
python worker.py --venues acl --always-update  # 强制重新爬取并解析数据
```
