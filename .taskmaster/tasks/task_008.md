# Task ID: 8

**Title:** Re-ranking 및 Query Rewriting 구현

**Status:** pending

**Dependencies:** 7

**Priority:** medium

**Description:** Cross-encoder 기반 검색 결과 재정렬과 LLM 기반 쿼리 재작성으로 RAG 품질 극대화

**Details:**

## 구현 세부사항

### 1. Re-ranking 구현
#### Cross-encoder 모델 선택
- `sentence-transformers/cross-encoder/ms-marco-MiniLM-L-6-v2` (다국어 지원)
- 또는 한국어 특화: `jhgan/ko-sroberta-multitask`

#### Re-ranker 클래스 구현
```python
from sentence_transformers import CrossEncoder

class ReRanker:
    def __init__(self):
        self.model = CrossEncoder('sentence-transformers/ms-marco-MiniLM-L-6-v2')
    
    def rerank(self, query: str, documents: List[Document], top_k: int = 3) -> List[Document]:
        pairs = [(query, doc.page_content) for doc in documents]
        scores = self.model.predict(pairs)
        # 점수 순으로 정렬하여 상위 top_k 반환
        sorted_docs = [doc for _, doc in sorted(zip(scores, documents), reverse=True)]
        return sorted_docs[:top_k]
```

#### 통합 플로우
1. Hybrid Search로 Top-10 검색
2. Re-ranker로 Top-3 재정렬
3. 최종 3개 문서를 LLM에 전달

### 2. Query Rewriting 구현
#### LLM 기반 쿼리 변환
```python
rewrite_prompt = """
사용자 질문을 검색에 최적화된 형태로 변환하세요.
- 오타 교정
- 핵심 키워드 추출
- 동의어 추가

원본 질문: {question}
최적화된 질문:
"""
```

#### 적용 전략
- 모호한 질문: "그거 알려줘" → "육아휴직 규정 알려줘"
- 오타 교정: "연차 규정은 뭐야?" → "연차 규정"
- 확장: "연차" → "연차, 휴가, 연휴"

### 3. RAG Agent 통합
- `core/agents/rag_agent.py`에서 파이프라인 수정:
  1. Query Rewriting (선택적)
  2. Hybrid Search (Top-10)
  3. Re-ranking (Top-3)
  4. LLM 답변 생성

### 4. 성능 측정
- RAGAS Answer Relevancy 향상 목표
- 검색 시간 vs 정확도 트레이드오프 분석

### 수용 기준
- Re-ranking으로 검색 품질 향상 (RAGAS 점수 +0.05)
- Query Rewriting으로 모호한 질문 처리 성공
- 전체 응답 시간 5초 이내 유지

**Test Strategy:**

## 검증 방법

1. **Re-ranking 테스트**
```python
from core.agents.rag_agent import RAGAgent

agent = RAGAgent(use_reranking=True)

# Hybrid Search 결과
hybrid_docs = agent.hybrid_search("육아휴직", top_k=10)
print([doc.metadata['score'] for doc in hybrid_docs])
# [0.82, 0.78, 0.75, 0.70, ...] (내림차순 아닐 수 있음)

# Re-ranking 결과
reranked_docs = agent.rerank("육아휴직", hybrid_docs, top_k=3)
print([doc.metadata['rerank_score'] for doc in reranked_docs])
# [0.95, 0.91, 0.88] (더 정확한 순서)
```

2. **Query Rewriting 테스트**
```python
from core.agents.rag_agent import rewrite_query

test_cases = [
    ("연차는 몇일?", "연차 일수"),
    ("아이 휴가", "육아휴직 규정"),
    ("재택 가능?", "재택근무 규정")
]

for original, expected_keyword in test_cases:
    rewritten = rewrite_query(original)
    assert expected_keyword in rewritten.lower()
```

3. **RAGAS 평가 비교**
```bash
# Before Re-ranking
python scripts/evaluate_rag.py --mode=hybrid
# Answer Relevancy: 0.78

# After Re-ranking
python scripts/evaluate_rag.py --mode=hybrid_rerank
# Answer Relevancy: 0.83 (향상)
```

4. **응답 시간 측정**
```python
import time

start = time.time()
result = agent.query("육아휴직 기간")
latency = time.time() - start

assert latency < 5.0  # 5초 이내
```

5. **모호한 질문 처리**
- 입력: "그 휴가 규정"
- Query Rewriting: "휴가 규정" (대명사 해석)
- 정상 답변 생성 확인
