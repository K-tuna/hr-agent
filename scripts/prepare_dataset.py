"""
파인튜닝 데이터셋 생성 스크립트
- SQL 데이터: 100개 (질문 → SQL)
- RAG 데이터: 100개 (질문 → 답변)
"""
import json
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent / "data" / "finetuning"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# SQL 데이터셋 (100개)
# ============================================================
SQL_DATA = [
    # 직원 수 관련 (10개)
    {"q": "전체 직원 수는 몇 명이야?", "sql": "SELECT COUNT(*) as total_employees FROM employees WHERE status = 'ACTIVE'"},
    {"q": "개발팀 직원 수 알려줘", "sql": "SELECT COUNT(*) as count FROM employees e JOIN departments d ON e.dept_id = d.dept_id WHERE d.name = '개발' AND e.status = 'ACTIVE'"},
    {"q": "영업팀에 몇 명이 있어?", "sql": "SELECT COUNT(*) as count FROM employees e JOIN departments d ON e.dept_id = d.dept_id WHERE d.name = '영업' AND e.status = 'ACTIVE'"},
    {"q": "인사팀 인원 현황", "sql": "SELECT COUNT(*) as count FROM employees e JOIN departments d ON e.dept_id = d.dept_id WHERE d.name = '인사' AND e.status = 'ACTIVE'"},
    {"q": "부서별 직원 수 알려줘", "sql": "SELECT d.name as department, COUNT(*) as count FROM employees e JOIN departments d ON e.dept_id = d.dept_id WHERE e.status = 'ACTIVE' GROUP BY d.name"},
    {"q": "사원 직급은 몇 명이야?", "sql": "SELECT COUNT(*) as count FROM employees WHERE position = '사원' AND status = 'ACTIVE'"},
    {"q": "과장 이상 직원 수", "sql": "SELECT COUNT(*) as count FROM employees WHERE position IN ('과장', '부장') AND status = 'ACTIVE'"},
    {"q": "2023년에 입사한 직원 수", "sql": "SELECT COUNT(*) as count FROM employees WHERE YEAR(join_date) = 2023"},
    {"q": "휴직 중인 직원 몇 명이야?", "sql": "SELECT COUNT(*) as count FROM employees WHERE status = 'LEAVE'"},
    {"q": "퇴사자 수 알려줘", "sql": "SELECT COUNT(*) as count FROM employees WHERE status = 'RESIGNED'"},

    # 급여 관련 (20개)
    {"q": "개발팀 평균 급여는?", "sql": "SELECT AVG(s.base_salary) as avg_salary FROM salaries s JOIN employees e ON s.emp_id = e.emp_id JOIN departments d ON e.dept_id = d.dept_id WHERE d.name = '개발'"},
    {"q": "영업팀 평균 연봉", "sql": "SELECT AVG(s.base_salary) as avg_salary FROM salaries s JOIN employees e ON s.emp_id = e.emp_id JOIN departments d ON e.dept_id = d.dept_id WHERE d.name = '영업'"},
    {"q": "전체 직원 평균 급여", "sql": "SELECT AVG(base_salary) as avg_salary FROM salaries"},
    {"q": "부서별 평균 급여 비교", "sql": "SELECT d.name as department, AVG(s.base_salary) as avg_salary FROM salaries s JOIN employees e ON s.emp_id = e.emp_id JOIN departments d ON e.dept_id = d.dept_id GROUP BY d.name ORDER BY avg_salary DESC"},
    {"q": "가장 높은 급여 받는 직원은?", "sql": "SELECT e.name, s.base_salary FROM employees e JOIN salaries s ON e.emp_id = s.emp_id ORDER BY s.base_salary DESC LIMIT 1"},
    {"q": "가장 낮은 급여는 얼마야?", "sql": "SELECT MIN(base_salary) as min_salary FROM salaries"},
    {"q": "급여 총액은?", "sql": "SELECT SUM(base_salary) as total_salary FROM salaries"},
    {"q": "보너스 총액 알려줘", "sql": "SELECT SUM(bonus) as total_bonus FROM salaries"},
    {"q": "개발팀 보너스 평균", "sql": "SELECT AVG(s.bonus) as avg_bonus FROM salaries s JOIN employees e ON s.emp_id = e.emp_id JOIN departments d ON e.dept_id = d.dept_id WHERE d.name = '개발'"},
    {"q": "급여 5000만원 이상인 직원", "sql": "SELECT e.name, s.base_salary FROM employees e JOIN salaries s ON e.emp_id = s.emp_id WHERE s.base_salary >= 5000000"},
    {"q": "급여 4000만원 미만인 직원 수", "sql": "SELECT COUNT(*) as count FROM salaries WHERE base_salary < 4000000"},
    {"q": "직급별 평균 급여", "sql": "SELECT e.position, AVG(s.base_salary) as avg_salary FROM employees e JOIN salaries s ON e.emp_id = s.emp_id GROUP BY e.position ORDER BY avg_salary DESC"},
    {"q": "부장 평균 급여", "sql": "SELECT AVG(s.base_salary) as avg_salary FROM salaries s JOIN employees e ON s.emp_id = e.emp_id WHERE e.position = '부장'"},
    {"q": "사원 평균 급여는?", "sql": "SELECT AVG(s.base_salary) as avg_salary FROM salaries s JOIN employees e ON s.emp_id = e.emp_id WHERE e.position = '사원'"},
    {"q": "급여와 보너스 합계 top 5", "sql": "SELECT e.name, (s.base_salary + s.bonus) as total FROM employees e JOIN salaries s ON e.emp_id = s.emp_id ORDER BY total DESC LIMIT 5"},
    {"q": "보너스 없는 직원", "sql": "SELECT e.name FROM employees e JOIN salaries s ON e.emp_id = s.emp_id WHERE s.bonus = 0"},
    {"q": "보너스 100만원 이상 직원", "sql": "SELECT e.name, s.bonus FROM employees e JOIN salaries s ON e.emp_id = s.emp_id WHERE s.bonus >= 1000000"},
    {"q": "인사팀 급여 총액", "sql": "SELECT SUM(s.base_salary) as total FROM salaries s JOIN employees e ON s.emp_id = e.emp_id JOIN departments d ON e.dept_id = d.dept_id WHERE d.name = '인사'"},
    {"q": "영업팀 보너스 총액", "sql": "SELECT SUM(s.bonus) as total FROM salaries s JOIN employees e ON s.emp_id = e.emp_id JOIN departments d ON e.dept_id = d.dept_id WHERE d.name = '영업'"},
    {"q": "급여 중간값은?", "sql": "SELECT base_salary as median_salary FROM salaries ORDER BY base_salary LIMIT 1 OFFSET (SELECT COUNT(*)/2 FROM salaries)"},

    # 근태 관련 (20개)
    {"q": "오늘 지각한 사람 있어?", "sql": "SELECT e.name FROM attendance a JOIN employees e ON a.emp_id = e.emp_id WHERE a.date = CURDATE() AND a.status = 'LATE'"},
    {"q": "1월 2일 출근 현황", "sql": "SELECT e.name, a.check_in, a.status FROM attendance a JOIN employees e ON a.emp_id = e.emp_id WHERE a.date = '2024-01-02'"},
    {"q": "김철수 근태 기록", "sql": "SELECT a.date, a.check_in, a.check_out, a.status FROM attendance a JOIN employees e ON a.emp_id = e.emp_id WHERE e.name = '김철수' ORDER BY a.date"},
    {"q": "이번 달 지각 횟수", "sql": "SELECT COUNT(*) as late_count FROM attendance WHERE status = 'LATE' AND MONTH(date) = MONTH(CURDATE())"},
    {"q": "휴가 사용 현황", "sql": "SELECT e.name, COUNT(*) as vacation_days FROM attendance a JOIN employees e ON a.emp_id = e.emp_id WHERE a.status = 'VACATION' GROUP BY e.name"},
    {"q": "결근자 명단", "sql": "SELECT DISTINCT e.name FROM attendance a JOIN employees e ON a.emp_id = e.emp_id WHERE a.status = 'ABSENT'"},
    {"q": "개발팀 지각 횟수", "sql": "SELECT COUNT(*) as count FROM attendance a JOIN employees e ON a.emp_id = e.emp_id JOIN departments d ON e.dept_id = d.dept_id WHERE d.name = '개발' AND a.status = 'LATE'"},
    {"q": "가장 많이 지각한 직원", "sql": "SELECT e.name, COUNT(*) as late_count FROM attendance a JOIN employees e ON a.emp_id = e.emp_id WHERE a.status = 'LATE' GROUP BY e.name ORDER BY late_count DESC LIMIT 1"},
    {"q": "1월 휴가 사용자", "sql": "SELECT DISTINCT e.name FROM attendance a JOIN employees e ON a.emp_id = e.emp_id WHERE a.status = 'VACATION' AND MONTH(a.date) = 1"},
    {"q": "출근율 계산해줘", "sql": "SELECT ROUND(SUM(CASE WHEN status = 'PRESENT' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as attendance_rate FROM attendance"},
    {"q": "부서별 지각 현황", "sql": "SELECT d.name, COUNT(*) as late_count FROM attendance a JOIN employees e ON a.emp_id = e.emp_id JOIN departments d ON e.dept_id = d.dept_id WHERE a.status = 'LATE' GROUP BY d.name"},
    {"q": "9시 이전 출근한 사람", "sql": "SELECT DISTINCT e.name FROM attendance a JOIN employees e ON a.emp_id = e.emp_id WHERE a.check_in < '09:00:00'"},
    {"q": "야근한 직원 (18시 이후 퇴근)", "sql": "SELECT e.name, a.date, a.check_out FROM attendance a JOIN employees e ON a.emp_id = e.emp_id WHERE a.check_out > '18:30:00'"},
    {"q": "평균 출근 시간", "sql": "SELECT AVG(TIME_TO_SEC(check_in))/3600 as avg_check_in_hour FROM attendance WHERE check_in IS NOT NULL"},
    {"q": "1월 3일 결근자", "sql": "SELECT e.name FROM attendance a JOIN employees e ON a.emp_id = e.emp_id WHERE a.date = '2024-01-03' AND a.status = 'ABSENT'"},
    {"q": "연속 지각 2회 이상인 직원", "sql": "SELECT e.name, COUNT(*) as late_count FROM attendance a JOIN employees e ON a.emp_id = e.emp_id WHERE a.status = 'LATE' GROUP BY e.name HAVING late_count >= 2"},
    {"q": "이번 주 휴가자", "sql": "SELECT e.name, a.date FROM attendance a JOIN employees e ON a.emp_id = e.emp_id WHERE a.status = 'VACATION' AND WEEK(a.date) = WEEK(CURDATE())"},
    {"q": "직원별 출근 일수", "sql": "SELECT e.name, COUNT(*) as work_days FROM attendance a JOIN employees e ON a.emp_id = e.emp_id WHERE a.status = 'PRESENT' GROUP BY e.name ORDER BY work_days DESC"},
    {"q": "영업팀 휴가 현황", "sql": "SELECT e.name, COUNT(*) as vacation_days FROM attendance a JOIN employees e ON a.emp_id = e.emp_id JOIN departments d ON e.dept_id = d.dept_id WHERE d.name = '영업' AND a.status = 'VACATION' GROUP BY e.name"},
    {"q": "인사팀 출근율", "sql": "SELECT ROUND(SUM(CASE WHEN a.status = 'PRESENT' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as rate FROM attendance a JOIN employees e ON a.emp_id = e.emp_id JOIN departments d ON e.dept_id = d.dept_id WHERE d.name = '인사'"},

    # 평가 관련 (20개)
    {"q": "김철수 평가 점수", "sql": "SELECT ev.year, ev.quarter, ev.score, ev.feedback FROM evaluations ev JOIN employees e ON ev.emp_id = e.emp_id WHERE e.name = '김철수'"},
    {"q": "평가 평균 점수", "sql": "SELECT AVG(score) as avg_score FROM evaluations"},
    {"q": "4점 이상 받은 직원", "sql": "SELECT e.name, ev.score FROM evaluations ev JOIN employees e ON ev.emp_id = e.emp_id WHERE ev.score >= 4.0"},
    {"q": "최고 평가 점수 받은 사람", "sql": "SELECT e.name, ev.score FROM evaluations ev JOIN employees e ON ev.emp_id = e.emp_id ORDER BY ev.score DESC LIMIT 1"},
    {"q": "최저 평가 점수는?", "sql": "SELECT MIN(score) as min_score FROM evaluations"},
    {"q": "부서별 평균 평가 점수", "sql": "SELECT d.name, AVG(ev.score) as avg_score FROM evaluations ev JOIN employees e ON ev.emp_id = e.emp_id JOIN departments d ON e.dept_id = d.dept_id GROUP BY d.name ORDER BY avg_score DESC"},
    {"q": "개발팀 평균 평가", "sql": "SELECT AVG(ev.score) as avg_score FROM evaluations ev JOIN employees e ON ev.emp_id = e.emp_id JOIN departments d ON e.dept_id = d.dept_id WHERE d.name = '개발'"},
    {"q": "영업팀 평가 현황", "sql": "SELECT e.name, ev.score, ev.feedback FROM evaluations ev JOIN employees e ON ev.emp_id = e.emp_id JOIN departments d ON e.dept_id = d.dept_id WHERE d.name = '영업'"},
    {"q": "2023년 4분기 평가 결과", "sql": "SELECT e.name, ev.score FROM evaluations ev JOIN employees e ON ev.emp_id = e.emp_id WHERE ev.year = 2023 AND ev.quarter = 4"},
    {"q": "3점 미만 직원", "sql": "SELECT e.name, ev.score FROM evaluations ev JOIN employees e ON ev.emp_id = e.emp_id WHERE ev.score < 3.5"},
    {"q": "직급별 평균 평가", "sql": "SELECT e.position, AVG(ev.score) as avg_score FROM evaluations ev JOIN employees e ON ev.emp_id = e.emp_id GROUP BY e.position ORDER BY avg_score DESC"},
    {"q": "부장 평균 평가 점수", "sql": "SELECT AVG(ev.score) as avg_score FROM evaluations ev JOIN employees e ON ev.emp_id = e.emp_id WHERE e.position = '부장'"},
    {"q": "평가 피드백에 리더십 언급된 직원", "sql": "SELECT e.name, ev.feedback FROM evaluations ev JOIN employees e ON ev.emp_id = e.emp_id WHERE ev.feedback LIKE '%리더십%'"},
    {"q": "평가 점수 분포", "sql": "SELECT FLOOR(score) as score_range, COUNT(*) as count FROM evaluations GROUP BY FLOOR(score)"},
    {"q": "평가 4.5 이상인 직원 명단", "sql": "SELECT e.name, e.position, ev.score FROM evaluations ev JOIN employees e ON ev.emp_id = e.emp_id WHERE ev.score >= 4.5"},
    {"q": "인사팀 평가 평균", "sql": "SELECT AVG(ev.score) as avg_score FROM evaluations ev JOIN employees e ON ev.emp_id = e.emp_id JOIN departments d ON e.dept_id = d.dept_id WHERE d.name = '인사'"},
    {"q": "신입(사원) 평가 평균", "sql": "SELECT AVG(ev.score) as avg_score FROM evaluations ev JOIN employees e ON ev.emp_id = e.emp_id WHERE e.position = '사원'"},
    {"q": "평가 피드백 목록", "sql": "SELECT e.name, ev.feedback FROM evaluations ev JOIN employees e ON ev.emp_id = e.emp_id WHERE ev.feedback IS NOT NULL"},
    {"q": "분기별 평균 평가", "sql": "SELECT quarter, AVG(score) as avg_score FROM evaluations GROUP BY quarter ORDER BY quarter"},
    {"q": "평가 점수 상위 5명", "sql": "SELECT e.name, ev.score FROM evaluations ev JOIN employees e ON ev.emp_id = e.emp_id ORDER BY ev.score DESC LIMIT 5"},

    # 직원 정보 관련 (20개)
    {"q": "김철수 정보 알려줘", "sql": "SELECT e.name, e.email, d.name as department, e.position, e.join_date FROM employees e JOIN departments d ON e.dept_id = d.dept_id WHERE e.name = '김철수'"},
    {"q": "개발팀 직원 명단", "sql": "SELECT e.name, e.position FROM employees e JOIN departments d ON e.dept_id = d.dept_id WHERE d.name = '개발' AND e.status = 'ACTIVE'"},
    {"q": "부장 목록", "sql": "SELECT e.name, d.name as department FROM employees e JOIN departments d ON e.dept_id = d.dept_id WHERE e.position = '부장'"},
    {"q": "2024년 입사자", "sql": "SELECT name, join_date FROM employees WHERE YEAR(join_date) = 2024"},
    {"q": "서울 근무 직원", "sql": "SELECT e.name FROM employees e JOIN departments d ON e.dept_id = d.dept_id WHERE d.location = '서울'"},
    {"q": "부산 근무 직원", "sql": "SELECT e.name FROM employees e JOIN departments d ON e.dept_id = d.dept_id WHERE d.location = '부산'"},
    {"q": "근속 5년 이상 직원", "sql": "SELECT name, join_date FROM employees WHERE DATEDIFF(CURDATE(), join_date) >= 1825"},
    {"q": "신입 직원 (1년 미만)", "sql": "SELECT name, join_date FROM employees WHERE DATEDIFF(CURDATE(), join_date) < 365"},
    {"q": "이메일 목록", "sql": "SELECT name, email FROM employees WHERE status = 'ACTIVE'"},
    {"q": "부서별 직원 명단", "sql": "SELECT d.name as department, GROUP_CONCAT(e.name) as employees FROM employees e JOIN departments d ON e.dept_id = d.dept_id WHERE e.status = 'ACTIVE' GROUP BY d.name"},
    {"q": "대리 직급 명단", "sql": "SELECT e.name, d.name as department FROM employees e JOIN departments d ON e.dept_id = d.dept_id WHERE e.position = '대리'"},
    {"q": "과장 직급 명단", "sql": "SELECT e.name, d.name as department FROM employees e JOIN departments d ON e.dept_id = d.dept_id WHERE e.position = '과장'"},
    {"q": "가장 오래 근무한 직원", "sql": "SELECT name, join_date FROM employees ORDER BY join_date LIMIT 1"},
    {"q": "가장 최근 입사자", "sql": "SELECT name, join_date FROM employees ORDER BY join_date DESC LIMIT 1"},
    {"q": "입사일 순 직원 목록", "sql": "SELECT name, join_date FROM employees ORDER BY join_date"},
    {"q": "영업팀 과장", "sql": "SELECT e.name FROM employees e JOIN departments d ON e.dept_id = d.dept_id WHERE d.name = '영업' AND e.position = '과장'"},
    {"q": "인사팀 직원 이메일", "sql": "SELECT e.name, e.email FROM employees e JOIN departments d ON e.dept_id = d.dept_id WHERE d.name = '인사'"},
    {"q": "직급별 인원 현황", "sql": "SELECT position, COUNT(*) as count FROM employees WHERE status = 'ACTIVE' GROUP BY position"},
    {"q": "부서 목록", "sql": "SELECT name, location FROM departments"},
    {"q": "근무지별 인원", "sql": "SELECT d.location, COUNT(*) as count FROM employees e JOIN departments d ON e.dept_id = d.dept_id WHERE e.status = 'ACTIVE' GROUP BY d.location"},

    # 복합 쿼리 (10개)
    {"q": "급여 높은 순 직원 목록", "sql": "SELECT e.name, d.name as department, s.base_salary FROM employees e JOIN departments d ON e.dept_id = d.dept_id JOIN salaries s ON e.emp_id = s.emp_id ORDER BY s.base_salary DESC"},
    {"q": "평가 점수와 급여 비교", "sql": "SELECT e.name, ev.score, s.base_salary FROM employees e JOIN evaluations ev ON e.emp_id = ev.emp_id JOIN salaries s ON e.emp_id = s.emp_id ORDER BY ev.score DESC"},
    {"q": "부서별 급여 총액과 인원", "sql": "SELECT d.name, COUNT(*) as count, SUM(s.base_salary) as total_salary FROM employees e JOIN departments d ON e.dept_id = d.dept_id JOIN salaries s ON e.emp_id = s.emp_id GROUP BY d.name"},
    {"q": "지각 많은 직원의 평가 점수", "sql": "SELECT e.name, COUNT(a.att_id) as late_count, ev.score FROM employees e JOIN attendance a ON e.emp_id = a.emp_id JOIN evaluations ev ON e.emp_id = ev.emp_id WHERE a.status = 'LATE' GROUP BY e.name, ev.score ORDER BY late_count DESC"},
    {"q": "고성과자 급여 평균", "sql": "SELECT AVG(s.base_salary) as avg_salary FROM employees e JOIN evaluations ev ON e.emp_id = ev.emp_id JOIN salaries s ON e.emp_id = s.emp_id WHERE ev.score >= 4.5"},
    {"q": "저성과자 명단", "sql": "SELECT e.name, ev.score, d.name as department FROM employees e JOIN evaluations ev ON e.emp_id = ev.emp_id JOIN departments d ON e.dept_id = d.dept_id WHERE ev.score < 3.5"},
    {"q": "개발팀 급여와 평가 현황", "sql": "SELECT e.name, s.base_salary, ev.score FROM employees e JOIN departments d ON e.dept_id = d.dept_id JOIN salaries s ON e.emp_id = s.emp_id JOIN evaluations ev ON e.emp_id = ev.emp_id WHERE d.name = '개발'"},
    {"q": "휴가 많이 쓴 직원 급여", "sql": "SELECT e.name, COUNT(a.att_id) as vacation_days, s.base_salary FROM employees e JOIN attendance a ON e.emp_id = a.emp_id JOIN salaries s ON e.emp_id = s.emp_id WHERE a.status = 'VACATION' GROUP BY e.name, s.base_salary ORDER BY vacation_days DESC"},
    {"q": "부장 급여와 평가 비교", "sql": "SELECT e.name, s.base_salary, ev.score FROM employees e JOIN salaries s ON e.emp_id = s.emp_id JOIN evaluations ev ON e.emp_id = ev.emp_id WHERE e.position = '부장'"},
    {"q": "신입 직원 평가 현황", "sql": "SELECT e.name, e.join_date, ev.score FROM employees e JOIN evaluations ev ON e.emp_id = ev.emp_id WHERE e.position = '사원' ORDER BY e.join_date DESC"},
]

# ============================================================
# RAG 데이터셋 (100개)
# ============================================================
RAG_DATA = [
    # 근무시간 관련 (15개)
    {"q": "기본 근무시간은?", "a": "기본근무시간은 1일 7시간 30분입니다. 출근시간은 09:30, 퇴근시간은 18:00을 기준으로 합니다."},
    {"q": "코어타임이 뭐야?", "a": "코어타임은 유연근무제 적용 시 반드시 근무해야 하는 필수 시간대로, 10:00~16:00입니다."},
    {"q": "연장근로 수당은?", "a": "연장근로수당은 통상임금의 50%를 가산하여 지급합니다. 연장근로는 주 12시간 이내로 제한됩니다."},
    {"q": "야간근로 시간은?", "a": "야간근로는 22:00부터 익일 06:00까지입니다. 야간근로수당은 통상임금의 50%를 가산하여 지급합니다."},
    {"q": "선택적 출근 가능해?", "a": "네, 업무 특성에 따라 08:30~10:30 사이 선택적 출근을 승인받을 수 있습니다."},
    {"q": "개발팀 연장근로 한도는?", "a": "개발 직군은 집중개발기간(최대 4주) 중 연장근로 한도가 주 16시간까지 확대됩니다. 종료 후 대체휴가가 부여됩니다."},
    {"q": "임신 중 근무시간 단축 가능해?", "a": "네, 임신 12주 이내 또는 36주 이후 근로자는 1일 2시간 단축근무를 신청할 수 있습니다."},
    {"q": "육아기 근로시간 단축은?", "a": "만 8세 이하 자녀를 둔 직원은 주 15~35시간 범위에서 육아기 근로시간 단축을 신청할 수 있습니다."},
    {"q": "계약직 연장근로 가능해?", "a": "계약직 및 인턴은 연장근로 대상에서 제외됩니다. 불가피한 경우 본인 서면 동의 후 주 8시간 이내에서만 허용됩니다."},
    {"q": "교대근무 수당은?", "a": "고객지원 직군 야간조 근무 시 야간근로수당 외 교대수당 일 2만 원이 추가 지급됩니다."},
    {"q": "관리자 연장근로수당은?", "a": "부서장 이상 관리자는 재량근무제가 적용되어 연장근로수당 대신 직책수당으로 보상받습니다."},
    {"q": "휴게시간은 얼마야?", "a": "휴게시간은 직원의 건강과 업무 효율 향상을 위해 근무 일정 중 부여됩니다. 부서별로 조정될 수 있습니다."},
    {"q": "업무 집중시간이 뭐야?", "a": "회사가 지정한 특정 시간대로, 이 시간에는 불필요한 회의, 잡무, 외부 업무 배치를 최소화합니다."},
    {"q": "장애인 근무시간 조정 가능해?", "a": "네, 장애 유형 및 정도에 따라 출퇴근 시간 유연 적용 및 휴게시간 추가 부여가 가능합니다."},
    {"q": "통상임금이 뭐야?", "a": "통상임금은 연장·야간·휴일근로수당 등을 산정할 때 기준이 되는 임금입니다."},

    # 휴가 관련 (25개)
    {"q": "연차휴가 며칠이야?", "a": "입사 첫해는 월 1일씩 최대 11일, 1년 이상 근속 시 15일입니다. 3년차부터 2년마다 1일씩 추가되어 최대 25일까지 부여됩니다."},
    {"q": "병가 며칠 쓸 수 있어?", "a": "병가는 연 7일입니다. 3일 이상 사용 시 진단서를 제출해야 합니다."},
    {"q": "결혼휴가 며칠?", "a": "본인 결혼 시 5일의 유급휴가가 부여됩니다. 경조금 30만 원도 지급됩니다."},
    {"q": "배우자 출산휴가는?", "a": "배우자 출산 시 10일의 휴가가 부여됩니다. 분할 사용이 가능합니다(예: 5일+5일)."},
    {"q": "부모님 돌아가시면 휴가 며칠?", "a": "부모·배우자 부모 사망 시 5일의 유급휴가가 부여됩니다. 조의금 30만 원과 조화도 발송됩니다."},
    {"q": "연차 신청 언제까지 해야 해?", "a": "사용 예정일로부터 최소 3일 전 신청이 원칙입니다. 긴급 시 당일 오전 9시 이전 신청도 가능하나, 월 2회를 초과할 수 없습니다."},
    {"q": "연차 승인권자는 누구야?", "a": "3일 이하는 팀장, 4일 이상은 부서장 승인이 필요합니다. 10일 이상 연속 사용 시 본부장 사전 협의가 필요합니다."},
    {"q": "미사용 연차는 어떻게 돼?", "a": "회계연도 종료 시 미사용 연차는 연차수당으로 정산하거나, 익년도 상반기까지 이월 사용할 수 있습니다. 이월은 최대 5일로 제한됩니다."},
    {"q": "경조사 증빙서류는?", "a": "경조사 증빙서류(청첩장, 사망진단서 등)는 휴가 종료 후 3일 이내 제출해야 합니다. 미제출 시 연차로 대체 처리됩니다."},
    {"q": "수습 기간 연차 사용 가능해?", "a": "수습 기간(3개월) 중에도 월 1일의 연차가 발생하나, 수습 종료 전 사용은 부서장 승인이 필요합니다."},
    {"q": "계약직 연차는?", "a": "계약직은 계약 기간에 비례하여 연차가 부여됩니다. 1년 미만 계약 시 월 1일씩, 계약 종료 시 미사용분은 수당으로 정산됩니다."},
    {"q": "인턴 휴가는?", "a": "인턴은 월 0.5일의 유급휴가가 부여됩니다. 인턴십 기간 중 사용하지 못한 휴가는 소멸됩니다."},
    {"q": "임신 중 특별휴가는?", "a": "임신 중인 직원에게는 월 1일의 유급 산전검진휴가가 추가 부여됩니다. 임신 초기(12주 이내) 및 말기(36주 이후)에는 월 2일까지 확대됩니다."},
    {"q": "난임 치료 휴가 있어?", "a": "난임 치료를 받는 직원에게는 연 5일의 유급 난임치료휴가가 부여됩니다. 체외수정 등 고난도 시술의 경우 추가 2일이 부여될 수 있습니다."},
    {"q": "가족돌봄휴가는?", "a": "자녀, 부모, 배우자의 긴급한 질병·사고 시 연 10일의 가족돌봄휴가를 사용할 수 있으며, 이 중 5일은 유급입니다."},
    {"q": "리프레시휴가 뭐야?", "a": "5년 이상 근속자에게 5년 단위로 5일의 리프레시휴가가 추가 부여됩니다. 연차와 별도로 운영됩니다."},
    {"q": "재해 시 특별휴가는?", "a": "본인 또는 직계가족이 자연재해, 화재 등 재난 피해를 입은 경우 최대 5일의 특별휴가가 부여됩니다."},
    {"q": "휴가 취소 가능해?", "a": "승인된 휴가의 취소 또는 일정 변경은 사용 예정일 전일까지 시스템에서 처리 가능합니다. 당일 취소는 부서장 승인이 필요합니다."},
    {"q": "휴가 중 업무 연락 받으면?", "a": "휴가 중 긴급 업무 연락은 최소화하며, 불가피하게 업무 처리가 필요한 경우 해당 시간만큼 대체휴가가 부여됩니다."},
    {"q": "자녀 결혼 휴가는?", "a": "자녀 결혼 시 1일의 휴가가 부여됩니다."},
    {"q": "해외 거주 부모 사망 시 추가 휴가?", "a": "해외 거주 부모 사망으로 추가 휴가가 필요한 경우 특별 심사 후 최대 3일 추가 승인이 가능합니다."},
    {"q": "육아휴직 기간은?", "a": "육아휴직은 법령에 따르며, 만 8세 이하 자녀를 양육하기 위해 신청할 수 있습니다."},
    {"q": "질병휴직 기간은?", "a": "질병휴직은 최대 3개월까지 가능합니다. 1개월 초과 사용 시 의료기관 진단서를 제출해야 합니다."},
    {"q": "학업휴직 가능해?", "a": "학업·개인 사유 휴직은 회사 승인 하에 6개월까지 허용될 수 있습니다."},
    {"q": "안식휴가 뭐야?", "a": "장기 근속자에게 재충전 기회를 제공하기 위해 부여하는 장기 유급휴가입니다."},

    # 근태 관련 (15개)
    {"q": "지각 기준은?", "a": "지각은 정해진 출근시간보다 늦게 출근하는 것으로, 15분 이상 지연 시 1회로 산정합니다."},
    {"q": "지각 많이 하면 어떻게 돼?", "a": "월 3회 초과 시 근태 안내가 제공되며, 월 6회 이상이면 인사부서 면담을 진행합니다."},
    {"q": "출퇴근 기록 누락하면?", "a": "출퇴근 기록 누락 시 1회당 근무시간 20분이 차감됩니다. 48시간 내 정정 요청 시 차감이 면제됩니다."},
    {"q": "무단결근하면?", "a": "무단결근은 급여에서 일 단위로 공제되며, 2일 연속 발생 시 서면 경위서를 제출해야 합니다."},
    {"q": "대중교통 지연으로 지각하면?", "a": "운행 중단 증빙(캡처 등) 제출 시 지각이 면제될 수 있습니다."},
    {"q": "조퇴 기준은?", "a": "조퇴는 정해진 퇴근시간 이전에 업무를 종료하고 퇴근하는 것으로, 15분 이상을 1회로 산정합니다."},
    {"q": "결근 종류는?", "a": "결근은 사전 승인 여부에 따라 유급/무급/무단결근으로 구분됩니다."},
    {"q": "근태 기록은 어떻게 관리돼?", "a": "직원의 모든 출퇴근 기록은 회사 지정 시스템을 통해 관리되며, 인사평가의 기초 자료로 활용됩니다."},
    {"q": "근태 정정 요청은?", "a": "기록 누락이나 오류 발생 시 정정 요청은 정해진 절차를 따릅니다. 48시간 내 요청이 원칙입니다."},
    {"q": "부정 출퇴근 기록하면?", "a": "회사는 근태 신뢰성을 확보하기 위해 부정 기록 방지 장치를 운영합니다. 부정 기록은 징계 사유가 됩니다."},
    {"q": "재택근무 출퇴근 기록은?", "a": "재택 시에도 근무시간은 본사 근무와 동일하게 적용되며, 시스템을 통해 기록해야 합니다."},
    {"q": "연속 지각 2회 이상이면?", "a": "연속 지각 2회 이상이면 인사부서에서 별도 관리하며, 개선되지 않으면 면담이 진행됩니다."},
    {"q": "결근자 급여 공제는?", "a": "무단결근은 급여에서 일 단위로 공제됩니다. 정당한 사유가 있는 경우 별도 심사를 거칩니다."},
    {"q": "출근율은 어떻게 계산해?", "a": "출근율은 (출근일 / 근무해야 할 일수) × 100으로 계산됩니다. 인사평가에 반영될 수 있습니다."},
    {"q": "야근하면 기록해야 해?", "a": "야간근로(22:00 이후 퇴근)는 별도 기록되며, 야간근로수당 산정의 근거가 됩니다."},

    # 재택근무/원격근무 (10개)
    {"q": "재택근무 가능해?", "a": "재택근무는 자율 출근제와 병행하여 운영되며, 팀별 협의에 따라 유연하게 조정할 수 있습니다."},
    {"q": "재택근무 장비 지원은?", "a": "회사는 재택근무 환경 구축을 위해 입사 시 장비 세팅비 50만 원을 일시 지원합니다."},
    {"q": "워케이션이 뭐야?", "a": "Work(업무)와 Vacation(휴가)의 합성어로, 휴양지 등에서 업무와 휴식을 병행하는 근무 형태입니다."},
    {"q": "재택근무 시 근무시간은?", "a": "재택 시 근무시간은 본사 근무와 동일하게 적용됩니다. 출퇴근 기록도 시스템에 해야 합니다."},
    {"q": "재택근무 환경 요건은?", "a": "직원은 업무 수행이 가능한 환경을 확보해야 합니다. 인터넷 연결, 보안 환경 등이 필요합니다."},
    {"q": "VPN이 뭐야?", "a": "Virtual Private Network의 약자로, 외부에서 사내망에 안전하게 접속하기 위한 가상 사설망입니다."},
    {"q": "재택근무 승인은?", "a": "재택근무는 팀별 협의에 따라 운영되며, 부서장 승인이 필요할 수 있습니다."},
    {"q": "재택근무 중 보안 규칙은?", "a": "재택근무 시에도 회사의 보안 규칙을 준수해야 합니다. VPN 사용, 기밀자료 관리 등이 적용됩니다."},
    {"q": "재택근무 빈도 제한 있어?", "a": "재택근무 빈도는 팀별 협의에 따라 결정되며, 업무 특성에 따라 조정될 수 있습니다."},
    {"q": "원격근무와 재택근무 차이는?", "a": "재택근무는 자택에서, 원격근무는 사무실 외 장소(카페, 공유오피스 등)에서 근무하는 것을 포함합니다."},

    # 평가/보상 관련 (15개)
    {"q": "평가 방식은?", "a": "평가는 정량평가(매출, 목표 달성률 등)와 정성평가(협업 태도, 조직 기여도 등)로 구성됩니다."},
    {"q": "다면평가가 뭐야?", "a": "다면평가는 상급자뿐 아니라 동료, 하급자 등 다양한 평가자가 참여하는 평가 방식입니다."},
    {"q": "KPI가 뭐야?", "a": "Key Performance Indicator의 약자로, 개인 또는 조직의 성과를 측정하는 핵심 지표입니다."},
    {"q": "OKR이 뭐야?", "a": "Objectives and Key Results의 약자로, 목표(O)와 핵심 결과(KR)를 설정하여 관리하는 성과 관리 방식입니다."},
    {"q": "PIP가 뭐야?", "a": "Performance Improvement Program의 약자로, 저성과자의 성과 개선을 지원하는 프로그램입니다."},
    {"q": "기본급은 어떻게 정해져?", "a": "기본급은 직무 등급과 경력에 따라 책정되는 고정 급여입니다."},
    {"q": "성과급은?", "a": "성과급은 평가 결과 및 회사 실적에 따라 차등 지급되는 변동 급여입니다."},
    {"q": "복지포인트 뭐야?", "a": "회사가 직원에게 부여하는 선택적 복리후생 비용으로, 지정된 항목 내에서 자유롭게 사용할 수 있습니다."},
    {"q": "평가 시기는?", "a": "평가는 분기별로 진행되며, 연말에 연간 종합 평가가 이루어집니다."},
    {"q": "평가 결과 이의신청 가능해?", "a": "평가 결과에 이의가 있는 경우 정해진 절차에 따라 이의신청이 가능합니다."},
    {"q": "승진 기준은?", "a": "승진은 평가 결과, 근속 연수, 직무 역량 등을 종합적으로 고려하여 인사위원회에서 심의합니다."},
    {"q": "연봉 협상 가능해?", "a": "연봉은 회사의 임금 체계에 따라 결정되며, 개별 협상 가능 여부는 회사 정책에 따릅니다."},
    {"q": "직무등급이 뭐야?", "a": "직무의 난이도, 책임 범위 등에 따라 분류한 등급으로, 보상 산정의 기준이 됩니다."},
    {"q": "인사위원회가 뭐야?", "a": "채용, 승진, 징계 등 주요 인사 사항을 심의·의결하는 기구입니다."},
    {"q": "평가 피드백은 어떻게 받아?", "a": "평가 후 상급자와 1:1 면담을 통해 피드백을 받으며, 개선 방향을 논의합니다."},

    # 징계/보안 관련 (10개)
    {"q": "징계 종류는?", "a": "징계는 경고, 주의, 감봉, 정직, 면직(해고) 순으로 중징계로 분류됩니다."},
    {"q": "경고 처분이 뭐야?", "a": "경고는 위반 행위에 대한 주의를 환기시키는 가장 경미한 징계입니다."},
    {"q": "감봉 처분은?", "a": "감봉은 일정 기간 급여의 일부를 감액하는 징계입니다."},
    {"q": "정직 처분은?", "a": "정직은 일정 기간 출근을 정지하고 급여를 지급하지 않는 징계입니다."},
    {"q": "징계위원회가 뭐야?", "a": "직원의 징계 사안을 심의·의결하는 기구입니다."},
    {"q": "기밀등급 분류는?", "a": "정보의 중요도에 따라 A(최고기밀), B(기밀), C(대외비), D(일반)로 구분합니다."},
    {"q": "MFA가 뭐야?", "a": "Multi-Factor Authentication의 약자로, 비밀번호 외 추가 인증 수단을 요구하는 보안 방식입니다."},
    {"q": "외부 저장장치 사용 가능해?", "a": "외부 저장장치 사용은 보안 규칙에 따라 제한될 수 있습니다. 승인이 필요할 수 있습니다."},
    {"q": "사적 계정 연동 가능해?", "a": "사적 계정 연동은 보안상 제한될 수 있습니다. 회사 정보 보안 규칙을 따라야 합니다."},
    {"q": "보안 위반 시 처벌은?", "a": "보안 규칙 위반 시 위반 정도에 따라 경고부터 면직까지 징계가 부과될 수 있습니다."},

    # 휴직 관련 (10개)
    {"q": "휴직 신청 자격은?", "a": "정규직 직원으로서 재직 기간 6개월 이상인 자가 신청할 수 있습니다. 단, 육아휴직은 재직 기간과 무관합니다."},
    {"q": "휴직 신청 기한은?", "a": "휴직 예정일로부터 최소 30일 전 신청이 원칙입니다. 질병휴직은 긴급 시 사후 7일 이내 신청이 가능합니다."},
    {"q": "휴직 필요 서류는?", "a": "휴직 신청서, 휴직 사유 증빙서류(진단서, 입학허가서 등), 업무 인수인계 계획서가 필요합니다."},
    {"q": "휴직 승인권자는?", "a": "1개월 이하는 부서장, 1~3개월은 본부장, 3개월 초과는 인사위원회 승인이 필요합니다."},
    {"q": "휴직 중 의무는?", "a": "휴직 기간 중 월 1회 현황 보고를 제출해야 하며, 연락처 변경 시 즉시 인사팀에 통보해야 합니다."},
    {"q": "복귀 절차는?", "a": "복귀 예정일 14일 전까지 복귀 신청서를 제출하고, 복귀 전 건강검진(질병휴직) 또는 면담을 실시합니다."},
    {"q": "휴직 중 다른 곳에서 일하면?", "a": "휴직 기간 중 타 기관 취업이 확인되면 즉시 면직 처리될 수 있습니다."},
    {"q": "휴직 후 복귀 안 하면?", "a": "정당한 사유 없이 복귀하지 않을 경우 무단결근으로 처리됩니다."},
    {"q": "휴직 중 급여는?", "a": "휴직 종류에 따라 급여 및 복리후생 유지 여부가 다릅니다. 육아휴직은 고용보험에서 급여가 지급됩니다."},
    {"q": "휴직 연장 가능해?", "a": "휴직 연장은 사유에 따라 가능할 수 있으며, 연장 신청 절차를 따라야 합니다."},
]


def create_sharegpt_format(question: str, answer: str) -> dict:
    """ShareGPT 형식으로 변환"""
    return {
        "conversations": [
            {"role": "user", "content": question},
            {"role": "assistant", "content": answer}
        ]
    }


def main():
    # SQL 데이터셋 생성
    sql_dataset = [
        create_sharegpt_format(item["q"], item["sql"])
        for item in SQL_DATA
    ]

    # RAG 데이터셋 생성
    rag_dataset = [
        create_sharegpt_format(item["q"], item["a"])
        for item in RAG_DATA
    ]

    # 통합 데이터셋
    combined_dataset = sql_dataset + rag_dataset

    # 파일 저장
    with open(OUTPUT_DIR / "sql_train.json", "w", encoding="utf-8") as f:
        json.dump(sql_dataset, f, ensure_ascii=False, indent=2)
    print(f"SQL 데이터셋 저장: {len(sql_dataset)}개")

    with open(OUTPUT_DIR / "rag_train.json", "w", encoding="utf-8") as f:
        json.dump(rag_dataset, f, ensure_ascii=False, indent=2)
    print(f"RAG 데이터셋 저장: {len(rag_dataset)}개")

    with open(OUTPUT_DIR / "combined_train.json", "w", encoding="utf-8") as f:
        json.dump(combined_dataset, f, ensure_ascii=False, indent=2)
    print(f"통합 데이터셋 저장: {len(combined_dataset)}개")

    print(f"\n저장 위치: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
