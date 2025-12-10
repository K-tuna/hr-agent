"""
통합 HR Agent Graph

사용법:
    from core.graph import HRAgent
    
    agent = HRAgent()
    result = agent.query("직원 수는?")
    print(result["final_answer"])
"""

from typing import TypedDict, Literal, Dict, Any
from langgraph.graph import StateGraph, END

from core.router import Router
from core.sql_agent import SQLAgent
from core.rag_agent import RAGAgent


class AgentState(TypedDict):
    """통합 Agent의 상태"""
    question: str           # 사용자 질문
    agent_type: str         # 선택된 Agent (SQL_AGENT | RAG_AGENT)
    sql_result: dict        # SQL Agent 결과
    rag_result: dict        # RAG Agent 결과
    final_answer: str       # 최종 답변
    error: str              # 오류 메시지


class HRAgent:
    """
    HR 통합 Agent
    - Router로 질문 분류
    - SQL Agent 또는 RAG Agent로 처리
    """
    
    def __init__(
        self,
        model: str = "gpt-4o-mini",
        verbose: bool = False
    ):
        """
        Args:
            model: OpenAI 모델명
            verbose: 디버그 출력 여부
        """
        self.model = model
        self.verbose = verbose
        
        # 컴포넌트 초기화
        self.router = Router(model=model)
        self.sql_agent = SQLAgent(model=model)
        self.rag_agent = RAGAgent(model=model)
        
        # 그래프 구성
        self.app = self._build_graph()
    
    def _log(self, message: str):
        """디버그 로그 출력"""
        if self.verbose:
            print(message)
    
    def _route_node(self, state: AgentState) -> AgentState:
        """질문을 분석하여 Agent 선택"""
        agent_type = self.router.route(state["question"])
        self._log(f"[Router] 질문: {state['question']}")
        self._log(f"[Router] 선택된 Agent: {agent_type}")
        state["agent_type"] = agent_type
        return state
    
    def _sql_agent_node(self, state: AgentState) -> AgentState:
        """SQL Agent 실행"""
        self._log(f"[SQL Agent] 질문 처리 중...")
        
        try:
            result = self.sql_agent.query(state["question"])
            state["sql_result"] = result
            
            # 최종 답변 생성
            if result["success"]:
                if result["results"]:
                    # 결과를 보기 좋게 포맷팅
                    state["final_answer"] = self._format_sql_results(result["results"])
                else:
                    state["final_answer"] = "조회 결과가 없습니다."
            else:
                state["final_answer"] = f"SQL 실행 오류: {result.get('error', 'Unknown error')}"
                state["error"] = result.get("error", "")
            
            self._log(f"[SQL Agent] 완료")
            
        except Exception as e:
            state["error"] = str(e)
            state["final_answer"] = f"SQL Agent 오류: {str(e)}"
            self._log(f"[SQL Agent] 오류: {e}")
        
        return state
    
    def _rag_agent_node(self, state: AgentState) -> AgentState:
        """RAG Agent 실행"""
        self._log(f"[RAG Agent] 질문 처리 중...")
        
        try:
            result = self.rag_agent.query(state["question"])
            state["rag_result"] = result
            
            # 최종 답변 생성
            if result["success"]:
                state["final_answer"] = result["answer"]
            else:
                state["final_answer"] = f"RAG 검색 오류: {result.get('error', 'Unknown error')}"
                state["error"] = result.get("error", "")
            
            self._log(f"[RAG Agent] 완료")
            
        except Exception as e:
            state["error"] = str(e)
            state["final_answer"] = f"RAG Agent 오류: {str(e)}"
            self._log(f"[RAG Agent] 오류: {e}")
        
        return state
    
    def _route_to_agent(self, state: AgentState) -> Literal["sql_agent", "rag_agent"]:
        """Agent 타입에 따라 다음 노드 결정"""
        if state["agent_type"] == "SQL_AGENT":
            return "sql_agent"
        else:
            return "rag_agent"
    
    def _format_sql_results(self, results: list) -> str:
        """SQL 결과를 보기 좋게 포맷팅"""
        if not results:
            return "조회 결과가 없습니다."
        
        # 단일 값인 경우
        if len(results) == 1 and len(results[0]) == 1:
            value = list(results[0].values())[0]
            return str(value)
        
        # 테이블 형태로 포맷팅
        output = []
        for row in results[:10]:  # 최대 10개만 표시
            output.append(str(dict(row)))
        
        if len(results) > 10:
            output.append(f"... 외 {len(results) - 10}개 행")
        
        return "\n".join(output)
    
    def _build_graph(self) -> StateGraph:
        """LangGraph 구성"""
        # StateGraph 생성
        workflow = StateGraph(AgentState)
        
        # 노드 추가
        workflow.add_node("router", self._route_node)
        workflow.add_node("sql_agent", self._sql_agent_node)
        workflow.add_node("rag_agent", self._rag_agent_node)
        
        # 엣지 추가
        workflow.set_entry_point("router")
        
        # 조건부 라우팅
        workflow.add_conditional_edges(
            "router",
            self._route_to_agent,
            {
                "sql_agent": "sql_agent",
                "rag_agent": "rag_agent"
            }
        )
        
        # Agent 실행 후 종료
        workflow.add_edge("sql_agent", END)
        workflow.add_edge("rag_agent", END)
        
        # 컴파일
        return workflow.compile()
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        질문에 대한 답변 생성
        
        Args:
            question: 사용자 질문
            
        Returns:
            {
                "question": str,
                "agent_type": str,
                "final_answer": str,
                "sql_result": dict (optional),
                "rag_result": dict (optional),
                "error": str,
                "success": bool
            }
        """
        # 초기 상태
        initial_state = {
            "question": question,
            "agent_type": "",
            "sql_result": {},
            "rag_result": {},
            "final_answer": "",
            "error": ""
        }
        
        # 그래프 실행
        result = self.app.invoke(initial_state)
        
        # 결과 포맷팅
        return {
            "question": question,
            "agent_type": result.get("agent_type", ""),
            "final_answer": result.get("final_answer", ""),
            "sql_result": result.get("sql_result", {}),
            "rag_result": result.get("rag_result", {}),
            "error": result.get("error", ""),
            "success": not bool(result.get("error", ""))
        }
    
    def stream(self, question: str):
        """
        스트리밍 응답 (향후 구현)
        
        Args:
            question: 사용자 질문
            
        Yields:
            상태 업데이트
        """
        initial_state = {
            "question": question,
            "agent_type": "",
            "sql_result": {},
            "rag_result": {},
            "final_answer": "",
            "error": ""
        }
        
        for state in self.app.stream(initial_state):
            yield state


# 편의 함수
def create_hr_agent(model: str = "gpt-4o-mini", verbose: bool = False) -> HRAgent:
    """
    HRAgent 인스턴스 생성 헬퍼 함수
    
    Returns:
        HRAgent 인스턴스
    """
    return HRAgent(model=model, verbose=verbose)

