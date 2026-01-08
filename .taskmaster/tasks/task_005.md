# Task ID: 5

**Title:** SQL Query Validation 및 위험 쿼리 차단

**Status:** pending

**Dependencies:** None

**Priority:** high

**Description:** 생성된 SQL의 문법 검증 및 위험한 쿼리(INSERT/UPDATE/DELETE/DROP) 실행 차단 시스템 구현

**Details:**

## 구현 세부사항

### 1. SQL 파서 통합
- `sqlparse` 라이브러리 사용 (Python 표준)
```python
import sqlparse

def validate_sql(sql: str) -> tuple[bool, str]:
    parsed = sqlparse.parse(sql)
    if not parsed:
        return False, "Invalid SQL syntax"
    return True, ""
```

### 2. 허용 쿼리 화이트리스트
- SELECT 문만 허용
- 허용되는 키워드: `SELECT`, `FROM`, `WHERE`, `JOIN`, `GROUP BY`, `HAVING`, `ORDER BY`, `LIMIT`

### 3. 위험 키워드 블랙리스트
- 차단 키워드:
  - DML: `INSERT`, `UPDATE`, `DELETE`, `REPLACE`, `MERGE`
  - DDL: `DROP`, `CREATE`, `ALTER`, `TRUNCATE`, `RENAME`
  - DCL: `GRANT`, `REVOKE`
  - 기타: `EXEC`, `EXECUTE`, `CALL`

### 4. SQL Validator 클래스 (`core/guardrails/sql_validator.py`)
```python
class SQLValidator:
    def validate(self, sql: str) -> ValidationResult:
        # 1. 문법 검증
        # 2. 블랙리스트 키워드 체크
        # 3. SELECT 문인지 확인
        # 4. 위험도 점수 계산 (0-100)
        pass
```

### 5. SQL Agent 통합
- `core/agents/sql_agent.py`의 `_execute_sql()` 전에 검증
- 차단 시 에러 메시지 반환: `"위험한 쿼리가 감지되어 실행이 차단되었습니다."`

### 6. 로깅
- 차단된 쿼리를 `logs/blocked_queries.log`에 기록
- 보안 감사 추적 용도

### 수용 기준
- 위험 쿼리 100% 차단 (테스트 케이스 15개)
- 정상 SELECT 쿼리 100% 통과
- 차단 시 명확한 에러 메시지 제공

**Test Strategy:**

## 검증 방법

1. **정상 쿼리 테스트**
```python
from core.guardrails.sql_validator import SQLValidator

validator = SQLValidator()

# 통과해야 하는 쿼리들
valid_queries = [
    "SELECT * FROM employees",
    "SELECT e.name, d.dept_name FROM employees e JOIN departments d ON e.dept_id = d.dept_id",
    "SELECT AVG(salary) FROM salaries GROUP BY dept_id"
]

for sql in valid_queries:
    result = validator.validate(sql)
    assert result.is_valid == True
```

2. **위험 쿼리 차단 테스트**
```python
blocked_queries = [
    "DROP TABLE employees",
    "DELETE FROM employees WHERE dept_id = 1",
    "INSERT INTO employees VALUES (999, 'Hacker')",
    "UPDATE salaries SET base_salary = 0",
    "TRUNCATE TABLE departments"
]

for sql in blocked_queries:
    result = validator.validate(sql)
    assert result.is_valid == False
    assert "차단" in result.error_message
```

3. **통합 테스트 (SQL Agent)**
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -d '{"question": "모든 직원 데이터 삭제해줘"}'
# 응답: {"error": "위험한 쿼리가 감지되어 실행이 차단되었습니다."}
```

4. **로그 확인**
```bash
cat logs/blocked_queries.log
# 출력: [2025-12-14 10:30:00] BLOCKED: DROP TABLE employees
```
