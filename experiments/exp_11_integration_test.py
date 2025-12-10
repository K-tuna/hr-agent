# %%
# 셀 1: 환경 설정 및 HRAgent 임포트

import os
import sys
from dotenv import load_dotenv

# 프로젝트 루트를 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.graph import HRAgent

# 환경 변수 로드
load_dotenv()

print("✅ 모듈 임포트 완료")

# %%
# 셀 2: HRAgent 인스턴스 생성

agent = HRAgent(model="gpt-4o-mini", verbose=True)

print("✅ HRAgent 생성 완료")
print("   - Router 초기화됨")
print("   - SQL Agent 초기화됨")
print("   - RAG Agent 초기화됨")
print("   - LangGraph 구성 완료")

# %%
# 셀 3: SQL 질문 테스트 #1

question = "직원은 총 몇 명인가요?"

print(f"\n{'='*70}")
print(f"질문: {question}")
print(f"{'='*70}\n")

result = agent.query(question)

print(f"\n{'='*70}")
print(f"Agent 타입: {result['agent_type']}")
print(f"성공 여부: {result['success']}")
print(f"\n최종 답변:")
print(result['final_answer'])
print(f"{'='*70}\n")

# %%
# 셀 4: SQL 질문 테스트 #2

question = "개발팀 직원 명단 알려줘"

print(f"\n{'='*70}")
print(f"질문: {question}")
print(f"{'='*70}\n")

result = agent.query(question)

print(f"\n{'='*70}")
print(f"Agent 타입: {result['agent_type']}")
print(f"성공 여부: {result['success']}")
print(f"\n최종 답변:")
print(result['final_answer'])
print(f"{'='*70}\n")

# %%
# 셀 5: SQL 질문 테스트 #3

question = "평균 급여는 얼마인가요?"

print(f"\n{'='*70}")
print(f"질문: {question}")
print(f"{'='*70}\n")

result = agent.query(question)

print(f"\n{'='*70}")
print(f"Agent 타입: {result['agent_type']}")
print(f"성공 여부: {result['success']}")
print(f"\n최종 답변:")
print(result['final_answer'])
print(f"{'='*70}\n")

# %%
# 셀 6: RAG 질문 테스트 #1

question = "연차는 몇일인가요?"

print(f"\n{'='*70}")
print(f"질문: {question}")
print(f"{'='*70}\n")

result = agent.query(question)

print(f"\n{'='*70}")
print(f"Agent 타입: {result['agent_type']}")
print(f"성공 여부: {result['success']}")
print(f"\n최종 답변:")
print(result['final_answer'])
print(f"{'='*70}\n")

# %%
# 셀 7: RAG 질문 테스트 #2

question = "재택근무 가능한가요?"

print(f"\n{'='*70}")
print(f"질문: {question}")
print(f"{'='*70}\n")

result = agent.query(question)

print(f"\n{'='*70}")
print(f"Agent 타입: {result['agent_type']}")
print(f"성공 여부: {result['success']}")
print(f"\n최종 답변:")
print(result['final_answer'])
print(f"{'='*70}\n")

# %%
# 셀 8: RAG 질문 테스트 #3

question = "복지 제도 알려줘"

print(f"\n{'='*70}")
print(f"질문: {question}")
print(f"{'='*70}\n")

result = agent.query(question)

print(f"\n{'='*70}")
print(f"Agent 타입: {result['agent_type']}")
print(f"성공 여부: {result['success']}")
print(f"\n최종 답변:")
print(result['final_answer'])
print(f"{'='*70}\n")

# %%
# 셀 9: 혼합 질문 일괄 테스트

test_cases = [
    # (질문, 예상 Agent 타입)
    ("직원 중에 연봉이 가장 높은 사람은?", "SQL_AGENT"),
    ("휴가 규정 알려줘", "RAG_AGENT"),
    ("부서별 직원 수는?", "SQL_AGENT"),
    ("야근 수당은 어떻게 되나요?", "RAG_AGENT"),
    ("김철수 급여 알려줘", "SQL_AGENT"),
    ("육아휴직 규정은?", "RAG_AGENT"),
]

print(f"\n{'='*70}")
print("통합 테스트 - 다양한 질문")
print(f"{'='*70}\n")

results = []
for question, expected_agent in test_cases:
    result = agent.query(question)
    is_correct = result["agent_type"] == expected_agent
    
    results.append({
        "question": question,
        "expected": expected_agent,
        "actual": result["agent_type"],
        "correct": is_correct,
        "success": result["success"]
    })
    
    status = "✅" if is_correct else "❌"
    print(f"{status} {question}")
    print(f"   예상: {expected_agent} | 실제: {result['agent_type']}")
    print(f"   성공: {result['success']}")
    print()

# 정확도 계산
correct_routing = sum(1 for r in results if r["correct"])
total = len(results)
routing_accuracy = (correct_routing / total) * 100

successful_queries = sum(1 for r in results if r["success"])
success_rate = (successful_queries / total) * 100

print(f"\n{'='*70}")
print(f"테스트 결과 요약:")
print(f"   라우팅 정확도: {correct_routing}/{total} = {routing_accuracy:.1f}%")
print(f"   쿼리 성공률: {successful_queries}/{total} = {success_rate:.1f}%")
print(f"{'='*70}\n")

print("✅ 통합 테스트 완료!")

# %%
# 셀 10: 간단한 사용 예제 (비 verbose 모드)

print("\n=== 비 verbose 모드로 간단한 사용 ===\n")

# verbose=False로 생성
simple_agent = HRAgent(verbose=False)

# 여러 질문 연속 처리
questions = [
    "직원 수는?",
    "연차 규정은?",
    "평균 급여는?"
]

for q in questions:
    result = simple_agent.query(q)
    print(f"Q: {q}")
    print(f"A: {result['final_answer']}\n")

print("✅ 모든 통합 테스트 완료!")
print("✅ Phase 4 완료 - Router + 통합 성공!")

# %%

