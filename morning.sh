#!/bin/bash

# Morning - 주식 분석 시스템 관리 스크립트 (루트 디렉토리)
# scripts 폴더의 관리 스크립트를 실행합니다.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$SCRIPT_DIR/scripts"

# scripts 폴더의 morning.sh 실행
if [ -f "$SCRIPTS_DIR/morning.sh" ]; then
    "$SCRIPTS_DIR/morning.sh" "$@"
else
    echo "❌ 스크립트 파일을 찾을 수 없습니다: $SCRIPTS_DIR/morning.sh"
    exit 1
fi
