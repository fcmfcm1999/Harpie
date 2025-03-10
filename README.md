# Harpie Daily Wallet Scan (Harpie每日钱包扫描）

## 简介
本项目实现了Harpie项目的钱包每日自动扫描功能, 仅需一次配置运行, 之后每日会在服务器上按照你设定的运行时间自动执行。

## 依赖
在运行此代码前，请确保已安装以下 Python 依赖库：

```sh
pip install requests python-dateutil pysocks

```

## 配置文件
本项目依赖 `config.json` 配置文件，该文件应包含如下结构：

```json
{
  "wallets": [
    {
      "address": "0x你的钱包地址",
      "proxy": "http://你的代理地址（可选）",
      "chainId": 1,
      "runTime": "06:30"
    }
  ]
}
```

其中：
- `address`：钱包地址
- `proxy`：代理地址（可选），支持http和socks5h
- `chainId`：区块链 ID（1 代表 Ethereum，137 代表 Polygon，8453 代表 Base，42161 代表 Arbitrum）
- `runTime`：每天定时执行该钱包扫描的北京时间（24 小时制，格式为 HH:MM）

## 运行方式

### 配置定时任务（Crontab）(推荐)

本项目提供了 `cron_setup.sh` 脚本，可自动将定时任务添加到 `crontab`，以便每天在指定时间运行钱包扫描。

#### 设置定时任务

1. 确保 `jq` 已安装（用于解析 JSON 文件）：
   ```sh
   sudo apt-get install jq  # Debian/Ubuntu
   sudo yum install jq       # CentOS
   ```

2. 运行脚本更新 `crontab` 任务：
   ```sh
   chmod +x cron_setup.sh
   bash cron_setup.sh
   ```

3. 运行成功后，`crontab -l` 命令可以查看已添加的定时任务。

### 运行所有钱包

```sh
python script.py
```

### 运行指定钱包

```sh
python script.py <索引>
```

例如，运行 `config.json` 文件中第一个钱包：

```sh
python script.py 0
```



