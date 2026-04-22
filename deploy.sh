#!/bin/bash
set -e

# ====== 配置 ======
SERVER="root@你的服务器IP"
REMOTE_DIR="$HOME/veil"
# ==================

echo "[1/2] 同步代码到服务器..."
rsync -avz --exclude '.git' --exclude 'node_modules' --exclude '.venv' --exclude '__pycache__' --exclude '.env' \
  ./ "$SERVER:${REMOTE_DIR}/"

echo "[2/2] 远程构建并启动..."
ssh "$SERVER" "
  cd ${REMOTE_DIR}
  docker compose up -d --build
  docker image prune -f
"

echo "完成！"
