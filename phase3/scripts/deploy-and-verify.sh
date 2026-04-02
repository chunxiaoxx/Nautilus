#!/bin/bash
# Nautilus deployment script with health verification and retry logic
# Usage: bash scripts/deploy-and-verify.sh
set -e

SERVER="cloud"
BACKEND_DIR="~/nautilus-mvp/phase3/backend"
TIMEOUT=15
MAX_RETRIES=3
RETRY_DELAY=5

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info()    { echo -e "[INFO] $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn()    { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $1"; }

# Retry wrapper: retry_cmd <max_retries> <delay> <description> <command...>
retry_cmd() {
    local max_retries=$1
    local delay=$2
    local desc=$3
    shift 3

    local attempt=1
    while [ $attempt -le $max_retries ]; do
        if "$@" 2>&1; then
            return 0
        fi
        if [ $attempt -lt $max_retries ]; then
            log_warn "$desc failed (attempt $attempt/$max_retries), retrying in ${delay}s..."
            sleep $delay
        fi
        attempt=$((attempt + 1))
    done

    log_error "$desc failed after $max_retries attempts"
    return 1
}

# File transfer: prefer rsync, fall back to scp
transfer_files() {
    local src=$1
    local dest=$2

    if command -v rsync &>/dev/null; then
        log_info "Using rsync for file transfer..."
        rsync -avz --checksum --timeout=30 -e ssh "$src" "$SERVER:$dest"
    else
        log_info "Using scp for file transfer (rsync not available)..."
        scp -r "$src" "$SERVER:$dest"
    fi
}

# Verify file integrity after transfer
verify_transfer() {
    local local_path=$1
    local remote_path=$2

    if [ -d "$local_path" ]; then
        local local_count=$(find "$local_path" -type f | wc -l)
        local remote_count=$(ssh "$SERVER" "find $remote_path -type f 2>/dev/null | wc -l")
        if [ "$local_count" != "$remote_count" ]; then
            log_error "File count mismatch: local=$local_count remote=$remote_count"
            return 1
        fi
        log_success "File count verified: $local_count files"
    else
        local local_size=$(stat -f%z "$local_path" 2>/dev/null || stat -c%s "$local_path" 2>/dev/null || echo "0")
        local remote_size=$(ssh "$SERVER" "stat -c%s $remote_path 2>/dev/null || echo 0")
        if [ "$local_size" != "$remote_size" ]; then
            log_error "File size mismatch: local=${local_size}B remote=${remote_size}B"
            return 1
        fi
        log_success "File size verified: ${local_size}B"
    fi
    return 0
}

echo "=== Nautilus Deployment ==="
echo ""

# 1. Push to cloud-server
echo "[1/6] Pushing to cloud-server..."
retry_cmd $MAX_RETRIES $RETRY_DELAY "git push" git push cloud-server master || {
    log_warn "Push rejected or failed, trying to update remote working directory directly..."
}

# 2. Update server working directory
echo ""
echo "[2/6] Updating server working directory..."
retry_cmd $MAX_RETRIES $RETRY_DELAY "git reset on server" \
    ssh $SERVER "cd ~/nautilus-mvp && git fetch origin 2>/dev/null; git reset --hard HEAD"

# 3. Sync agent-engine to backend/agent_engine
echo ""
echo "[3/6] Syncing agent-engine to backend/agent_engine..."
retry_cmd $MAX_RETRIES $RETRY_DELAY "agent-engine sync" \
    ssh $SERVER "cd ~/nautilus-mvp && bash phase3/scripts/sync-agent-engine.sh"

# 4. Restart backend
echo ""
echo "[4/6] Restarting backend..."
ssh $SERVER "sudo systemctl restart nautilus-backend"

# 5. Wait and verify
echo ""
echo "[5/6] Waiting ${TIMEOUT}s for startup..."
sleep $TIMEOUT

echo ""
echo "[6/6] Running health checks..."

HEALTH_OK=true

# Check /api/stats
STATS=$(ssh $SERVER "curl -s -w '\n%{http_code}' http://localhost:8000/api/stats" 2>/dev/null)
STATS_CODE=$(echo "$STATS" | tail -1)
STATS_BODY=$(echo "$STATS" | sed '$d')

if [ "$STATS_CODE" = "200" ]; then
    log_success "/api/stats: OK"
else
    log_error "/api/stats: FAILED (HTTP ${STATS_CODE})"
    HEALTH_OK=false
fi

# Check /health
HEALTH=$(ssh $SERVER "curl -s -w '\n%{http_code}' http://localhost:8000/health" 2>/dev/null)
HEALTH_CODE=$(echo "$HEALTH" | tail -1)
HEALTH_BODY=$(echo "$HEALTH" | sed '$d')

if [ "$HEALTH_CODE" = "200" ]; then
    STATUS=$(echo "$HEALTH_BODY" | python3 -c "import sys,json;print(json.load(sys.stdin).get('status','unknown'))" 2>/dev/null || echo "unknown")
    log_success "/health: OK (status: ${STATUS})"
else
    log_warn "/health: HTTP ${HEALTH_CODE} (non-critical)"
fi

# Check survival API
SURV_CODE=$(ssh $SERVER "curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/api/survival/statistics" 2>/dev/null)
if [ "$SURV_CODE" = "200" ]; then
    log_success "/api/survival/statistics: OK"
else
    log_warn "/api/survival/statistics: HTTP ${SURV_CODE}"
fi

# Check academic API
ACAD_CODE=$(ssh $SERVER "curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/api/academic/" 2>/dev/null)
if [ "$ACAD_CODE" = "200" ]; then
    log_success "/api/academic/: OK"
else
    log_warn "/api/academic/: HTTP ${ACAD_CODE}"
fi

echo ""
if [ "$HEALTH_OK" = true ]; then
    log_success "=== Deployment Complete ==="
else
    log_error "=== Deployment had issues - check logs ==="
    echo ""
    echo "Recent backend logs:"
    ssh $SERVER "journalctl -u nautilus-backend -n 15 --no-pager" 2>/dev/null
    exit 1
fi
