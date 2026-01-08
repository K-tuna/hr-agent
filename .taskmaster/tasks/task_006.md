# Task ID: 6

**Title:** Human-in-the-loop 승인 플로우 구현

**Status:** pending

**Dependencies:** 5

**Priority:** medium

**Description:** 위험도 높은 쿼리나 확신도 낮은 응답에 대한 사용자 승인 대기 메커니즘 구축

**Details:**

## 구현 세부사항

### 1. 위험도 점수 계산
- SQL 복잡도 점수 (0-100):
  - 서브쿼리 포함: +30점
  - 3개 이상 테이블 JOIN: +20점
  - 집계 함수 사용: +10점
- 확신도 점수 (LLM logprobs 활용):
  - OpenAI API `logprobs=True` 설정
  - 평균 확률 < 0.7 시 낮은 확신도로 판정

### 2. 승인 필요 조건
- 위험도 점수 >= 60점
- 확신도 점수 < 0.7
- 사용자 정의 규칙 (config 파일)

### 3. 승인 대기 상태 구현
- Redis 또는 In-memory 큐에 요청 저장
- 상태: `PENDING_APPROVAL` → `APPROVED` / `REJECTED`
- 타임아웃: 5분 (자동 거부)

### 4. API 엔드포인트 추가
- `POST /api/v1/approvals/{request_id}/approve`: 승인
- `POST /api/v1/approvals/{request_id}/reject`: 거부
- `GET /api/v1/approvals/pending`: 대기 중인 요청 목록

### 5. Streamlit UI 통합
- 승인 대기 메시지 표시
```python
if response['status'] == 'pending_approval':
    st.warning("⚠️ 위험도 높은 쿼리입니다. 승인이 필요합니다.")
    if st.button("승인"):
        approve_request(response['request_id'])
```

### 6. 알림 (선택)
- 이메일 또는 Slack 웹훅으로 승인 요청 알림

### 수용 기준
- 위험 쿼리 실행 전 100% 사용자 확인
- 승인/거부 플로우 정상 동작
- UI에서 승인 버튼 표시

**Test Strategy:**

## 검증 방법

1. **위험 쿼리 테스트**
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -d '{"question": "모든 부서의 직원 수와 평균 급여를 서브쿼리로 계산해줘"}'
```

예상 응답:
```json
{
  "status": "pending_approval",
  "request_id": "req_12345",
  "message": "위험도 높은 쿼리입니다. 승인이 필요합니다.",
  "risk_score": 70,
  "confidence": 0.65
}
```

2. **승인 프로세스 테스트**
```bash
# 대기 중인 요청 확인
curl http://localhost:8000/api/v1/approvals/pending

# 승인
curl -X POST http://localhost:8000/api/v1/approvals/req_12345/approve
```

3. **UI 테스트**
- Streamlit에서 위험 쿼리 입력
- 승인 버튼 표시 확인
- 승인 후 결과 출력 확인

4. **타임아웃 테스트**
- 승인 요청 후 5분 대기
- 자동 거부 확인
