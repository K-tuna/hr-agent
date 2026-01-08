# Task ID: 9

**Title:** Streaming 응답 및 대화 히스토리 구현

**Status:** pending

**Dependencies:** None

**Priority:** medium

**Description:** 실시간 토큰 스트리밍으로 UX 개선 및 ConversationBufferMemory를 활용한 대화 맥락 유지 기능 구현

**Details:**

## 구현 세부사항

### 1. Streaming 응답 (FastAPI)
#### SSE(Server-Sent Events) 엔드포인트 추가
```python
from fastapi.responses import StreamingResponse

@router.post("/query/stream")
async def stream_query(request: QueryRequest):
    async def event_generator():
        async for token in hr_agent.stream(request.question):
            yield f"data: {token}\n\n"
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

#### LangChain astream 활용
```python
from langchain_core.runnables import RunnableConfig

async def stream(self, question: str):
    async for chunk in self.chain.astream(question):
        yield chunk.content
```

### 2. Streamlit UI 통합
#### st.empty()로 실시간 업데이트
```python
import streamlit as st
import requests

def stream_response(question: str):
    placeholder = st.empty()
    response_text = ""
    
    with requests.get(
        f"{API_URL}/query/stream",
        json={"question": question},
        stream=True
    ) as r:
        for line in r.iter_lines():
            if line.startswith(b"data: "):
                token = line[6:].decode('utf-8')
                response_text += token
                placeholder.markdown(response_text + "▌")  # 커서 효과
    
    placeholder.markdown(response_text)  # 최종 결과
```

### 3. 대화 히스토리 구현
#### ConversationBufferMemory 통합
```python
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import MessagesPlaceholder

class HRAgent:
    def __init__(self):
        self.memory = ConversationBufferMemory(
            return_messages=True,
            memory_key="chat_history",
            max_token_limit=2000  # 최대 10턴 정도
        )
    
    def query(self, question: str, session_id: str):
        # 이전 대화 로드
        history = self.memory.load_memory_variables({"session_id": session_id})
        # 질문 처리
        result = self.agent.invoke({"question": question, "chat_history": history})
        # 대화 저장
        self.memory.save_context({"input": question}, {"output": result})
        return result
```

### 4. Multi-turn 대화 지원
#### 대명사 해석 프롬프트
```python
prompt_template = """
이전 대화:
{chat_history}

현재 질문: {question}

이전 대화를 참고하여 "그", "그것", "그 직원" 같은 대명사를 해석하세요.
"""
```

### 5. 세션 관리
- Redis 또는 In-memory dict로 세션별 메모리 관리
- 세션 타임아웃: 30분 비활동 시 삭제

### 수용 기준
- 첫 토큰 1초 이내 출력 시작
- Streamlit에서 타이핑 효과 확인
- 이전 대화 참조 가능 (최소 5턴)

**Test Strategy:**

## 검증 방법

1. **Streaming 응답 테스트 (API)**
```bash
curl -N http://localhost:8000/api/v1/query/stream \
  -H "Content-Type: application/json" \
  -d '{"question": "개발팀 평균 급여는?"}'

# 출력 (실시간):
# data: 개발
# data: 팀
# data: 의
# data:  평균
# ...
```

2. **첫 토큰 지연 시간 측정**
```python
import time

start = time.time()
first_token_time = None

for i, token in enumerate(stream_query("직원 수는?")):
    if i == 0:
        first_token_time = time.time() - start
        break

assert first_token_time < 1.0  # 1초 이내
```

3. **Streamlit UI 테스트**
- 질문 입력 후 즉시 타이핑 시작 확인
- 커서 효과(▌) 표시 확인

4. **대화 히스토리 테스트**
```python
# 1턴
response1 = agent.query("김철수의 급여는?", session_id="test_session")
# 답변: "김철수의 급여는 7,000,000원입니다."

# 2턴 (대명사 사용)
response2 = agent.query("그 직원의 부서는?", session_id="test_session")
# 답변: "개발팀입니다." (김철수를 기억함)

assert "개발" in response2
```

5. **Multi-turn 대화 시나리오**
```
User: 개발팀 직원은 몇 명이야?
Bot: 5명입니다.

User: 그들의 평균 급여는?
Bot: 7,250,000원입니다. ("그들" = 개발팀 직원)

User: 가장 높은 사람은?
Bot: 김철수님으로 8,500,000원입니다.
```
