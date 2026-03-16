import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, 
  Download, 
  Eye, 
  Code, 
  RefreshCw, 
  Share2,
  Sparkles,
  Save
} from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { api } from '../lib/api';
import { useToast } from '../hooks/useToast';
import type { Project } from '../types';

export const ProjectDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();
  
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState<'preview' | 'code'>('preview');
  const [showExportModal, setShowExportModal] = useState(false);

  useEffect(() => {
    if (id) {
      loadProject(parseInt(id));
    }
  }, [id]);

  const loadProject = async (projectId: number) => {
    try {
      setLoading(true);
      const data = await api.getProjects();
      const found = data.find((p: Project) => p.id === projectId);
      if (found) {
        setProject(found);
      } else {
        throw new Error('프로젝트를 찾을 수 없습니다');
      }
    } catch (error) {
      console.error('프로젝트 로딩 실패:', error);
      toast({
        title: '로딩 실패',
        description: '프로젝트를 불러올 수 없습니다.',
        variant: 'destructive'
      });
      navigate('/dashboard');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (format: 'html' | 'pdf' | 'json') => {
    if (!project) return;
    
    try {
      const blob = await api.exportProject(project.id, format);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${project.project_name}.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      toast({
        title: '내보내기 완료',
        description: `${format.toUpperCase()} 파일이 다운로드되었습니다.`,
        variant: 'default'
      });
      setShowExportModal(false);
    } catch (error) {
      console.error('내보내기 실패:', error);
      toast({
        title: '내보내기 실패',
        description: '파일을 생성할 수 없습니다.',
        variant: 'destructive'
      });
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="flex flex-col items-center justify-center h-screen">
        <p className="text-xl text-muted-foreground mb-4">프로젝트를 찾을 수 없습니다</p>
        <Button onClick={() => navigate('/dashboard')}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          대시보드로 돌아가기
        </Button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* 헤더 */}
      <div className="border-b bg-card">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => navigate('/dashboard')}
              >
                <ArrowLeft className="h-5 w-5" />
              </Button>
              <div>
                <h1 className="text-2xl font-bold">{project.project_name}</h1>
                <p className="text-sm text-muted-foreground">
                  {project.platform === 'wadiz' && '와디즈'}
                  {project.platform === 'smartstore' && '스마트스토어'}
                  {project.platform === 'coupang' && '쿠팡'}
                  프로젝트
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                onClick={() => setViewMode(viewMode === 'preview' ? 'code' : 'preview')}
              >
                {viewMode === 'preview' ? (
                  <>
                    <Code className="mr-2 h-4 w-4" />
                    코드 보기
                  </>
                ) : (
                  <>
                    <Eye className="mr-2 h-4 w-4" />
                    미리보기
                  </>
                )}
              </Button>
              <Button
                variant="outline"
                onClick={() => setShowExportModal(true)}
              >
                <Download className="mr-2 h-4 w-4" />
                내보내기
              </Button>
              <Button>
                <Sparkles className="mr-2 h-4 w-4" />
                AI 리뉴얼
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* 컨텐츠 영역 */}
      <div className="container mx-auto px-6 py-8">
        <Card>
          <CardContent className="p-6">
            {viewMode === 'preview' ? (
              <div 
                className="prose max-w-none"
                dangerouslySetInnerHTML={{ __html: project.generated_html || '<p>생성된 HTML이 없습니다</p>' }}
              />
            ) : (
              <pre className="bg-muted p-4 rounded-lg overflow-x-auto">
                <code>{project.generated_html || '// 생성된 코드가 없습니다'}</code>
              </pre>
            )}
          </CardContent>
        </Card>
      </div>

      {/* 내보내기 모달 */}
      {showExportModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle>내보내기 형식 선택</CardTitle>
              <CardDescription>
                원하는 형식으로 프로젝트를 내보낼 수 있습니다
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button
                variant="outline"
                className="w-full justify-start"
                onClick={() => handleExport('html')}
              >
                <Code className="mr-2 h-4 w-4" />
                HTML 파일로 내보내기
              </Button>
              <Button
                variant="outline"
                className="w-full justify-start"
                onClick={() => handleExport('pdf')}
              >
                <Download className="mr-2 h-4 w-4" />
                PDF 파일로 내보내기
              </Button>
              <Button
                variant="outline"
                className="w-full justify-start"
                onClick={() => handleExport('json')}
              >
                <Save className="mr-2 h-4 w-4" />
                JSON 데이터로 내보내기
              </Button>
              <Button
                variant="ghost"
                className="w-full"
                onClick={() => setShowExportModal(false)}
              >
                취소
              </Button>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default ProjectDetailPage;
