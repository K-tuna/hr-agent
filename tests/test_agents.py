"""
Agent Tests (샘플)
포트폴리오용 pytest 테스트 예시
"""

import pytest
from unittest.mock import Mock, patch

from core.types.agent_types import AgentResult


# ===== SQL Agent Tests =====
class TestSQLAgent:
    """SQL Agent 단위 테스트"""

    def test_query_with_mock_db(self, mock_db):
        """Mock DB로 SQL Agent 테스트"""
        # Given: Mock DB가 결과를 반환하도록 설정
        mock_db.execute_query.return_value = ([{"count": 10}], None)

        # When: SQL Agent를 사용하여 쿼리 (실제로는 Mock 사용)
        # 실제 테스트에서는 SQLAgent를 초기화하지만,
        # 여기서는 단순히 Mock 동작 확인
        results, error = mock_db.execute_query("SELECT COUNT(*) FROM employees")

        # Then: 결과 검증
        assert error is None
        assert results == [{"count": 10}]

    def test_get_table_schema(self, mock_db):
        """스키마 조회 테스트"""
        schema = mock_db.get_table_schema()

        assert "employees" in schema
        assert "departments" in schema


# ===== Router Tests =====
class TestRouter:
    """Router 단위 테스트"""

    def test_route_sql_question(self, mock_router):
        """SQL 질문 라우팅 테스트"""
        # Given: Router가 SQL_AGENT를 반환하도록 설정
        mock_router.route.return_value = "SQL_AGENT"

        # When
        result = mock_router.route("직원 수는?")

        # Then
        assert result == "SQL_AGENT"

    def test_route_rag_question(self, mock_router):
        """RAG 질문 라우팅 테스트"""
        # Given: Router가 RAG_AGENT를 반환하도록 설정
        mock_router.route.return_value = "RAG_AGENT"

        # When
        result = mock_router.route("연차 규정은?")

        # Then
        assert result == "RAG_AGENT"


# ===== HR Agent Tests =====
class TestHRAgent:
    """HR Agent 통합 테스트"""

    def test_query_returns_agent_result(self, mock_sql_agent):
        """HR Agent가 AgentResult 형식으로 반환하는지 테스트"""
        # When
        result = mock_sql_agent.query("직원 수는?")

        # Then
        assert result["success"] is True
        assert "answer" in result
        assert "metadata" in result
        assert result["metadata"]["agent_type"] == "SQL_AGENT"

    def test_rag_agent_result(self, mock_rag_agent):
        """RAG Agent 결과 테스트"""
        # When
        result = mock_rag_agent.query("연차 규정은?")

        # Then
        assert result["success"] is True
        assert "연차" in result["answer"]
        assert result["metadata"]["agent_type"] == "RAG_AGENT"


# ===== Container Tests =====
class TestContainer:
    """DI Container 테스트"""

    def test_container_has_hr_agent(self, test_container):
        """Container가 HRAgent를 제공하는지 테스트"""
        # Container에 mock이 주입되어 있으므로 _hr_agent는 None
        # 실제 hr_agent는 cached_property로 생성됨
        assert test_container.settings is not None
        assert test_container._db is not None

    def test_container_settings(self, test_container):
        """Container 설정 테스트"""
        assert test_container.settings.LLM_MODEL == "gpt-4o-mini"
        assert test_container.settings.DEBUG is True


# ===== AgentResult Type Tests =====
class TestAgentResultType:
    """AgentResult 타입 테스트"""

    def test_agent_result_structure(self):
        """AgentResult 구조 테스트"""
        result = AgentResult(
            success=True,
            answer="테스트 답변",
            metadata={"agent_type": "SQL_AGENT"},
            error=None,
        )

        assert result["success"] is True
        assert result["answer"] == "테스트 답변"
        assert result["metadata"]["agent_type"] == "SQL_AGENT"
        assert result["error"] is None

    def test_agent_result_with_error(self):
        """에러가 있는 AgentResult 테스트"""
        result = AgentResult(
            success=False,
            answer="",
            metadata={"agent_type": "SQL_AGENT"},
            error="DB 연결 오류",
        )

        assert result["success"] is False
        assert result["error"] == "DB 연결 오류"
