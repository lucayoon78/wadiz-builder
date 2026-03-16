import React, { useState, useEffect } from 'react';
import { ArrowLeft, Download, Eye, Share2, Settings, Code } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { api } from '../lib/api';
import { useNavigate, useParams } from 'react-router-dom';

interface Project {
  id: number;
  project_name: string;
  product_name: string;
  platform?: string;
  html_content?: string;
  created_at: string;
}

export const ProjectDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [previewMode, setPreviewMode] = useState<'desktop' | 'tablet' | 'mobile'>('desktop');
  const [showExportModal, setShowExportModal] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    loadProject();
  }, [id]);

  const loadProject = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/projects/${id}`);
      setProject(response.data);
    } catch (error) {
      console.error('프로젝트 로딩 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (platform: string) => {
    try {
      const response = await api.post('/multi-platform/multi-platform-export', {
        project_id: parseInt(id!),
        platforms: [platform],
        generate_thumbnails: true,
        generate_gifs: true,
      });
      
      // 다운로드 처리
      const blob = new Blob([response.data.exports[0].html_content], { type: 'text/html' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${project?.project_name}-${platform}.html`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('내보내기 실패:', error);
      alert('내보내기에 실패했습니다.');
    }
  };

  const previewWidths = {
    desktop: '100%',
    tablet: '768px',
    mobile: '375px',
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="text-6xl">😢</div>
          <h2 className="text-2xl font-bold">프로젝트를 찾을 수 없습니다</h2>
          <Button onClick={() => navigate('/dashboard')}>대시보드로 돌아가기</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* 상단 툴바 */}
      <div className="border-b border-white/10 bg-card sticky top-0 z-50">
        <div className="flex items-center justify-between px-6 py-4">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/dashboard')}
              className="p-2 hover:bg-secondary rounded-lg transition-colors"
            >
              <ArrowLeft className="h-5 w-5" />
            </button>
            <div>
              <h1 className="font-semibold">{project.project_name}</h1>
              <p className="text-sm text-muted-foreground">{project.product_name}</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* 프리뷰 모드 */}
            <div className="flex items-center gap-2 bg-secondary rounded-lg p-1">
              {[
                { mode: 'desktop' as const, label: '🖥️', width: '100%' },
                { mode: 'tablet' as const, label: '📱', width: '768px' },
                { mode: 'mobile' as const, label: '📱', width: '375px' },
              ].map((m) => (
                <button
                  key={m.mode}
                  onClick={() => setPreviewMode(m.mode)}
                  className={`px-4 py-2 rounded transition-colors text-sm font-medium ${
                    previewMode === m.mode
                      ? 'bg-primary text-primary-foreground'
                      : 'text-muted-foreground hover:text-foreground'
                  }`}
                >
                  {m.label}
                </button>
              ))}
            </div>

            <Button variant="secondary" className="gap-2">
              <Settings className="h-5 w-5" />
              설정
            </Button>

            <Button
              variant="primary"
              className="gap-2"
              onClick={() => setShowExportModal(true)}
            >
              <Download className="h-5 w-5" />
              내보내기
            </Button>
          </div>
        </div>
      </div>

      {/* 메인 컨텐츠 - 2컬럼 레이아웃 */}
      <div className="flex h-[calc(100vh-73px)]">
        {/* 좌측: 컨트롤 패널 */}
        <div className="w-80 border-r border-white/10 bg-card overflow-y-auto">
          <div className="p-6 space-y-6">
            <div className="space-y-2">
              <h3 className="font-semibold">프로젝트 정보</h3>
              <Card className="p-4 space-y-3 text-sm">
                <div>
                  <div className="text-muted-foreground mb-1">제품명</div>
                  <div className="font-medium">{project.product_name}</div>
                </div>
                <div>
                  <div className="text-muted-foreground mb-1">플랫폼</div>
                  <div className="font-medium capitalize">{project.platform || '와디즈'}</div>
                </div>
                <div>
                  <div className="text-muted-foreground mb-1">생성일</div>
                  <div className="font-medium">{new Date(project.created_at).toLocaleDateString('ko-KR')}</div>
                </div>
              </Card>
            </div>

            <div className="space-y-2">
              <h3 className="font-semibold">빠른 작업</h3>
              <div className="space-y-2">
                <Button variant="secondary" className="w-full justify-start gap-2">
                  <Code className="h-5 w-5" />
                  HTML 코드 보기
                </Button>
                <Button variant="secondary" className="w-full justify-start gap-2">
                  <Share2 className="h-5 w-5" />
                  공유하기
                </Button>
                <Button variant="secondary" className="w-full justify-start gap-2">
                  <Eye className="h-5 w-5" />
                  새 탭에서 열기
                </Button>
              </div>
            </div>

            <div className="space-y-2">
              <h3 className="font-semibold">내보내기 옵션</h3>
              <div className="space-y-2">
                {[
                  { platform: 'wadiz', label: '와디즈', emoji: '🚀' },
                  { platform: 'smartstore', label: '스마트스토어', emoji: '🛒' },
                  { platform: 'coupang', label: '쿠팡', emoji: '📦' },
                  { platform: 'gmarket', label: 'G마켓', emoji: '🏪' },
                ].map((p) => (
                  <button
                    key={p.platform}
                    onClick={() => handleExport(p.platform)}
                    className="w-full flex items-center gap-3 p-3 rounded-lg border border-white/10 hover:border-primary hover:bg-primary/5 transition-all text-left"
                  >
                    <span className="text-2xl">{p.emoji}</span>
                    <div className="flex-1">
                      <div className="font-medium">{p.label}</div>
                      <div className="text-xs text-muted-foreground">HTML 다운로드</div>
                    </div>
                    <Download className="h-5 w-5 text-muted-foreground" />
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* 우측: 라이브 프리뷰 */}
        <div className="flex-1 bg-muted/20 overflow-auto p-6">
          <div className="flex justify-center">
            <div
              className="bg-white rounded-lg shadow-2xl transition-all duration-300"
              style={{ width: previewWidths[previewMode], maxWidth: '100%' }}
            >
              {project.html_content ? (
                <iframe
                  srcDoc={project.html_content}
                  className="w-full border-0 rounded-lg"
                  style={{ height: '800px' }}
                  title="프리뷰"
                />
              ) : (
                <div className="h-96 flex items-center justify-center text-muted-foreground">
                  프리뷰를 불러올 수 없습니다
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* 내보내기 모달 (간단 버전) */}
      {showExportModal && (
        <div
          className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 animate-fade-in"
          onClick={() => setShowExportModal(false)}
        >
          <Card
            className="w-full max-w-md p-6 space-y-4 animate-scale-in"
            onClick={(e) => e.stopPropagation()}
          >
            <h2 className="text-2xl font-bold">플랫폼 선택</h2>
            <p className="text-muted-foreground">어느 플랫폼으로 내보낼까요?</p>
            <div className="space-y-2">
              {[
                { platform: 'wadiz', label: '와디즈', emoji: '🚀' },
                { platform: 'smartstore', label: '스마트스토어', emoji: '🛒' },
                { platform: 'coupang', label: '쿠팡', emoji: '📦' },
                { platform: 'gmarket', label: 'G마켓', emoji: '🏪' },
              ].map((p) => (
                <Button
                  key={p.platform}
                  variant="secondary"
                  className="w-full justify-start gap-3"
                  onClick={() => {
                    handleExport(p.platform);
                    setShowExportModal(false);
                  }}
                >
                  <span className="text-2xl">{p.emoji}</span>
                  {p.label}
                </Button>
              ))}
            </div>
            <Button
              variant="ghost"
              className="w-full"
              onClick={() => setShowExportModal(false)}
            >
              취소
            </Button>
          </Card>
        </div>
      )}
    </div>
  );
};
