# Ollama 전환 시 FAISS 임베딩 차원 불일치

## 문제
- Streamlit 채팅에서 RAG 질문 시 응답 없음 (무한 로딩)
- SQL 질문은 정상 작동, RAG 질문만 실패
- 에러 메시지가 빈 문자열로 나와서 원인 파악 어려움

## 원인
FAISS 인덱스가 OpenAI 임베딩(1536차원)으로 생성되어 있는데, Ollama 임베딩(1024차원)으로 검색 시도하여 차원 불일치 발생

```
AssertionError: d == self.d
File "faiss/class_wrappers.py", line 329, in replacement_search
    assert d == self.d
```

- OpenAI `text-embedding-3-small`: 1536차원
- Ollama `snowflake-arctic-embed2`: 1024차원

## 해결 과정

### 시도 1: 에러 메시지 추적
- 파일: RAG Agent query() 메서드
- 결과: `str(e)`가 빈 문자열로 나옴
- 원인: FAISS 내부에서 AssertionError 발생

### 시도 2: 단계별 디버깅
```python
# 1. 임베딩 생성 - 성공
embeddings = create_embeddings(provider='ollama', model='snowflake-arctic-embed2')

# 2. FAISS 로드 - 성공 (차원 검증 안 함)
vectorstore = FAISS.load_local(index_path, embeddings)

# 3. 검색 - 실패! (여기서 차원 불일치)
docs = retriever.invoke('연차휴가')
```

### 시도 3: 인덱스 재생성 (성공)
- 파일: `scripts/build_index.py`
- 명령: `python scripts/build_index.py`
- 결과: Ollama 임베딩(1024차원)으로 인덱스 재생성

```bash
$ python scripts/build_index.py
Provider: ollama
Embedding: snowflake-arctic-embed2
벡터 차원: 1024
인덱스 저장 완료: data/faiss_index
```

## 검증
```python
from core.container import init_container
container = init_container(settings)

# RAG 테스트
result = container.rag_agent.query('연차휴가는 며칠?')
print(result['success'])  # True
print(result['metadata']['agent_type'])  # RAG_AGENT
```

## 변경된 파일
- `data/faiss_index/` - Ollama 임베딩으로 재생성

## 관련 설정 (.env)
```
LLM_PROVIDER=ollama
OLLAMA_MODEL=qwen3:8b
OLLAMA_EMBEDDING_MODEL=snowflake-arctic-embed2
OLLAMA_BASE_URL=http://localhost:11434
```
