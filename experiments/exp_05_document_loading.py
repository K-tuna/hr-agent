# %%
# 셀 1: 환경 설정 및 라이브러리 임포트
"""
문서 로드 및 청킹 실험 (PDF)

목표:
- 회사 규정 PDF 문서 로드
- 텍스트 청킹 (chunk_size=500, overlap=50)
- 청크 확인
"""

import os
from pathlib import Path

# 프로젝트 루트 경로 설정
PROJECT_ROOT = Path(__file__).parent.parent
DOCS_PATH = PROJECT_ROOT / "data" / "company_docs" / "회사규정.pdf"

# 문서 존재 확인
if DOCS_PATH.exists():
    print(f"[OK] 문서 발견: {DOCS_PATH}")
    print(f"파일 크기: {DOCS_PATH.stat().st_size:,} bytes")
else:
    print(f"[ERROR] 문서 없음: {DOCS_PATH}")

# %%
# 셀 2: PDF 문서 로드
"""
PyPDFLoader를 사용해 PDF 파일 로드
"""

from langchain_community.document_loaders import PyPDFLoader

# PDF 로드
loader = PyPDFLoader(str(DOCS_PATH))
documents = loader.load()

print(f"[OK] PDF 로드 완료")
print(f"페이지 수: {len(documents)}")
print(f"첫 페이지 길이: {len(documents[0].page_content)} 글자")
print(f"\n--- 첫 페이지 미리보기 (처음 300자) ---")
print(documents[0].page_content[:300])

# %%
# 셀 3: 텍스트 청킹
"""
RecursiveCharacterTextSplitter로 문서를 작은 청크로 분할
- chunk_size: 500 (한 청크당 글자 수)
- chunk_overlap: 50 (청크 간 겹치는 글자 수)
"""

from langchain.text_splitter import RecursiveCharacterTextSplitter

# 청킹 설정
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    length_function=len,
    separators=["\n\n", "\n", " ", ""]
)

# 문서 청킹
chunks = text_splitter.split_documents(documents)

print(f"[OK] 청킹 완료")
print(f"원본 페이지 수: {len(documents)}")
print(f"생성된 청크 수: {len(chunks)}")
print(f"평균 청크 크기: {sum(len(c.page_content) for c in chunks) / len(chunks):.0f} 글자")

# %%
# 셀 4: 청크 내용 확인
"""
생성된 청크 샘플 확인
"""

# 첫 3개 청크 출력
print("=== 청크 샘플 (처음 3개) ===\n")
for i, chunk in enumerate(chunks[:3]):
    print(f"[청크 {i+1}] 길이: {len(chunk.page_content)} 글자")
    print(f"페이지: {chunk.metadata.get('page', 'N/A')}")
    print(f"내용:\n{chunk.page_content[:200]}...")
    print("-" * 60)

# 특정 키워드 포함 청크 찾기 (테스트)
keyword = "연차"
matching_chunks = [c for c in chunks if keyword in c.page_content]
print(f"\n'{keyword}' 포함 청크 수: {len(matching_chunks)}")

# %%
# 셀 5: 청크 통계 및 검증
"""
청크 크기 분포 확인
"""

# 청크 크기 분석
chunk_sizes = [len(c.page_content) for c in chunks]
min_size = min(chunk_sizes)
max_size = max(chunk_sizes)
avg_size = sum(chunk_sizes) / len(chunk_sizes)

print("=== 청크 크기 통계 ===")
print(f"최소: {min_size} 글자")
print(f"최대: {max_size} 글자")
print(f"평균: {avg_size:.0f} 글자")
print(f"총 청크 수: {len(chunks)}")

# 크기별 분포
size_ranges = {
    "0-200": len([s for s in chunk_sizes if s < 200]),
    "200-400": len([s for s in chunk_sizes if 200 <= s < 400]),
    "400-600": len([s for s in chunk_sizes if 400 <= s < 600]),
    "600+": len([s for s in chunk_sizes if s >= 600])
}

print("\n=== 크기별 분포 ===")
for range_name, count in size_ranges.items():
    print(f"{range_name}자: {count}개")

print("\n[OK] 문서 로드 및 청킹 완료!")
print(f"다음 단계: exp_06에서 FAISS 인덱스 생성")

# %%

