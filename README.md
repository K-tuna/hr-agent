<div align="center">

# 🤖 Enterprise HR AI Agent

**자연어로 질문하면 자동으로 SQL 실행하거나 사규 검색해드립니다**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3.27-1C3C3C?style=flat)](https://www.langchain.com/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)

![demo](assets/demo.gif)

<details>
   <summary>이전 버전</summary>
      <img width="1918" height="909" alt="image" src="https://github.com/user-attachments/assets/68e35916-5ef4-411c-bb34-4da47bfb8413" />
</details>

</div>

---

## 🚀 Quick Start

```bash
# 1. 클론
git clone https://github.com/K-tuna/enterprise-hr-agent.git
cd enterprise-hr-agent

# 2. Ollama 설치 및 모델 다운로드
# https://ollama.com 에서 설치 후:
ollama pull qwen3:8b

# 3. 환경변수 설정 (Ollama 기본값)
echo "OLLAMA_HOST=http://localhost:11434" > .env

# 4. 실행 (Docker)
docker-compose up -d

# 5. 접속
# API: http://localhost:8000/docs
# UI:  http://localhost:8501
```

---

## 🛤️ 개발 과정

| Phase | 작업 | 상세 |
|-------|------|------|
| 1 | 환경 구축 | Docker Compose (3개 서비스), MySQL 8.0 |
| 2 | SQL Agent | 자연어→SQL, Self-Correction 자동 재시도 |
| 3 | RAG Agent | 55,000자 PDF → 110+ 청크, FAISS Top-3 검색 |
| 4 | Router | LLM Few-shot 의도 분류, LangGraph 통합 |
| 5 | API | FastAPI 3-tier, Swagger 자동 문서화 |
| 6 | UI | Streamlit 채팅, Agent 타입 실시간 표시 |
| 7 | 리팩토링 | DI Container 패턴, 모듈 구조화 |

📝 [트러블슈팅 10건 해결](docs/troubleshooting/README.md)

---

## 🎯 핵심 차별점

### 1. **Self-Correction SQL Agent** ⚡
잘못된 SQL이 생성되어도 에러 메시지를 분석해 **자동으로 3번까지 재시도**
```
❌ 1차 시도: SELECT * FROM employee WHERE dept = 'Sales'
   → Error: Table 'employee' doesn't exist

✅ 2차 시도: SELECT * FROM employees WHERE dept_id = (SELECT dept_id FROM departments WHERE name = 'Sales')
   → Success!
```

### 2. **Router 기반 Multi-Agent** 🔀
질문 의도를 LLM이 자동 분석하여 **적절한 Agent로 분기**
- "직원 수는?" → SQL Agent
- "연차 규정은?" → RAG Agent
- Few-shot 프롬프트로 정확한 의도 분류

### 3. **100% 로컬 LLM** 🏠
API 비용 없이 **완전 오프라인** 실행 가능
- **Ollama + Qwen3:8B**: 로컬 추론
- **QLoRA 파인튜닝**: HR 도메인 특화 (qwen3-hr)
- **sentence-transformers**: 로컬 임베딩

### 4. **현업 표준 아키텍처** 🏗️
- **LangGraph StateGraph**: 복잡한 플로우 선언적 구현
- **FastAPI 3-tier**: API/Service/Model 분리 (15개 파일)
- **FAISS 벡터 검색**: Meta의 고성능 라이브러리
- **Docker Compose**: 원클릭 실행 환경

---

## 🏛️ 아키텍처

```
┌──────────┐      ┌───────────────┐      ┌─────────────────────────────────┐
│   User   │ ───▶ │  Streamlit UI │ ───▶ │         FastAPI Server          │
└──────────┘      └───────────────┘      │                                 │
                                         │  ┌───────────────────────────┐  │
                                         │  │   HRAgent (LangGraph)     │  │
                                         │  │                           │  │
                                         │  │   ┌───────────────────┐   │  │
                                         │  │   │  Router (LLM)     │   │  │
                                         │  │   │  "SQL or RAG?"    │   │  │
                                         │  │   └─────────┬─────────┘   │  │
                                         │  │             │             │  │
                                         │  │       ┌─────┴─────┐       │  │
                                         │  │       ▼           ▼       │  │
                                         │  │  ┌────────┐  ┌────────┐   │  │
                                         │  │  │  SQL   │  │  RAG   │   │  │
                                         │  │  │ Agent  │  │ Agent  │   │  │
                                         │  │  └────┬───┘  └────┬───┘   │  │
                                         │  └───────┼───────────┼───────┘  │
                                         └──────────┼───────────┼──────────┘
                                                    │           │
                                                    ▼           ▼
                                               ┌────────┐  ┌────────┐
                                               │ MySQL  │  │ FAISS  │
                                               │   DB   │  │ Index  │
                                               └────────┘  └────────┘
```

---

## 🛠️ 기술 스택

| 카테고리 | 기술 | 선택 이유 |
|---------|------|----------|
| **LLM Framework** | LangChain 0.3.27 | LTS 지원 (2026.12까지), LCEL 스타일 |
| **Graph Engine** | LangGraph 0.2.60 | Self-Correction 루프 구현 필수 |
| **LLM** | Ollama + Qwen3:8B | 100% 로컬, API 비용 제로, 온프레미스 |
| **Fine-tuned** | qwen3-hr (QLoRA) | HR 도메인 특화 모델 |
| **Embedding** | sentence-transformers | 로컬 실행, 한글 지원 |
| **Vector DB** | FAISS | 무료, 로컬 실행, 빠름 |
| **Web Framework** | FastAPI | Async, 자동 문서화, 현업 표준 |
| **Frontend** | Streamlit | 빠른 프로토타이핑, Python only |
| **Database** | MySQL 8.0 | HR 시스템 업계 표준 |
| **Infra** | Docker Compose | 개발/배포 환경 일치 |

---

## 📡 API 엔드포인트

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/` | API 정보 |
| GET | `/api/v1/health` | 헬스 체크 |
| POST | `/api/v1/query` | HR 질의 처리 (핵심!) |
| GET | `/docs` | Swagger UI |
| GET | `/redoc` | ReDoc 문서 |

### POST /api/v1/query

**Request:**
```json
{
  "question": "개발팀 평균 급여는?"
}
```

**Response:**
```json
{
  "question": "개발팀 평균 급여는?",
  "answer": "7,250,000원",
  "agent_type": "SQL_AGENT",
  "success": true,
  "error": null
}
```

---

## 🎬 데모

### 📊 SQL Agent (Self-Correction)

**질문:** "영업팀 평균 급여 알려줘"

```
[1차 시도 실패]
SQL: SELECT AVG(salary) FROM employee WHERE dept = 'Sales'
Error: Table 'employee' doesn't exist

[2차 시도 성공] ✅
SQL: SELECT AVG(s.base_salary) 
     FROM salaries s 
     JOIN employees e ON s.emp_id = e.emp_id 
     JOIN departments d ON e.dept_id = d.dept_id 
     WHERE d.name = 'Sales'
     
Result: 6,500,000원
```

### 📚 RAG Agent (FAISS 검색)

**질문:** "육아휴직은 몇 개월까지 가능해?"

```
[FAISS 검색]
Top 3 유사 문서 검색 → 규정 2.4 "출산/육아휴직" 발견

[LLM 답변 생성]
"육아휴직은 최대 1년(12개월)까지 가능하며, 
통상임금의 80%가 지급됩니다."

[참조 문서]
- 회사규정.pdf, 2.4절
```

### 🔀 Router (자동 분기)

| 질문 | 분류 결과 |
|------|----------|
| "김철수 연봉은?" | SQL_AGENT ✅ |
| "재택근무 규정은?" | RAG_AGENT ✅ |
| "부서별 직원 수는?" | SQL_AGENT ✅ |
| "복지 제도 알려줘" | RAG_AGENT ✅ |

Few-shot 프롬프트로 정확한 의도 분류

---

## 📁 프로젝트 구조

<details>
<summary>펼쳐보기</summary>

```
enterprise-hr-agent/
├── app/                          # FastAPI (3-tier 아키텍처)
│   ├── main.py
│   ├── core/                    # 설정 & 의존성
│   ├── models/                  # Pydantic 모델
│   ├── services/                # 비즈니스 로직
│   └── api/v1/endpoints/        # REST 엔드포인트
│
├── core/                         # Agent 핵심 로직
│   ├── agents/
│   │   ├── hr_agent.py          # 통합 Agent (LangGraph)
│   │   ├── sql_agent.py         # SQL Agent + Self-Correction
│   │   └── rag_agent.py         # RAG Agent (FAISS)
│   ├── database/
│   │   └── connection.py        # DB 연결 + 스키마 조회
│   ├── routing/
│   │   └── router.py            # 질문 의도 분류 (Few-shot)
│   ├── types/                   # 타입 정의
│   └── container.py             # DI Container
│
├── frontend/
│   └── app.py                   # Streamlit 채팅 UI
│
├── data/
│   ├── db_init/init.sql         # MySQL 스키마 + 더미 데이터 (15명)
│   ├── company_docs/            # 사규 문서 (PDF)
│   └── faiss_index/             # FAISS 벡터 인덱스
│
├── docker-compose.yml           # MySQL + API + Streamlit
├── Dockerfile
└── requirements.txt
```

</details>

---

## 🔬 기술적 하이라이트

### 1. Self-Correction with LangGraph
```python
# 전통적인 방법 (단순 루프)
for attempt in range(3):
    sql = generate_sql(question)
    result, error = execute_sql(sql)
    if not error:
        break

# LangGraph 방식 (선언적)
workflow.add_conditional_edges(
    "execute",
    check_error,
    {
        "retry": "generate",  # 에러 시 재생성
        "end": END            # 성공 시 종료
    }
)
```

### 2. LCEL 스타일 (LangChain 0.3.x)
```python
# 체인 구성
chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt 
    | llm 
    | StrOutputParser()
)

# 실행
result = chain.invoke("연차는 몇일?")
```

### 3. Few-shot 프롬프트 (Router)
```python
template = """
<분류 예시>
질문: "직원은 총 몇 명인가요?" → SQL_AGENT
질문: "연차 규정 알려줘" → RAG_AGENT
질문: "개발팀 평균 급여는?" → SQL_AGENT
...

질문: {question}
분류:"""
```

### 4. RAG 파라미터 설정

#### 최적 파라미터 (RAGAS 평가 기준)

| 파라미터 | 설정값 | 근거 |
|---------|-------|------|
| **chunk_size** | 1,000자 | RAGAS Context Precision 0.70 (500자 대비 +0.15) |
| **chunk_overlap** | 200자 (20%) | 문맥 연결, LangChain 권장값 |
| **top_k** | 5 | Context Recall 1.0 달성 |
| **temperature** | 0 | 정확성 우선, RAG 표준 |

#### RAGAS 평가 결과

| 설정 | Context Precision | Context Recall | 평균 |
|-----|-------------------|----------------|-----|
| **1000/200, k=5** | 0.702 | 1.000 | **0.851** |
| 1000/200, k=3 | 0.692 | 0.900 | 0.796 |
| 500/50, k=5 | 0.553 | 1.000 | 0.776 |
| 500/50, k=3 | 0.558 | 0.800 | 0.679 |

> **RAGAS**: LLM 기반 RAG 평가 프레임워크. 키워드 매칭보다 의미적 관련성을 정확히 평가.

#### 파라미터 영향도

| 순위 | 파라미터 | 영향 | 설명 |
|-----|---------|-----|------|
| 1 | chunk_size | 높음 | 맥락 충분성에 가장 큰 영향 |
| 2 | chunk_overlap | 높음 | 문맥 손실 방지 |
| 3 | top_k | 중간 | Recall에 직접 영향 |
| 4 | temperature | 낮음 | RAG는 0 고정이 표준 |

#### 참고 자료
- [LangChain RAG Tutorial](https://python.langchain.com/docs/tutorials/rag/) - chunk_size=1000, overlap=200
- [RAGAS Documentation](https://docs.ragas.io/) - RAG 평가 프레임워크

---


## 🎯 핵심 기능 상세

### SQL Agent
- ✅ 자연어 → SQL 자동 생성
- ✅ 스키마 자동 인식
- ✅ Self-Correction (최대 3회)
- ✅ 복잡한 JOIN/GROUP BY 지원
- ✅ 에러 메시지 기반 수정

### RAG Agent
- ✅ PDF 문서 로드 (PDFPlumber)
- ✅ RecursiveCharacterTextSplitter (chunk_size=1000, overlap=200)
- ✅ 로컬 임베딩 (snowflake-arctic-embed2)
- ✅ FAISS 벡터 검색 (Top-K=5)
- ✅ RAGAS 기반 파라미터 최적화
- ✅ 참조 문서 출처 제공

### Router
- ✅ LLM 기반 의도 분류
- ✅ Few-shot 프롬프트 (8개 예시)
- ✅ 안전한 폴백 (불확실 시 RAG)

---

## 🗺️ Roadmap

| Version | Focus | Key Features |
|---------|-------|--------------|
| **v1.0** ✅ | 기본 완성 | SQL Agent, RAG Agent, Router |
| **v1.5** ✅ | 로컬 LLM | OpenAI → Ollama/Qwen3 전환, 파인튜닝 (qwen3-hr) |
| **v2.0** 🚧 | 2025 현업 표준 | SQL: Few-shot, SQLCoder / RAG: Reranker, Hybrid Search |
| v2.1 | 모니터링 | LangSmith 트레이싱, RAGAS 평가 |
| v2.2 | 보안 | PII 마스킹, SQL Validation |

👉 [Phase 2 상세](docs/phase2/phase2_prd.md)

