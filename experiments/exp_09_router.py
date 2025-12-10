# %%
# 셀 1: 환경 설정 및 OpenAI 연결 테스트

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# 환경 변수 로드
load_dotenv()

# OpenAI API 키 확인
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("❌ OPENAI_API_KEY not found in environment")

print(f"✅ OpenAI API Key loaded: {api_key[:10]}...")

# LLM 초기화
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 간단한 테스트
response = llm.invoke("Hello!")
print(f"✅ LLM 연결 성공")
print(f"응답: {response.content}")

# %%
# 셀 2: 의도 분류 프롬프트 설계

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 의도 분류 프롬프트 (현업 스타일 - Few-shot 예시 포함)
classification_template = """당신은 HR 시스템의 질문 분류 전문가입니다.
사용자의 질문을 분석하여 적절한 Agent로 라우팅하세요.

<분류 기준>
1. SQL_AGENT: 직원 데이터, 통계, 급여, 부서 정보 등 **데이터베이스 조회**가 필요한 질문
2. RAG_AGENT: 회사 규정, 정책, 제도, 복지 등 **문서 검색**이 필요한 질문

<분류 예시>
질문: "직원은 총 몇 명인가요?" → SQL_AGENT
질문: "연차 규정 알려줘" → RAG_AGENT
질문: "개발팀 평균 급여는?" → SQL_AGENT
질문: "재택근무 가능한가요?" → RAG_AGENT
질문: "부서별 직원 수는?" → SQL_AGENT
질문: "복지 제도 알려줘" → RAG_AGENT
질문: "김철수 연봉은?" → SQL_AGENT
질문: "휴가 신청 방법은?" → RAG_AGENT

<중요 지시사항>
- 반드시 "SQL_AGENT" 또는 "RAG_AGENT" 중 정확히 하나만 출력하세요.
- 설명, 이유, 추가 텍스트 절대 금지!
- 불확실하면 RAG_AGENT를 선택하세요.

질문: {question}

분류:"""

prompt = ChatPromptTemplate.from_template(classification_template)

# 분류 체인 (LCEL)
classification_chain = prompt | llm | StrOutputParser()

print("✅ 분류 프롬프트 및 체인 생성 완료")

# %%
# 셀 3: 분류 테스트 (SQL 질문들)

sql_questions = [
    "직원은 총 몇 명인가요?",
    "개발팀 직원 명단 알려줘",
    "평균 급여는 얼마인가요?",
    "김철수 연봉 알려줘",
    "부서별 직원 수는?"
]

print("=== SQL Agent로 분류되어야 하는 질문들 ===\n")
for q in sql_questions:
    result = classification_chain.invoke({"question": q})
    print(f"질문: {q}")
    print(f"분류: {result.strip()}")
    print()

# %%
# 셀 4: 분류 테스트 (RAG 질문들)

rag_questions = [
    "연차는 몇 일인가요?",
    "재택근무 가능한가요?",
    "복지 제도 알려줘",
    "휴가 신청 방법은?",
    "회사 규정 중 근무시간은?"
]

print("=== RAG Agent로 분류되어야 하는 질문들 ===\n")
for q in rag_questions:
    result = classification_chain.invoke({"question": q})
    print(f"질문: {q}")
    print(f"분류: {result.strip()}")
    print()

# %%
# 셀 5: Router 함수 구현

def route_question(question: str) -> str:
    """
    질문을 분석하여 적절한 Agent로 라우팅
    
    Args:
        question: 사용자 질문
        
    Returns:
        "SQL_AGENT" 또는 "RAG_AGENT"
    """
    result = classification_chain.invoke({"question": question})
    agent_type = result.strip()
    
    # 검증
    if agent_type not in ["SQL_AGENT", "RAG_AGENT"]:
        # 기본값: RAG_AGENT (안전한 선택)
        print(f"⚠️ 예상치 못한 분류 결과: {agent_type}, RAG_AGENT로 기본 설정")
        return "RAG_AGENT"
    
    return agent_type

# 테스트
test_cases = [
    "직원 수는?",
    "연차 규정 알려줘",
    "평균 급여는?",
    "복지 제도는?"
]

print("=== Router 함수 테스트 ===\n")
for question in test_cases:
    agent = route_question(question)
    print(f"질문: {question}")
    print(f"→ {agent}")
    print()

print("✅ Router 함수 구현 완료")

# %%
# 셀 6: 혼합 질문 테스트

mixed_questions = [
    ("직원 중에 연봉 1억 이상은?", "SQL_AGENT"),
    ("연차 몇일까지 이월 가능해?", "RAG_AGENT"),
    ("부서별 평균 연령은?", "SQL_AGENT"),
    ("육아휴직 규정은?", "RAG_AGENT"),
    ("최근 입사한 직원은?", "SQL_AGENT"),
    ("야근 수당 정책은?", "RAG_AGENT"),
]

print("=== 혼합 질문 분류 정확도 테스트 ===\n")

correct = 0
total = len(mixed_questions)

for question, expected in mixed_questions:
    result = route_question(question)
    is_correct = result == expected
    correct += is_correct
    
    print(f"질문: {question}")
    print(f"예상: {expected} | 결과: {result} {'✅' if is_correct else '❌'}")
    print()

accuracy = (correct / total) * 100
print(f"정확도: {correct}/{total} = {accuracy:.1f}%")
print("✅ Router 실험 완료!")

# %%

