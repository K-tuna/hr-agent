# %%
# 셀 0: 경로 설정 (실험 파일용)
import sys
from pathlib import Path

# 프로젝트 루트를 path에 추가
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

print(f"✅ 프로젝트 루트: {PROJECT_ROOT}")

# %%
# 셀 1: 리팩토링된 코드 테스트 - Import 확인
"""
리팩토링된 HR Agent 테스트
- DI Container 패턴 검증
- 새로운 구조 동작 확인
"""

# 새로운 구조에서 import
from core.types import AgentResult, AgentType
from core.types.errors import HRAgentError, SQLExecutionError
from app.core.config import get_settings

print("✅ Import 성공!")
print(f"Settings: {get_settings().PROJECT_NAME}")

# %%
# 셀 1.5: 환경변수 설정 (로컬 테스트용)
import os
os.environ["DATABASE_URL"] = "mysql+pymysql://user:password@localhost:3306/enterprise_hr_db?charset=utf8mb4"

# %%
# 셀 2: Container 초기화 테스트
"""
DI Container가 제대로 초기화되는지 확인
"""

from core.container import init_container, get_container

settings = get_settings()
print(f"LLM Model: {settings.LLM_MODEL}")
print(f"SQL Max Attempts: {settings.SQL_AGENT_MAX_ATTEMPTS}")
print(f"RAG Top K: {settings.RAG_TOP_K}")

# Container 초기화
container = init_container(settings)
print("✅ Container 초기화 성공!")

# %%
# 셀 3: Router 테스트
"""
Router가 질문을 올바르게 분류하는지 확인
"""

router = container.router

# SQL 질문 테스트
sql_questions = [
    "직원 수는?",
    "개발팀 평균 급여는?",
    "부서별 인원은?",
]

print("=== SQL 질문 테스트 ===")
for q in sql_questions:
    result = router.route(q)
    status = "✅" if result == "SQL_AGENT" else "❌"
    print(f"{status} '{q}' → {result}")

# RAG 질문 테스트
rag_questions = [
    "연차 규정은?",
    "재택근무 정책 알려줘",
    "복지 제도는?",
]

print("\n=== RAG 질문 테스트 ===")
for q in rag_questions:
    result = router.route(q)
    status = "✅" if result == "RAG_AGENT" else "❌"
    print(f"{status} '{q}' → {result}")

# %%
# 셀 4: SQL Agent 테스트
"""
SQL Agent가 자연어를 SQL로 변환하고 실행하는지 확인
(DB 연결 필요)
"""

sql_agent = container.sql_agent

# 간단한 질문 테스트
question = "직원은 총 몇 명인가요?"
print(f"질문: {question}")
print("처리 중...")

result = sql_agent.query(question)

print(f"\n성공: {result['success']}")
print(f"답변: {result['answer']}")
print(f"SQL: {result['metadata'].get('sql', 'N/A')}")
print(f"시도 횟수: {result['metadata'].get('attempts', 'N/A')}")

# %%
# 셀 5: RAG Agent 테스트
"""
RAG Agent가 문서를 검색하고 답변하는지 확인
"""

rag_agent = container.rag_agent

question = "연차 휴가는 며칠인가요?"
print(f"질문: {question}")
print("검색 중...")

result = rag_agent.query(question)

print(f"\n성공: {result['success']}")
print(f"답변: {result['answer']}")
print(f"참조 문서 수: {len(result['metadata'].get('source_docs', []))}")

# %%
# 셀 6: HR Agent 통합 테스트
"""
HRAgent가 Router를 통해 자동으로 적절한 Agent를 선택하는지 확인
"""

hr_agent = container.hr_agent

test_questions = [
    ("직원 수는?", "SQL_AGENT"),
    ("연차 규정 알려줘", "RAG_AGENT"),
    ("개발팀 평균 급여는?", "SQL_AGENT"),
    ("재택근무 정책은?", "RAG_AGENT"),
]

print("=== HR Agent 통합 테스트 ===\n")

for question, expected_agent in test_questions:
    print(f"질문: {question}")
    result = hr_agent.query(question)

    actual_agent = result['metadata'].get('agent_type', 'UNKNOWN')
    status = "✅" if actual_agent == expected_agent else "❌"

    print(f"  {status} Agent: {actual_agent} (예상: {expected_agent})")
    print(f"  답변: {result['answer'][:50]}...")
    print()

# %%
# 셀 7: AgentResult 타입 확인
"""
모든 Agent가 통일된 AgentResult 형식을 반환하는지 확인
"""

print("=== AgentResult 타입 검증 ===\n")

# SQL Agent 결과
sql_result = sql_agent.query("직원 수는?")
print("SQL Agent 결과 키:", list(sql_result.keys()))

# RAG Agent 결과
rag_result = rag_agent.query("연차는?")
print("RAG Agent 결과 키:", list(rag_result.keys()))

# HR Agent 결과
hr_result = hr_agent.query("직원 수는?")
print("HR Agent 결과 키:", list(hr_result.keys()))

# 모두 같은 형식인지 확인
expected_keys = {'success', 'answer', 'metadata', 'error'}
all_match = all(
    set(r.keys()) == expected_keys
    for r in [sql_result, rag_result, hr_result]
)

print(f"\n✅ 모든 Agent가 통일된 AgentResult 반환: {all_match}")

# %%
# 셀 8: 에러 처리 테스트
"""
에러 발생 시 적절히 처리되는지 확인
"""

from core.types.errors import HRAgentError, DatabaseConnectionError

print("=== 에러 타입 테스트 ===\n")

# 에러 생성 테스트
try:
    raise DatabaseConnectionError("테스트 DB 연결 오류")
except HRAgentError as e:
    print(f"✅ 에러 코드: {e.code}")
    print(f"✅ 에러 메시지: {e.message}")
    print(f"✅ HRAgentError 상속 확인")

# %%
# 셀 9: 완료!
"""
리팩토링 검증 완료
"""

print("=" * 50)
print("🎉 리팩토링 검증 완료!")
print("=" * 50)
print("""
✅ 새로운 디렉토리 구조
✅ DI Container 패턴
✅ 통일된 AgentResult 타입
✅ 커스텀 에러 처리
✅ 설정 통합

다음 단계:
1. Docker 빌드 테스트: docker-compose up --build
2. API 테스트: http://localhost:8000/docs
""")
