# 🏢 Enterprise HR Agent

> 자연어로 HR 데이터 분석(SQL)과 사규 검색(RAG)을 처리하는 AI 에이전트

## ✨ 주요 기능

| 기능 | 설명 |
|---|---|
| **SQL Agent** | 자연어 → SQL 생성 → 실행 → Self-Correction (최대 3회) |
| **RAG Agent** | PDF 사규 문서 검색 (FAISS) |
| **Router** | 질문 의도 파악 후 Agent 자동 분기 |

## 🛠 기술 스택

| 구분 | 기술 |
|---|---|
| Language | Python 3.11+ |
| LLM | OpenAI `gpt-4o-mini` |
| Framework | LangGraph, LangChain 0.3.27, FastAPI |
| Vector Search | FAISS |
| Database | MySQL 8.0 |
| Infra | Docker Compose |

## 🚀 Quick Start

```bash
# 1. 환경 변수 설정
cp .env.example .env
# .env 파일에 OPENAI_API_KEY 입력

# 2. Docker 실행
docker compose up -d

# 3. 패키지 설치
pip install -r requirements.txt

# 4. 서버 실행
uvicorn api.main:app --reload
```

## 📁 프로젝트 구조

```
enterprise-hr-agent/
├── api/
│   └── main.py           # FastAPI 서버
├── core/
│   ├── sql_agent.py      # SQL Agent + Self-Correction
│   ├── rag_agent.py      # RAG Agent (FAISS)
│   ├── router.py         # 의도 분류
│   └── graph.py          # LangGraph 메인 그래프
├── db/
│   └── init/
│       └── init.sql      # HR 스키마 + 더미 데이터
├── data/
│   └── company_rules.pdf # 사규 문서
├── docs/
│   └── PLANNING.md       # 기획서
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 📖 API 사용법

```bash
# 질문하기
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "개발팀에서 연봉이 가장 높은 직원은?"}'
```

## 🎯 시연 예시

### SQL Agent
```
Q: "개발팀에서 연봉이 가장 높은 직원은?"
A: "개발팀에서 연봉이 가장 높은 직원은 김철수이며, 기본급은 800만원입니다."
```

### RAG Agent
```
Q: "연차 사용 규정이 뭐야?"
A: "사규에 따르면, 1년 이상 근속한 직원에게 15일의 연차휴가가 부여됩니다."
```

## 📋 향후 개선 사항

- [ ] Human-in-the-loop (위험 쿼리 승인)
- [ ] SSE 스트리밍 응답
- [ ] Kafka 연동
- [ ] Vespa/Qdrant 전환
- [ ] 배포 (Railway/Render)

## 📄 License

MIT


