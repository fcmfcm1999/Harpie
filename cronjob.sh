#!/bin/bash

JSON_FILE="$(dirname "$0")/config.json"

if [ ! -f "$JSON_FILE" ]; then
    echo "Error: config file not found!"
    exit 1
fi

# 获取系统时区偏移（以小时为单位）
LOCAL_OFFSET=$(date +%:::z)
BJ_OFFSET=8  # 北京时间 UTC+8
TIME_DIFF=$((BJ_OFFSET - LOCAL_OFFSET))

# 解析 JSON 并提取 runTime
JOBS=$(jq -c '.wallets[]' "$JSON_FILE")

# 清除现有的相关 cron 任务
crontab -l | grep -v "python3 /root/Harpie/main.py" | crontab -

# 遍历 JSON 数据
NEW_CRON=""
INDEX=0
while IFS= read -r job; do
    RUNTIME=$(echo "$job" | jq -r '.runTime')
    MINUTE=$(echo "$RUNTIME" | cut -d":" -f2)
    HOUR=$(echo "$RUNTIME" | cut -d":" -f1)

    # 计算本地时区的执行时间
    HOUR=$(( (HOUR - TIME_DIFF + 24) % 24 ))

    NEW_CRON+="$MINUTE $HOUR * * * python3 /root/Harpie/main.py $INDEX >> /root/Harpie/output.log 2>&1 &\n"
    ((INDEX++))
done <<< "$JOBS"

# 将新的 cron 任务添加到 crontab
(crontab -l; echo -e "$NEW_CRON") | crontab -

echo "Crontab updated successfully!"
