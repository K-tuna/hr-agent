# Project: Enterprise HR Agent

지금부터 너는 **3년 차 같은 신입 백엔드 엔지니어**의 파트너 AI야.
우리는 16시간 안에 **HR 도메인 AI Agent 포트폴리오**를 완성해야 해.

⚠️ 시간이 16시간밖에 없어. 불필요한 기능은 과감히 버리고 **핵심만** 구현해.

아래 내용을 완벽히 숙지하고 개발을 시작해 줘.

---

## 1. [Tech Spec] 인수인계 명세서

**"자연어로 HR 데이터 분석(SQL)과 사규 검색(RAG)을 처리하는 AI 에이전트"**

### Tech Stack
- **Language:** Python 3.11+
- **LLM:** OpenAI `gpt-4o-mini`
- **Framework:** `langgraph==0.2.60`, `langchain==0.3.27`, `fastapi==0.115.6`
- **Vector Search:** FAISS (`faiss-cpu==1.9.0.post1`)
- **Database:** MySQL 8.0 (`pymysql`, `sqlalchemy`)
- **Infra:** Docker Compose

### 기술 선택 근거
- **LangChain 0.3.27:** 0.x 최종 안정 버전, 2026.12까지 LTS 지원
- **LangGraph:** Self-Correction 루프 구현에 필수 (Chain은 직선형만 가능)
- **FAISS:** 현업 활용도 2위 (Meta), 고성능 벡터 검색, Vespa/Qdrant 전환 가능
- **MySQL:** 플렉스 실제 스택, 엔터프라이즈 HR 시스템 표준

### Key Features (3개만)
1. **SQL Agent:** 자연어 → SQL 생성 → 실행 → **실패 시 Self-Correction (최대 3회)**
2. **RAG Agent:** PDF 사규 검색 (FAISS)
3. **Router:** 질문 의도 파악 후 Agent 분기

### Current Status
- `docker compose up -d`로 MySQL(Port 3306) 실행 완료
- `db/init/init.sql` (HR 테이블) 적용 완료

### 파일 구조
- `docker-compose.yml`
- `requirements.txt`
- `README.md`
- `db/init/init.sql`
- `core/sql_agent.py` — SQL Agent + Self-Correction
- `core/rag_agent.py` — RAG Agent (FAISS)
- `core/router.py` — 의도 분류
- `core/graph.py` — LangGraph 메인 그래프
- `api/main.py` — FastAPI 서버
- `data/company_rules.pdf` — 샘플 사규

### DB 연결
`mysql+pymysql://user:password@localhost:3306/enterprise_hr_db`

---

## 2. [Feature Examples] 기능 예시

### 예시 1: SQL Agent (정상 케이스)
```
User: "개발팀에서 연봉이 가장 높은 직원은?"

[SQL 생성]
SELECT e.name, s.base_salary 
FROM employees e 
JOIN salaries s ON e.emp_id = s.emp_id 
JOIN departments d ON e.dept_id = d.dept_id 
WHERE d.name = 'Engineering' 
ORDER BY s.base_salary DESC LIMIT 1;

[응답]
"개발팀에서 연봉이 가장 높은 직원은 김철수이며, 기본급은 800만원입니다."
```

### 예시 2: SQL Agent (Self-Correction)
```
User: "영업팀 평균 급여 알려줘"

[1차 SQL 생성] - 테이블명 오류
SELECT AVG(salary) FROM employee WHERE dept = 'Sales';

[실행 실패]
Error: Table 'employee' doesn't exist

[자동 수정 - 스키마 참조]
SELECT AVG(s.base_salary) FROM salaries s 
JOIN employees e ON s.emp_id = e.emp_id 
JOIN departments d ON e.dept_id = d.dept_id 
WHERE d.name = 'Sales';

[2차 실행 성공]
```

### 예시 3: RAG Agent
```
User: "연차 사용 규정이 뭐야?"
→ [FAISS 검색] → "사규에 따르면, 1년 이상 근속한 직원에게 15일의 연차휴가가 부여됩니다."
```

### 예시 4: Router
```
"김철수 연봉 알려줘" → SQL Agent
"휴가 규정 알려줘" → RAG Agent
```

---

## 3. [Strategy] 포트폴리오 어필 포인트

### A. Text-to-SQL 역량
- 자연어 질의 → SQL 생성 → 실행
- **Self-Correction:** 오류 발생 시 에러 메시지 기반 자동 수정 (최대 3회)

### B. Multi-Agent 역량
- **Router 기반 분기:** 질문 의도에 따라 SQL Agent / RAG Agent 선택
- LangGraph StateGraph로 **확장 가능한 구조** 설계

### C. RAG 역량
- PDF 문서 임베딩 → FAISS 저장
- 유사도 검색 기반 답변 생성

---

## 4. [Constraints] 제약 사항

### ✅ 구현할 것
- SQL Agent + Self-Correction (최대 3회)
- RAG Agent (FAISS)
- Router (의도 분기)
- FastAPI 기본 엔드포인트 (`/query`, `/health`)
- **시연 영상 (GIF/영상)** — README에 삽입

### ❌ 버릴 것 (시간 부족)
- Human-in-the-loop
- Kafka 연동
- SSE 스트리밍
- EXPLAIN 분석
- Feedback Loop

### ⏳ 시간 되면
- Railway/Render 배포 (SQLite 전환)

---

## 5. [Timeline] 16시간 개발 일정

| 시간 | 작업 | 산출물 |
|---|---|---|
| 0-2h | 환경 세팅 | Docker, DB, 프로젝트 구조 |
| 2-6h | SQL Agent | `core/sql_agent.py` |
| 6-9h | RAG Agent | `core/rag_agent.py` |
| 9-11h | Router + 통합 | `core/router.py`, `core/graph.py` |
| 11-14h | FastAPI 서버 | `api/main.py` |
| 14-15h | 테스트 + 시연 영상 | GIF/영상 촬영 |
| 15-16h | README 작성 | 문서화 |
| (여유 시) | 배포 | Railway/Render |

---

## 6. [Action] 작업 규칙

- 설명은 짧게, **실행 가능한 코드 위주**로 작성해.
- 내가 요청하면 해당 파일 전체 코드를 바로 작성해줘.
- 불필요한 기능 추가하지 마. 시간 없어.

---

이제 시작하자. 첫 번째로 `core/sql_agent.py`부터 작성해줘.

