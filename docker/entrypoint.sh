#!/bin/bash

# Docker Secrets를 환경변수로 변환
# Secrets는 /run/secrets/ 폴더에 파일로 마운트됨

if [ -f /run/secrets/db_url ]; then
    export DATABASE_URL=$(cat /run/secrets/db_url)
fi

# 전달받은 명령어 실행 (CMD)
exec "$@"
