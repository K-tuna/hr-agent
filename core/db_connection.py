"""
DB 연결 헬퍼 모듈
SQLAlchemy를 사용해 MySQL에 연결합니다.
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()


class DatabaseConnection:
    """MySQL 데이터베이스 연결 관리 클래스"""
    
    def __init__(self):
        """환경변수에서 DB 정보를 읽어 연결 URL 생성"""
        self.host = os.getenv("MYSQL_HOST", "localhost")
        self.port = os.getenv("MYSQL_PORT", "3306")
        self.user = os.getenv("MYSQL_USER", "user")
        self.password = os.getenv("MYSQL_PASSWORD", "password")
        self.database = os.getenv("MYSQL_DATABASE", "enterprise_hr_db")
        
        # SQLAlchemy 연결 URL
        # 형식: mysql+pymysql://user:password@host:port/database
        self.connection_url = (
            f"mysql+pymysql://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.database}"
        )
        
        # SQLAlchemy 엔진 생성
        self.engine = create_engine(
            self.connection_url,
            echo=False,  # SQL 쿼리 로그 출력 (디버깅용)
            pool_pre_ping=True  # 연결 끊김 방지
        )
        
        # 세션 팩토리 생성
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def test_connection(self):
        """
        DB 연결 테스트
        Returns:
            bool: 연결 성공 시 True
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                print("✅ DB 연결 성공!")
                return True
        except Exception as e:
            print(f"❌ DB 연결 실패: {e}")
            return False
    
    def execute_query(self, query: str):
        """
        SQL 쿼리 실행 (SELECT 등)
        Args:
            query: 실행할 SQL 쿼리 문자열
        Returns:
            tuple: (결과 리스트, 에러 메시지)
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                rows = result.fetchall()
                columns = result.keys()
                
                # 결과를 딕셔너리 리스트로 변환
                results = []
                for row in rows:
                    results.append(dict(zip(columns, row)))
                
                return results, None
        except Exception as e:
            return None, str(e)
    
    def get_table_schema(self):
        """
        DB의 모든 테이블 스키마 정보 추출
        SQL Agent에서 Text-to-SQL 생성 시 사용
        Returns:
            str: 테이블 스키마 정보 (포맷팅된 문자열)
        """
        schema_info = []
        
        try:
            # 모든 테이블 목록 가져오기
            tables_query = """
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_SCHEMA = %s
            """ % f"'{self.database}'"
            
            with self.engine.connect() as conn:
                tables_result = conn.execute(text(tables_query))
                tables = [row[0] for row in tables_result.fetchall()]
                
                # 각 테이블의 컬럼 정보 가져오기
                for table in tables:
                    columns_query = f"""
                        SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_KEY
                        FROM INFORMATION_SCHEMA.COLUMNS
                        WHERE TABLE_SCHEMA = '{self.database}' 
                        AND TABLE_NAME = '{table}'
                        ORDER BY ORDINAL_POSITION
                    """
                    
                    columns_result = conn.execute(text(columns_query))
                    columns = columns_result.fetchall()
                    
                    # 테이블 스키마 포맷팅
                    schema_info.append(f"\nTable: {table}")
                    schema_info.append("-" * 50)
                    for col in columns:
                        col_name, data_type, nullable, key = col
                        key_info = f" [{key}]" if key else ""
                        schema_info.append(
                            f"  - {col_name} ({data_type}){key_info}"
                        )
            
            return "\n".join(schema_info)
        
        except Exception as e:
            return f"스키마 추출 실패: {e}"


# 싱글톤 인스턴스 (전역에서 재사용)
db = DatabaseConnection()


if __name__ == "__main__":
    """테스트 코드"""
    print("=" * 60)
    print("DB 연결 테스트 시작")
    print("=" * 60)
    
    # 1. 연결 테스트
    db.test_connection()
    
    print("\n" + "=" * 60)
    print("간단한 쿼리 실행")
    print("=" * 60)
    
    # 2. 간단한 쿼리 실행
    results, error = db.execute_query("SELECT * FROM departments")
    if error:
        print(f"❌ 에러: {error}")
    else:
        print("✅ 쿼리 성공!")
        for row in results:
            print(row)
    
    print("\n" + "=" * 60)
    print("스키마 정보 추출")
    print("=" * 60)
    
    # 3. 스키마 정보 출력
    schema = db.get_table_schema()
    print(schema)









