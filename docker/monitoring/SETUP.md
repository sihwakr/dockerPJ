# 모니터링 설정 가이드

## 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐    ┌─────────────┐  │
│  │ 앱 EC2  │  │ 앱 EC2  │  │ 앱 EC2  │    │ 모니터링 EC2 │  │
│  │   #1    │  │   #2    │  │   #3    │    │             │  │
│  │         │  │         │  │         │    │ Prometheus  │  │
│  │ :9100 ──┼──┼─────────┼──┼─────────┼───▶│ Grafana     │  │
│  │ :8080 ──┼──┼─────────┼──┼─────────┼───▶│ :3000       │  │
│  │         │  │         │  │         │    │ :9090       │  │
│  └─────────┘  └─────────┘  └─────────┘    └─────────────┘  │
│                                                             │
│  Node Exporter: 9100                                        │
│  cAdvisor: 8080                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Step 1: 앱 EC2에 Exporter 배포

각 앱 EC2 (Swarm 노드)에서 실행:

```bash
# Exporter 스택 배포
docker stack deploy -c docker-compose.exporters.yml exporters
```

확인:
```bash
# Node Exporter
curl http://localhost:9100/metrics

# cAdvisor
curl http://localhost:8080/metrics
```

---

## Step 2: 보안 그룹 설정

### 앱 EC2 보안 그룹
| 포트 | 소스 | 설명 |
|------|------|------|
| 9100 | 모니터링 EC2 IP | Node Exporter |
| 8080 | 모니터링 EC2 IP | cAdvisor |
| 9323 | 모니터링 EC2 IP | Docker metrics |

### 모니터링 EC2 보안 그룹
| 포트 | 소스 | 설명 |
|------|------|------|
| 3000 | 내 IP | Grafana 접속 |
| 9090 | 내 IP | Prometheus 접속 |

---

## Step 3: prometheus.yml 수정

`monitoring/prometheus.yml` 파일에서 IP 변경:

```yaml
# 아래 IP를 실제 EC2 Private IP로 변경
- targets:
  - 'SWARM_EC2_1_IP:9100'    # → '10.0.1.10:9100'
  - 'SWARM_EC2_2_IP:9100'    # → '10.0.1.11:9100'
  - 'SWARM_EC2_3_IP:9100'    # → '10.0.1.12:9100'
```

---

## Step 4: 모니터링 EC2에서 실행

```bash
cd monitoring
docker-compose up -d
```

---

## Step 5: 접속

| 서비스 | URL | 계정 |
|--------|-----|------|
| Grafana | http://모니터링EC2:3000 | admin / admin123 |
| Prometheus | http://모니터링EC2:9090 | - |

---

## Step 6: Grafana 대시보드 추가

1. Grafana 로그인
2. 좌측 메뉴 → Dashboards → Import
3. 추천 대시보드 ID 입력:
   - **1860**: Node Exporter Full
   - **893**: Docker and system monitoring
   - **14282**: cAdvisor

---

## 수집되는 메트릭

### Node Exporter (EC2 호스트)
- CPU 사용률
- 메모리 사용량
- 디스크 I/O
- 네트워크 트래픽

### cAdvisor (컨테이너)
- 컨테이너별 CPU
- 컨테이너별 메모리
- 컨테이너 네트워크
- 컨테이너 재시작 횟수

---

## 부하 테스트 시 확인할 것

| 메트릭 | 의미 | 비교 포인트 |
|--------|------|-------------|
| container_cpu_usage_seconds_total | 컨테이너 CPU | Swarm vs ECS |
| container_memory_usage_bytes | 컨테이너 메모리 | Swarm vs ECS |
| node_cpu_seconds_total | 호스트 CPU | 오버헤드 비교 |
| container_last_seen | 컨테이너 생존 | 장애 복구 속도 |
