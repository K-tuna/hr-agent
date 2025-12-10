"""
Router - 질문 의도 분류기

사용법:
    from core.router import Router
    
    router = Router()
    agent_type = router.route("직원 수는?")
    # agent_type = "SQL_AGENT" 또는 "RAG_AGENT"
"""

from typing import Literal
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


AgentType = Literal["SQL_AGENT", "RAG_AGENT"]


class Router:
    """
    질문 의도 분류 Router
    - SQL_AGENT: 데이터베이스 조회
    - RAG_AGENT: 문서 검색
    """
    
    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0):
        """
        Args:
            model: OpenAI 모델명
            temperature: LLM temperature (0=결정적)
        """
        self.model = model
        self.temperature = temperature
        self._init_chain()
    
    def _init_chain(self):
        """분류 체인 초기화"""
        # LLM
        llm = ChatOpenAI(model=self.model, temperature=self.temperature)
        
        # 프롬프트 (현업 스타일 - Few-shot 예시 포함)
        template = """당신은 HR 시스템의 질문 분류 전문가입니다.
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
        
        prompt = ChatPromptTemplate.from_template(template)
        
        # 체인 (LCEL)
        self.chain = prompt | llm | StrOutputParser()
    
    def route(self, question: str) -> AgentType:
        """
        질문을 분석하여 적절한 Agent로 라우팅
        
        Args:
            question: 사용자 질문
            
        Returns:
            "SQL_AGENT" 또는 "RAG_AGENT"
        """
        try:
            result = self.chain.invoke({"question": question})
            agent_type = result.strip()
            
            # 검증
            if agent_type not in ["SQL_AGENT", "RAG_AGENT"]:
                # 기본값: RAG_AGENT (안전한 선택)
                return "RAG_AGENT"
            
            return agent_type
        
        except Exception as e:
            # 오류 시 기본값
            print(f"⚠️ Router 오류: {e}, RAG_AGENT로 폴백")
            return "RAG_AGENT"


# 편의 함수
def create_router(model: str = "gpt-4o-mini") -> Router:
    """
    Router 인스턴스 생성 헬퍼 함수
    
    Returns:
        Router 인스턴스
    """
    return Router(model=model)

