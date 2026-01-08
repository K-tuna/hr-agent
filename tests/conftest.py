"""
Pytest Fixtures
테스트용 공통 fixture 정의
"""

import pytest
from unittest.mock import Mock, MagicMock
from typing import List, Dict, Any, Optional, Tuple

from app.core.config import Settings
from core.container import Container
from core.types.agent_types import AgentResult


# ===== Mock Settings =====
@pytest.fixture
def mock_settings() -> Settings:
    """테스트용 Settings"""
    return Settings(
        DATABASE_URL="mysql+pymysql://test:test@localhost:3306/test_db",
        OPENAI_API_KEY="test-api-key",
        LLM_MODEL="gpt-4o-mini",
        LLM_TEMPERATURE=0.0,
        SQL_AGENT_MAX_ATTEMPTS=3,
        RAG_TOP_K=3,
        DEBUG=True,
    )


# ===== Mock Database =====
@pytest.fixture
def mock_db() -> Mock:
    """Mock DatabaseConnection"""
    db = Mock()
    db.execute_query.return_value = ([{"count": 10}], None)
    db.get_table_schema.return_value = """
TABLE employees:
  - emp_id (int)
  - name (varchar)
  - dept_id (int)

TABLE departments:
  - dept_id (int)
  - name (varchar)
"""
    db.test_connection.return_value = True
    return db


# ===== Mock LLM =====
@pytest.fixture
def mock_llm() -> Mock:
    """Mock ChatOpenAI"""
    llm = Mock()
    llm.invoke.return_value = Mock(content="SELECT COUNT(*) FROM employees;")
    return llm


# ===== Mock SQL Agent =====
@pytest.fixture
def mock_sql_agent() -> Mock:
    """Mock SQLAgent"""
    agent = Mock()
    agent.query.return_value = AgentResult(
        success=True,
        answer="10명",
        metadata={"agent_type": "SQL_AGENT", "sql": "SELECT COUNT(*) FROM employees;"},
        error=None,
    )
    return agent


# ===== Mock RAG Agent =====
@pytest.fixture
def mock_rag_agent() -> Mock:
    """Mock RAGAgent"""
    agent = Mock()
    agent.query.return_value = AgentResult(
        success=True,
        answer="1년 이상 근속한 직원에게 15일의 연차휴가가 부여됩니다.",
        metadata={"agent_type": "RAG_AGENT", "source_docs": ["연차휴가 규정..."]},
        error=None,
    )
    return agent


# ===== Mock Router =====
@pytest.fixture
def mock_router() -> Mock:
    """Mock Router"""
    router = Mock()
    router.route.return_value = "SQL_AGENT"
    return router


# ===== Test Container =====
@pytest.fixture
def test_container(mock_settings, mock_db, mock_router, mock_sql_agent, mock_rag_agent) -> Container:
    """
    테스트용 Container (의존성 주입)

    모든 컴포넌트가 Mock으로 대체됨
    """
    return Container(
        settings=mock_settings,
        _db=mock_db,
        _router=mock_router,
        _sql_agent=mock_sql_agent,
        _rag_agent=mock_rag_agent,
    )
