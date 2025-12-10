# %%
"""
Step 1.3: Self-Correction (자동 SQL 수정)
목표: SQL 실행 실패 시 에러를 보고 자동으로 수정
"""
print("=" * 70)
print("Step 1.3: Self-Correction")
print("=" * 70)

# %%
# 셀 1: 환경 설정 (exp_01에서 학습한 내용 재사용)
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
load_dotenv()

from core.db_connection import db
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

print("✅ 환경 설정 완료")

# %%
# 셀 2: 기본 설정 (스키마, LLM, Chain) - 0.3.x 방식
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

schema = db.get_table_schema()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# SQL 생성 프롬프트 (ChatPromptTemplate - 0.3.x 권장)
sql_prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 MySQL 데이터베이스 전문가입니다. SQL 쿼리만 생성하세요."),
    ("user", """데이터베이스 스키마:
{schema}

사용자 질문: {question}

규칙:
1. MySQL 문법 사용
2. SELECT 쿼리만 생성
3. 세미콜론(;)으로 끝내기
4. 쿼리만 출력 (설명 금지, 마크다운 코드 블록 금지)

SQL 쿼리:""")
])

# Chain: Prompt → LLM → Parser
sql_chain = sql_prompt | llm | StrOutputParser()

print("✅ 기본 설정 완료 (ChatPromptTemplate + StrOutputParser)")

# %%
# 셀 3: 일부러 실패하는 질문 (테스트)
question_fail = "employee 테이블에서 모든 직원 이름 보여줘"

print(f"\n테스트 질문: {question_fail}")
print("(의도: 'employee' 테이블은 없음, 'employees'가 맞음)")

# StrOutputParser가 자동으로 문자열 변환 + 프롬프트에서 마크다운 금지
sql_v1 = sql_chain.invoke({
    "schema": schema,
    "question": question_fail
}).strip()

print(f"\n생성된 SQL:\n{sql_v1}")

# %%
# 셀 4: SQL 실행 (실패 예상)
print("\n" + "-" * 70)
print("SQL 실행 중...")

results, error = db.execute_query(sql_v1)

if error:
    print(f"\n❌ 예상대로 실패!")
    print(f"에러: {error}")
else:
    print(f"\n✅ 성공 (예상 밖)")
    print(f"결과: {results}")

# %%
# 셀 5: Self-Correction 프롬프트
correction_prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 MySQL 데이터베이스 전문가입니다. SQL 오류를 수정하세요."),
    ("user", """이전에 생성한 SQL에서 오류가 발생했습니다.

데이터베이스 스키마:
{schema}

원래 질문: {question}

생성된 SQL:
{sql}

오류 메시지:
{error}

위 오류를 분석하고, 수정된 SQL을 생성하세요.

규칙:
1. MySQL 문법 사용
2. SELECT 쿼리만
3. 세미콜론(;)으로 끝내기
4. 쿼리만 출력 (설명 금지, 마크다운 금지)

수정된 SQL:""")
])

correction_chain = correction_prompt | llm | StrOutputParser()

print("✅ Self-Correction 프롬프트 준비")

# %%
# 셀 6: SQL 재생성 (Self-Correction)
print("\n" + "=" * 70)
print("Self-Correction 시도")
print("=" * 70)

sql_v2 = correction_chain.invoke({
    "schema": schema,
    "question": question_fail,
    "sql": sql_v1,
    "error": error
}).strip()

print(f"\n수정된 SQL (v2):\n{sql_v2}")

# %%
# 셀 7: 수정된 SQL 실행
print("\n" + "-" * 70)
print("수정된 SQL 실행 중...")

results, error_v2 = db.execute_query(sql_v2)

if error_v2:
    print(f"\n❌ 여전히 실패!")
    print(f"에러: {error_v2}")
else:
    print(f"\n✅ 성공! Self-Correction 작동!")
    print(f"결과 ({len(results)}건):")
    for row in results:
        print(f"  {row}")

# %%
# 셀 8: Self-Correction 루프 (최대 3회)
print("\n" + "=" * 70)
print("Self-Correction 루프 (최대 3회 재시도)")
print("=" * 70)

# 초기 SQL 생성
question = "employee 테이블에서 모든 직원 이름 보여줘"
current_sql = sql_chain.invoke({
    "schema": schema,
    "question": question
}).strip()

print(f"\n[시도 1] 생성된 SQL:\n{current_sql}")

max_attempts = 3
for attempt in range(1, max_attempts + 1):
    # SQL 실행
    results, error = db.execute_query(current_sql)
    
    if not error:
        print(f"\n✅ 성공! (시도 {attempt}회)")
        print(f"결과 ({len(results)}건):")
        for row in results[:5]:  # 최대 5개만 출력
            print(f"  {row}")
        break
    
    # 실패 시
    print(f"\n❌ 시도 {attempt} 실패")
    print(f"에러: {error}")
    
    # 마지막 시도면 종료
    if attempt == max_attempts:
        print(f"\n❌ {max_attempts}회 시도 후 실패!")
        break
    
    # Self-Correction 시도
    print(f"\n[시도 {attempt + 1}] Self-Correction 중...")
    current_sql = correction_chain.invoke({
        "schema": schema,
        "question": question,
        "sql": current_sql,
        "error": error
    }).strip()
    
    print(f"수정된 SQL:\n{current_sql}")