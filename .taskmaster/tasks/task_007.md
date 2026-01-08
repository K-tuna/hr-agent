# Task ID: 7

**Title:** Hybrid Search (BM25 + FAISS) 구현

**Status:** pending

**Dependencies:** None

**Priority:** medium

**Description:** BM25 키워드 검색과 FAISS 벡터 검색을 결합한 Hybrid Search 시스템으로 RAG 검색 품질 향상

**Details:**

## 구현 세부사항

### 1. BM25 검색 구현
- `rank_bm25` 라이브러리 설치: `pip install rank-bm25`
- 문서 전처리:
  - 한국어 형태소 분석 (선택): `konlpy.tag.Okt` 또는 간단한 공백 토큰화
  - 불용어 제거 (조사, 접속사 등)

```python
from rank_bm25 import BM25Okapi

class BM25Retriever:
    def __init__(self, documents: List[str]):
        tokenized_docs = [doc.split() for doc in documents]
        self.bm25 = BM25Okapi(tokenized_docs)
    
    def search(self, query: str, top_k: int = 3) -> List[Document]:
        tokenized_query = query.split()
        scores = self.bm25.get_scores(tokenized_query)
        # 상위 top_k 문서 반환
```

### 2. Hybrid Retriever 구성
- `core/agents/rag_agent.py`에 하이브리드 검색 추가
- 앙상블 전략:
  - BM25 점수와 FAISS 유사도를 정규화 (0-1)
  - 가중 합산: `final_score = α * bm25_score + (1-α) * faiss_score`
  - 기본 가중치: `α = 0.5` (동등 비중)

### 3. LangChain EnsembleRetriever 활용
```python
from langchain.retrievers import EnsembleRetriever

bm25_retriever = BM25Retriever.from_documents(documents)
faiss_retriever = FAISS.from_documents(documents, embeddings).as_retriever()

hybrid_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, faiss_retriever],
    weights=[0.5, 0.5]
)
```

### 4. 가중치 튜닝
- `core/config.py`에 설정 추가:
  - `BM25_WEIGHT = 0.5`
  - `FAISS_WEIGHT = 0.5`
- 실험을 통해 최적 가중치 탐색 (Grid Search)

### 5. 성능 비교
- RAGAS 평가로 단순 FAISS vs Hybrid Search 비교
- Context Precision 지표 10% 이상 향상 목표

### 수용 기준
- Hybrid Search 정상 동작
- RAGAS Context Precision 10% 향상
- 설정 파일로 가중치 조절 가능

**Test Strategy:**

## 검증 방법

1. **기본 동작 테스트**
```python
from core.agents.rag_agent import RAGAgent

agent = RAGAgent(use_hybrid_search=True)
result = agent.search("연차 규정")

# BM25와 FAISS 점수 모두 사용했는지 확인
assert 'bm25_score' in result.metadata
assert 'faiss_score' in result.metadata
```

2. **키워드 중심 질문 테스트**
- 질문: "육아휴직 기간" (명확한 키워드)
- BM25가 높은 가중치로 정확한 문서 검색 예상

3. **의미 기반 질문 테스트**
- 질문: "아이를 돌보기 위한 휴가 제도" (동의어 사용)
- FAISS가 높은 가중치로 관련 문서 검색 예상

4. **RAGAS 평가 비교**
```bash
# FAISS only
python scripts/evaluate_rag.py --mode=faiss
# Context Precision: 0.75

# Hybrid
python scripts/evaluate_rag.py --mode=hybrid
# Context Precision: 0.85 (10% 향상)
```

5. **가중치 실험**
```python
for alpha in [0.3, 0.5, 0.7]:
    set_config(BM25_WEIGHT=alpha)
    run_evaluation()
# 최적 가중치 식별
```
