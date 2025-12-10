# %%
"""
Step 1.2: Text-to-SQL 생성 (Interactive)
각 셀을 Shift+Enter로 하나씩 실행하세요!
"""
print("=" * 70)
print("Step 1.2: Text-to-SQL Interactive")
print("=" * 70)

# %%
# 셀 1: 환경 설정
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
load_dotenv()

print("✅ 환경 설정 완료")

# %%
# 셀 2: DB 스키마 가져오기
from core.db_connection import db

schema = db.get_table_schema()
print("📊 DB 스키마:")
print(schema)

# %%
# 셀 3: LLM 생성
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)

print("✅ LLM 생성 완료")
print(f"모델: gpt-4o-mini")

# %%
# 셀 4: 간단한 LLM 테스트
response = llm.invoke("안녕하세요!")
print(f"응답: {response.content}")

# %%
# 셀 5: ChatPromptTemplate 생성 (0.3.x 권장 방식)
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_messages([
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

print("✅ ChatPromptTemplate 생성 완료 (0.3.x)")
print(f"입력 변수: {prompt.input_variables}")

# %%
# 셀 6: Chain 생성 (Prompt → LLM → Parser)
chain = prompt | llm | StrOutputParser()

print("✅ Chain 생성 완료 (with StrOutputParser)")
print("이제 질문 → SQL 변환이 가능합니다!")

# %%
# 셀 7: 첫 번째 SQL 생성 테스트
question1 = "개발팀 직원 수는?"

print(f"\n질문: {question1}")
print("-" * 70)

# StrOutputParser가 자동으로 문자열 반환
sql_raw = chain.invoke({
    "schema": schema,
    "question": question1
})

sql = sql_raw.strip()
print(f"생성된 SQL:\n{sql}")

# %%
# 셀 8: 두 번째 테스트
question2 = "김철수의 연봉은?"

print(f"\n질문: {question2}")
print("-" * 70)

sql_raw = chain.invoke({
    "schema": schema,
    "question": question2
})

sql = sql_raw.strip()
print(f"생성된 SQL:\n{sql}")

# %%
# 셀 9: 세 번째 테스트
question3 = "부서별 평균 급여를 알려줘"

print(f"\n질문: {question3}")
print("-" * 70)

sql_raw = chain.invoke({
    "schema": schema,
    "question": question3
})

sql = sql_raw.strip()
print(f"생성된 SQL:\n{sql}")

# %%
print("\n" + "=" * 70)
print("✅ Step 1.2 완료!")
print("=" * 70)

# %%
# 셀 10: SQL 실행해보기
print(f"실행할 SQL:\n{sql}\n")

# DB에서 실행
results, error = db.execute_query(sql)

if error:
    print(f"❌ SQL 실행 실패:")
    print(f"에러: {error}")
else:
    print(f"✅ SQL 실행 성공!")
    print(f"결과 ({len(results)}건):")
    for row in results:
        print(f"  {row}")
# %%
