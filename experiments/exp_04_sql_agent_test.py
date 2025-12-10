# %%
"""
Step 2: SQL Agent 테스트 (리팩토링 완료 후)
목표: core/sql_agent.py를 import해서 실제로 사용해보기
"""
print("=" * 70)
print("Step 2: SQL Agent 테스트 (Production Code)")
print("=" * 70)

# %%
# 셀 1: 환경 설정
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.sql_agent import SQLAgent

print("✅ SQLAgent import 완료")

# %%
# 셀 2: SQLAgent 인스턴스 생성
agent = SQLAgent(model="gpt-4o-mini", max_attempts=3)

print("✅ SQLAgent 인스턴스 생성 완료")
print(f"  - 모델: gpt-4o-mini")
print(f"  - 최대 시도: 3회")

# %%
# 셀 3: 간단한 질문 테스트
print("\n테스트 1: 간단한 COUNT 쿼리")
print("-" * 70)

question1 = "직원 수는?"
result1 = agent.query(question1)

print(f"질문: {question1}")
print(f"성공: {result1['success']}")
print(f"SQL: {result1['sql']}")
print(f"결과: {result1['results']}")
print(f"시도: {result1['attempts']}회")

# %%
# 셀 4: 복잡한 질문 테스트 (JOIN + GROUP BY)
print("\n테스트 2: 복잡한 집계 쿼리")
print("-" * 70)

question2 = "각 부서별 평균 급여를 보여줘"
result2 = agent.query(question2)

print(f"질문: {question2}")
print(f"성공: {result2['success']}")
print(f"SQL:\n{result2['sql']}")
print(f"\n결과:")
for row in result2['results']:
    print(f"  {row}")
print(f"시도: {result2['attempts']}회")

# %%
# 셀 5: Self-Correction 확인 (일부러 틀린 질문)
print("\n테스트 3: Self-Correction 테스트")
print("-" * 70)

# 존재하지 않는 컬럼 요청
question3 = "모든 직원의 phone_number를 보여줘"
result3 = agent.query(question3)

print(f"질문: {question3}")
print(f"(의도: phone_number 컬럼은 존재하지 않음)")
print(f"성공: {result3['success']}")
print(f"SQL: {result3['sql']}")
if result3['success']:
    print(f"결과: {result3['results'][:3]}")
else:
    print(f"에러: {result3['error']}")
print(f"시도: {result3['attempts']}회")
print(f"\n분석: {'Self-Correction 작동!' if result3['attempts'] > 1 else 'LLM이 처음부터 올바르게 생성'}")

# %%
# 셀 6: 여러 질문 연속 테스트
print("\n테스트 4: 여러 질문 연속 실행")
print("=" * 70)

questions = [
    "가장 높은 급여를 받는 직원은?",
    "IT 부서 직원 수는?",
    "2023년 이후 입사한 직원들의 이름을 보여줘",
    "평균 급여보다 많이 받는 직원 수는?"
]

for i, q in enumerate(questions, 1):
    print(f"\n[{i}] 질문: {q}")
    result = agent.query(q)
    print(f"    성공: {'✅' if result['success'] else '❌'}")
    print(f"    SQL: {result['sql'][:60]}...")
    if result['success'] and result['results']:
        print(f"    결과: {result['results'][0] if len(result['results']) == 1 else f'{len(result['results'])}건'}")
    print(f"    시도: {result['attempts']}회")

print("\n" + "=" * 70)
print("✅ 모든 테스트 완료!")

# %%
# 셀 7: 마무리 및 사용법 정리
print("\n" + "=" * 70)
print("SQL Agent 사용법 정리")
print("=" * 70)

print("""
✅ SQL Agent 완성!

📦 Import:
    from core.sql_agent import SQLAgent

🚀 사용법:
    agent = SQLAgent(model="gpt-4o-mini", max_attempts=3)
    result = agent.query("직원 수는?")
    
📊 반환값:
    {
        "success": True/False,     # 성공 여부
        "sql": "SELECT ...",        # 생성된 SQL
        "results": [...],           # 실행 결과
        "error": None/"...",        # 에러 메시지
        "attempts": 1               # 시도 횟수
    }

⚡ 특징:
    - Self-Correction (최대 3회)
    - LangGraph 기반 선언적 플로우
    - 복잡한 JOIN/GROUP BY 자동 생성
    
🎯 다음 단계: FastAPI 통합!
""")

# %%


