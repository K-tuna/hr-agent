# %%
"""
Step 1.4: LangGraph로 Self-Correction 구현
목표: StateGraph를 사용한 선언적 플로우
"""
print("=" * 70)
print("Step 1.4: LangGraph SQL Agent")
print("=" * 70)

# %%
# 셀 1: 환경 설정
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
load_dotenv()

from core.db_connection import db
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# LangGraph 임포트
from langgraph.graph import StateGraph, END
from typing import TypedDict

print("✅ 환경 설정 완료 (Python 3.13)")

# %%
# 셀 2: State 정의 (LangGraph의 핵심!)
class SQLAgentState(TypedDict):
    """SQL Agent의 상태를 저장하는 State"""
    question: str             # 사용자 질문
    schema: str               # DB 스키마
    sql: str                  # 현재 SQL
    error: str | None         # 에러 메시지
    results: list | None      # 실행 결과
    attempt: int              # 시도 횟수
    max_attempts: int         # 최대 시도 횟수

print("✅ State 정의 완료")
print("State 필드:")
print("  - question: 사용자 질문")
print("  - schema: DB 스키마")
print("  - sql: 현재 SQL")
print("  - error: 에러 메시지")
print("  - results: 실행 결과")
print("  - attempt: 시도 횟수")
print("  - max_attempts: 최대 시도")

# %%
# 셀 3: generate_sql_node (SQL 생성)
def generate_sql_node(state: SQLAgentState) -> SQLAgentState:
    """Node 1: SQL 생성"""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "MySQL SQL 쿼리만 생성하세요."),
        ("user", """스키마:
{schema}

질문: {question}

규칙:
1. MySQL 문법
2. SELECT 쿼리만
3. 세미콜론(;)으로 끝내기
4. 쿼리만 출력 (설명 금지, 마크다운 금지)

SQL:""")
    ])
    chain = prompt | llm | StrOutputParser()
    sql = chain.invoke({"schema": state["schema"], "question": state["question"]}).strip()
    return {**state, "sql": sql, "attempt": state["attempt"] + 1}

print("✅ generate_sql_node 정의")

# 테스트
state = {"question": "직원 수는?", "schema": db.get_table_schema(), "sql": "", "error": None, "results": None, "attempt": 0, "max_attempts": 3}
result = generate_sql_node(state)
print(f"SQL: {result['sql']}")  # [:50] 제거

# %%
# 셀 4: execute_sql_node (SQL 실행)
def execute_sql_node(state: SQLAgentState) -> SQLAgentState:
    """Node 2: SQL 실행"""
    results, error = db.execute_query(state["sql"])
    if error:
        return {**state, "error": error, "results": None}
    else:
        return {**state, "error": None, "results": results}

print("✅ execute_sql_node 정의")

# 테스트 (성공 케이스)
result["sql"] = "SELECT COUNT(*) FROM employees;"
result2 = execute_sql_node(result)
print(f"결과: {result2['results']}")
print(f"에러: {result2['error']}")

# %%
# 셀 5: correction_node (SQL 수정)
def correction_node(state: SQLAgentState) -> SQLAgentState:
    """Node 3: SQL 수정"""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "MySQL 오류를 수정하세요."),
        ("user", """스키마:
{schema}

질문: {question}
실패한 SQL: {sql}
에러: {error}

수정된 SQL (쿼리만, 마크다운 금지):""")
    ])
    chain = prompt | llm | StrOutputParser()
    corrected_sql = chain.invoke({"schema": state["schema"], "question": state["question"], "sql": state["sql"], "error": state["error"]}).strip()
    return {**state, "sql": corrected_sql, "attempt": state["attempt"] + 1, "error": None}

print("✅ correction_node 정의")

# 테스트 (실패 케이스)
error_state = {**state, "sql": "SELECT * FROM employee;", "error": "Table 'employee' doesn't exist"}
result3 = correction_node(error_state)
print(f"수정된 SQL: {result3['sql']}")

# %%
# 셀 6: should_retry (Conditional Edge - 라우팅)
def should_retry(state: SQLAgentState) -> str:
    """라우팅: 성공 시 end, 실패 시 correction (단, 최대 시도 이내)"""
    if state["error"] is None and state["results"] is not None:
        return "end"
    if state["attempt"] < state["max_attempts"]:
        return "correction"
    return "end"

print("✅ should_retry 정의")

# 테스트
print(f"성공 케이스 → {should_retry(result2)}")  # "end"
print(f"실패 케이스 (재시도 가능) → {should_retry({**error_state, 'attempt': 1})}")  # "correction"
print(f"실패 케이스 (최대 도달) → {should_retry({**error_state, 'attempt': 3})}")  # "end"

# %%
# 셀 7: StateGraph 구성
workflow = StateGraph(SQLAgentState)

# 노드 추가
workflow.add_node("generate_sql", generate_sql_node)
workflow.add_node("execute_sql", execute_sql_node)
workflow.add_node("correction", correction_node)

# 엣지 연결
workflow.set_entry_point("generate_sql")  # 시작점
workflow.add_edge("generate_sql", "execute_sql")  # SQL 생성 → 실행
workflow.add_conditional_edges("execute_sql", should_retry, {
    "correction": "correction",  # 실패 → 수정
    "end": END                    # 성공 → 종료
})
workflow.add_edge("correction", "execute_sql")  # 수정 → 다시 실행

# 컴파일
app = workflow.compile()

print("✅ StateGraph 구성 완료")
print("플로우: generate_sql → execute_sql → [should_retry] → correction or END")

# %%
# 셀 8: 전체 실행 테스트 (Self-Correction 확인)
print("\n" + "=" * 70)
print("LangGraph SQL Agent 실행 테스트")
print("=" * 70)

# 초기 State (의도적으로 틀린 질문 - "employee" 테이블은 없음)
initial_state: SQLAgentState = {
    "question": "employee 테이블에서 모든 직원 이름 보여줘",
    "schema": db.get_table_schema(),
    "sql": "",
    "error": None,
    "results": None,
    "attempt": 0,
    "max_attempts": 3
}

print(f"\n질문: {initial_state['question']}")
print(f"최대 시도: {initial_state['max_attempts']}회\n")

# 그래프 실행
final_state = app.invoke(initial_state)

# 결과 출력
print("\n" + "=" * 70)
if final_state["results"]:
    print(f"✅ 성공! (총 {final_state['attempt']}회 시도)")
    print(f"최종 SQL: {final_state['sql']}")
    print(f"결과 ({len(final_state['results'])}건): {final_state['results'][:3]}")
else:
    print(f"❌ 실패! (총 {final_state['attempt']}회 시도)")
    print(f"최종 SQL: {final_state['sql']}")
    print(f"에러: {final_state['error']}")

# %%
# 셀 9: Self-Correction 강제 테스트 (수동으로 틀린 SQL 주입)
print("\n" + "=" * 70)
print("Self-Correction 강제 테스트 (틀린 SQL 직접 주입)")
print("=" * 70)

# 초기 State: SQL을 일부러 틀리게 설정, attempt=1로 시작
forced_fail_state: SQLAgentState = {
    "question": "모든 직원의 이름과 급여를 보여줘",
    "schema": db.get_table_schema(),
    "sql": "SELECT name, salary FROM employee;",  # ❌ employee (틀림) 
    "error": None,
    "results": None,
    "attempt": 1,  # generate_sql 스킵한 것처럼
    "max_attempts": 3
}

print(f"질문: {forced_fail_state['question']}")
print(f"강제 주입 SQL: {forced_fail_state['sql']}")
print(f"(의도: employee 테이블 없음, employees가 맞음)\n")

# execute_sql부터 시작 (수동 실행)
print("[1] execute_sql 실행...")
state1 = execute_sql_node(forced_fail_state)
print(f"에러: {state1['error']}\n")

print("[2] should_retry 판단...")
next_node = should_retry(state1)
print(f"다음 노드: {next_node}\n")

if next_node == "correction":
    print("[3] correction_node 실행...")
    state2 = correction_node(state1)
    print(f"수정된 SQL: {state2['sql']}\n")
    
    print("[4] 수정된 SQL 재실행...")
    state3 = execute_sql_node(state2)
    print(f"결과: {state3['results'][:2] if state3['results'] else None}")
    print(f"에러: {state3['error']}")
    print(f"\n✅ Self-Correction 성공! (시도: {state3['attempt']}회)")

# %%

