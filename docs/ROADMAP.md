# 프로젝트 로드맵

---

## v1.0 ✅ (현재)

### SQL Agent
- Text-to-SQL (자연어 → SQL 자동 생성)
- Self-Correction (에러 시 최대 3회 재시도)
- 스키마 자동 인식 + ENUM 값 매핑
- LLM 기반 자연어 답변 포맷팅

### RAG Agent
- PDF 문서 로드 (PDFPlumber)
- 청킹 (500자, overlap 50자)
- FAISS 벡터 검색 (Top-K=3)
- 컨텍스트 기반 답변 생성

### Router
- LLM Few-shot 의도 분류
- SQL/RAG 자동 분기
- 에러 시 RAG 폴백

### Infra
- FastAPI 3-tier 구조
- Streamlit 채팅 UI
- Docker Compose (MySQL + API + Streamlit)
- 빈 문자열 입력 검증

### LLM Provider 추상화
- LLM Factory 패턴 (`core/llm/factory.py`)
- OpenAI ↔ Ollama 환경변수 기반 전환
- Ollama qwen3:8b 기본 지원
- FAISS 인덱스 임베딩 모델 연동 (snowflake-arctic-embed2)

---

## v1.1 - RAG 고도화
- Hybrid Search (BM25 키워드 + Vector 의미 결합)
- Re-ranking (Cross-encoder로 검색 결과 재정렬)
- Query Rewriting (LLM으로 질문을 검색 최적화 형태로 변환)
- Metadata Filtering (부서/날짜 등 사전 필터링)

## v1.2 - SQL 고도화
- Query Caching (해시 기반 중복 쿼리 캐싱)
- Query Validation (SQL 파싱 + SELECT만 허용 + 위험 키워드 차단)
- Query Decomposition (복잡한 질문을 여러 쿼리로 분해)
- Schema Linking (질문과 관련된 테이블만 컨텍스트에 포함)

## v1.3 - Router 고도화
- Rule-based 1차 (키워드 매칭으로 빠른 분류)
- Confidence 체크 (확신도 낮으면 사용자에게 재질문)
- Multi-Agent (3개 이상 Agent 확장 구조)

## v1.4 - UX 개선
- Streaming (SSE로 ChatGPT처럼 실시간 응답)
- 대화 히스토리 (ConversationBufferMemory)
- Multi-turn (이전 대화 컨텍스트 참조)

## v1.5 - 평가/모니터링
- RAGAS (RAG 평가: Faithfulness, Relevancy, Context Precision)
- SQL 평가 (Execution Accuracy 측정)
- LangSmith (트레이싱 + 디버깅)

---

## v2.0 - 고급 RAG
- Agentic RAG (검색 결과를 Agent가 자체 평가)
- Self-RAG (필요할 때만 검색 수행)
- CRAG (Corrective RAG - 검색 실패 시 웹 검색 등 대체)
- Graph RAG (지식 그래프 + 벡터 검색 결합)

## v2.1 - 고급 SQL
- SQLCoder (Text-to-SQL 전용 Fine-tuned 모델)
- Semantic Layer (dbt/Cube.js 연동)

## v2.2 - LLM 다양화
- ~~Local LLM (Ollama)~~ → v1.0에서 완료
- Model Router (질문 복잡도에 따라 모델 선택)
- Fallback Chain (모델 실패 시 대체 모델)

## v3.0 - 엔터프라이즈
- Fine-tuning (도메인 특화 모델 학습)
- Human-in-the-loop (위험 쿼리 승인 플로우)
- Guardrails (입출력 필터링)

---

## 트러블슈팅

`docs/troubleshooting/README.md` 참고
