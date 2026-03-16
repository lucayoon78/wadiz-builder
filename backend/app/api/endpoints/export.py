"""
HTML Export endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.schemas import HTMLExportRequest, HTMLExportResponse
from app.services.export_service import ExportService
from app.services.auth_service import get_current_user
from app.models.models import User

router = APIRouter()


@router.post("/html", response_model=HTMLExportResponse)
async def export_html(
    request: HTMLExportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    프로젝트를 HTML로 export (ZIP 파일)
    
    - 와디즈 황금 구조로 생성된 HTML
    - 모든 이미지 포함
    - CSS 인라인 스타일 적용
    - 모바일 반응형
    """
    export_service = ExportService(db)
    
    # Verify project ownership
    from app.services.project_service import ProjectService
    project_service = ProjectService(db)
    project = await project_service.get_project(request.project_id)
    
    if not project or project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    
    try:
        result = await export_service.export_to_html(
            request.project_id,
            request.template_id,
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Export failed: {str(e)}",
        )


@router.get("/download/{file_key}")
async def download_html(
    file_key: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """HTML ZIP 파일 다운로드"""
    export_service = ExportService(db)
    
    try:
        file_path = await export_service.get_export_file(file_key)
        return FileResponse(
            path=file_path,
            media_type="application/zip",
            filename=f"wadiz-page-{file_key}.zip",
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found or expired",
        )
