from typing import Dict, Any
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import engine, get_db, Base
from app.models.analysis import Analysis
from app.services.crawler_service import fetch_html
from app.services.analysis_service import analyze_html

# 테이블 생성
Base.metadata.create_all(bind=engine)


# --- Models ---

class AnalyzeRequest(BaseModel):
    url: str


class AnalyzeResponse(BaseModel):
    id: int
    success: bool
    url: str
    html_length: int
    tag_counts: Dict[str, int]
    keyword_frequency: Dict[str, int]
    link_stats: Dict[str, Any]
    image_stats: Dict[str, Any]
    text_stats: Dict[str, Any]
    dom_depth: int


class HistoryResponse(BaseModel):
    id: int
    url: str
    created_at: str


# --- App ---

app = FastAPI(
    title="Simple GEO",
    description="URL 입력 → HTML 크롤링 → CPU 분석 (부하테스트용)",
    version="2.0.0"
)


# --- Routes ---

@app.get("/health")
async def health_check():
    """헬스체크"""
    return {"status": "healthy"}


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze_url(request: AnalyzeRequest, db: Session = Depends(get_db)):
    """URL의 HTML을 크롤링하고 CPU 집약적 분석 수행"""

    # 1. HTML 크롤링 (I/O 부하)
    try:
        html = await fetch_html(request.url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"URL 크롤링 실패: {str(e)}")

    # 2. CPU 집약적 분석 (CPU 부하)
    try:
        result = analyze_html(html, request.url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"분석 실패: {str(e)}")

    # 3. DB에 저장 (DB 부하)
    analysis = Analysis(
        url=result["url"],
        html_length=result["html_length"],
        tag_counts=result["tag_counts"],
        keyword_frequency=result["keyword_frequency"],
        link_stats=result["link_stats"],
        image_stats=result["image_stats"],
        text_stats=result["text_stats"],
        dom_depth=result["dom_depth"]
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    return AnalyzeResponse(
        id=analysis.id,
        success=True,
        url=analysis.url,
        html_length=analysis.html_length,
        tag_counts=analysis.tag_counts,
        keyword_frequency=analysis.keyword_frequency,
        link_stats=analysis.link_stats,
        image_stats=analysis.image_stats,
        text_stats=analysis.text_stats,
        dom_depth=analysis.dom_depth
    )


@app.get("/api/history")
async def get_history(db: Session = Depends(get_db)):
    """분석 히스토리 조회"""
    analyses = db.query(Analysis).order_by(Analysis.created_at.desc()).limit(20).all()
    return [
        HistoryResponse(
            id=a.id,
            url=a.url,
            created_at=a.created_at.isoformat()
        )
        for a in analyses
    ]


@app.get("/api/analysis/{analysis_id}", response_model=AnalyzeResponse)
async def get_analysis(analysis_id: int, db: Session = Depends(get_db)):
    """특정 분석 결과 조회"""
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="분석 결과를 찾을 수 없습니다")

    return AnalyzeResponse(
        id=analysis.id,
        success=True,
        url=analysis.url,
        html_length=analysis.html_length,
        tag_counts=analysis.tag_counts,
        keyword_frequency=analysis.keyword_frequency,
        link_stats=analysis.link_stats,
        image_stats=analysis.image_stats,
        text_stats=analysis.text_stats,
        dom_depth=analysis.dom_depth
    )
