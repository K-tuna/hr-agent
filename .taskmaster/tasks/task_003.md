# Task ID: 3

**Title:** LangSmith 트레이싱 및 모니터링 연동

**Status:** pending

**Dependencies:** None

**Priority:** high

**Description:** LangSmith를 연동하여 모든 Agent 호출을 트레이싱하고, 응답 시간 및 에러를 모니터링하는 시스템 구축

**Details:**

## 구현 세부사항

### 1. LangSmith 설정
- LangSmith 계정 생성 (https://smith.langchain.com/)
- API 키 발급 및 환경 변수 설정:
```bash
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_api_key
LANGCHAIN_PROJECT=enterprise-hr-agent
```

### 2. 트레이싱 활성화
- `core/agents/hr_agent.py`에 트레이싱 컨텍스트 추가
- 각 Agent 호출 시 메타데이터 태깅:
  - `agent_type`: SQL_AGENT / RAG_AGENT
  - `user_id`: 사용자 식별자
  - `session_id`: 세션 ID

### 3. 커스텀 로깅
- LangSmith의 `tracing_v2_enabled` 컨텍스트 사용
- 주요 체크포인트:
  - Router 의도 분류 결과
  - SQL 생성 및 실행 시간
  - RAG 검색 시간 및 검색된 문서 수
  - Self-Correction 재시도 횟수

### 4. 에러 트래킹
- 모든 예외를 LangSmith에 자동 로깅
- 스택 트레이스 및 입력 컨텍스트 포함

### 5. 대시보드 구성
- LangSmith UI에서 프로젝트 대시보드 설정
- 주요 메트릭:
  - 평균 응답 시간 (목표: 3초 이내)
  - 에러율 (목표: 5% 이하)
  - Agent 타입별 사용 빈도

### 수용 기준
- 모든 요청이 LangSmith에 트레이싱됨
- 대시보드에서 실시간 메트릭 확인 가능
- 평균 응답 시간 3초 이내

**Test Strategy:**

## 검증 방법

1. **트레이싱 활성화 확인**
```bash
# .env 파일 확인
cat .env | grep LANGCHAIN_TRACING_V2
# 출력: LANGCHAIN_TRACING_V2=true
```

2. **테스트 쿼리 실행**
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"question": "개발팀 평균 급여는?"}'
```

3. **LangSmith UI 확인**
- https://smith.langchain.com/projects 접속
- `enterprise-hr-agent` 프로젝트에서 방금 요청 확인
- Trace 상세 보기:
  - Router 호출 → SQL Agent 호출 → SQL 실행
  - 각 단계별 latency 표시

4. **에러 트래킹 테스트**
- 의도적으로 잘못된 질문 입력
- LangSmith에서 에러 로그 및 스택 트레이스 확인

5. **성능 메트릭 검증**
- 10개 이상 요청 후 대시보드에서 평균 응답 시간 확인
- 3초 이내인지 검증
