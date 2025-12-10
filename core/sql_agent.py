"""
SQL Agent: 자연어 질문을 SQL로 변환하고 실행
Self-Correction 기능 포함 (LangGraph 기반)
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from typing import TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END

from core.db_connection import db


class SQLAgentState(TypedDict):
    """SQL Agent의 상태"""
    question: str
    schema: str
    sql: str
    error: str | None
    results: list | None
    attempt: int
    max_attempts: int


class SQLAgent:
    """
    SQL Agent 클래스
    - 자연어 질문 → SQL 생성 → 실행
    - Self-Correction (최대 3회)
    """
    
    def __init__(self, model: str = "gpt-4o-mini", max_attempts: int = 3):
        """
        Args:
            model: 사용할 OpenAI 모델
            max_attempts: 최대 재시도 횟수
        """
        self.llm = ChatOpenAI(model=model, temperature=0)
        self.max_attempts = max_attempts
        self.schema = db.get_table_schema()
        self.app = self._build_workflow()
    
    def query(self, question: str) -> dict:
        """
        자연어 질문을 받아 SQL 실행 결과 반환
        
        Args:
            question: 사용자 질문
            
        Returns:
            {
                "success": bool,
                "sql": str,
                "results": list | None,
                "error": str | None,
                "attempts": int
            }
        """
        initial_state: SQLAgentState = {
            "question": question,
            "schema": self.schema,
            "sql": "",
            "error": None,
            "results": None,
            "attempt": 0,
            "max_attempts": self.max_attempts
        }
        
        final_state = self.app.invoke(initial_state)
        
        return {
            "success": final_state["error"] is None and final_state["results"] is not None,
            "sql": final_state["sql"],
            "results": final_state["results"],
            "error": final_state["error"],
            "attempts": final_state["attempt"]
        }
    
    def _generate_sql_node(self, state: SQLAgentState) -> SQLAgentState:
        """Node 1: SQL 생성"""
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
        
        chain = prompt | self.llm | StrOutputParser()
        sql = chain.invoke({"schema": state["schema"], "question": state["question"]}).strip()
        
        return {**state, "sql": sql, "attempt": state["attempt"] + 1}
    
    def _execute_sql_node(self, state: SQLAgentState) -> SQLAgentState:
        """Node 2: SQL 실행"""
        results, error = db.execute_query(state["sql"])
        
        if error:
            return {**state, "error": error, "results": None}
        else:
            return {**state, "error": None, "results": results}
    
    def _correction_node(self, state: SQLAgentState) -> SQLAgentState:
        """Node 3: SQL 수정"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "MySQL 오류를 수정하세요."),
            ("user", """스키마:
{schema}

질문: {question}
실패한 SQL: {sql}
에러: {error}

수정된 SQL (쿼리만, 마크다운 금지):""")
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        corrected_sql = chain.invoke({
            "schema": state["schema"],
            "question": state["question"],
            "sql": state["sql"],
            "error": state["error"]
        }).strip()
        
        return {**state, "sql": corrected_sql, "attempt": state["attempt"] + 1, "error": None}
    
    def _should_retry(self, state: SQLAgentState) -> str:
        """Conditional Edge: 재시도 여부 판단"""
        if state["error"] is None and state["results"] is not None:
            return "end"
        if state["attempt"] < state["max_attempts"]:
            return "correction"
        return "end"
    
    def _build_workflow(self) -> any:
        """LangGraph StateGraph 구성"""
        workflow = StateGraph(SQLAgentState)
        
        # 노드 추가
        workflow.add_node("generate_sql", self._generate_sql_node)
        workflow.add_node("execute_sql", self._execute_sql_node)
        workflow.add_node("correction", self._correction_node)
        
        # 엣지 연결
        workflow.set_entry_point("generate_sql")
        workflow.add_edge("generate_sql", "execute_sql")
        workflow.add_conditional_edges("execute_sql", self._should_retry, {
            "correction": "correction",
            "end": END
        })
        workflow.add_edge("correction", "execute_sql")
        
        return workflow.compile()


# 싱글톤 인스턴스
sql_agent = SQLAgent()


if __name__ == "__main__":
    """테스트"""
    print("=" * 70)
    print("SQL Agent 테스트")
    print("=" * 70)
    
    # 테스트 1: 정상 질문
    result = sql_agent.query("직원 수는?")
    print(f"\n질문: 직원 수는?")
    print(f"성공: {result['success']}")
    print(f"SQL: {result['sql']}")
    print(f"결과: {result['results']}")
    print(f"시도: {result['attempts']}회")
    
    # 테스트 2: 복잡한 질문
    result2 = sql_agent.query("각 부서별 평균 급여를 보여줘")
    print(f"\n질문: 각 부서별 평균 급여를 보여줘")
    print(f"성공: {result2['success']}")
    print(f"SQL: {result2['sql']}")
    print(f"결과: {result2['results'][:3]}")
    print(f"시도: {result2['attempts']}회")

