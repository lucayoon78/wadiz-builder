import React, { useState, useEffect } from 'react';
import { Plus, Search, Filter, Grid3x3, List, MoreVertical } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { api } from '../lib/api';
import { useNavigate } from 'react-router-dom';

interface Project {
  id: number;
  project_name: string;
  product_name: string;
  platform?: string;
  created_at: string;
  updated_at: string;
  status?: string;
}

export const DashboardPage: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const navigate = useNavigate();

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      setLoading(true);
      const response = await api.get('/projects');
      setProjects(response.data);
    } catch (error) {
      console.error('프로젝트 로딩 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredProjects = projects.filter((project) =>
    project.project_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    project.product_name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getPlatformBadge = (platform?: string) => {
    const platformMap: { [key: string]: { label: string; variant: 'default' | 'success' | 'warning' | 'error' } } = {
      wadiz: { label: '와디즈', variant: 'default' },
      smartstore: { label: '스마트스토어', variant: 'success' },
      coupang: { label: '쿠팡', variant: 'warning' },
      gmarket: { label: 'G마켓', variant: 'error' },
    };
    const platformInfo = platformMap[platform || 'wadiz'] || { label: platform || '와디즈', variant: 'default' as const };
    return <Badge variant={platformInfo.variant}>{platformInfo.label}</Badge>;
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return '방금 전';
    if (diffMins < 60) return `${diffMins}분 전`;
    if (diffHours < 24) return `${diffHours}시간 전`;
    if (diffDays < 7) return `${diffDays}일 전`;
    return date.toLocaleDateString('ko-KR');
  };

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* 헤더 */}
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <h1 className="text-4xl font-bold tracking-tight">프로젝트</h1>
            <p className="text-muted-foreground">
              {projects.length}개의 프로젝트를 관리하고 있습니다
            </p>
          </div>
          <Button
            size="lg"
            className="gap-2"
            onClick={() => navigate('/create')}
          >
            <Plus className="h-5 w-5" />
            새 프로젝트
          </Button>
        </div>

        {/* 검색 및 필터 */}
        <div className="flex items-center gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-muted-foreground" />
            <Input
              type="text"
              placeholder="프로젝트 이름 또는 제품명으로 검색..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
          <Button variant="secondary" className="gap-2">
            <Filter className="h-5 w-5" />
            필터
          </Button>
          <div className="flex items-center gap-2 bg-secondary rounded-lg p-1">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded transition-colors ${
                viewMode === 'grid' ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              <Grid3x3 className="h-5 w-5" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded transition-colors ${
                viewMode === 'list' ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              <List className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* 프로젝트 그리드 */}
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
          </div>
        ) : filteredProjects.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-64 space-y-4">
            <div className="text-6xl">📦</div>
            <h3 className="text-xl font-semibold">프로젝트가 없습니다</h3>
            <p className="text-muted-foreground">새 프로젝트를 만들어 시작하세요</p>
            <Button onClick={() => navigate('/create')} className="gap-2">
              <Plus className="h-5 w-5" />
              첫 프로젝트 만들기
            </Button>
          </div>
        ) : (
          <div
            className={
              viewMode === 'grid'
                ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'
                : 'space-y-4'
            }
          >
            {filteredProjects.map((project) => (
              <Card
                key={project.id}
                hoverable
                className="animate-fade-in"
                onClick={() => navigate(`/project/${project.id}`)}
              >
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="space-y-1 flex-1">
                      <CardTitle className="text-lg line-clamp-1">
                        {project.project_name}
                      </CardTitle>
                      <CardDescription className="line-clamp-1">
                        {project.product_name}
                      </CardDescription>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        // 메뉴 열기 로직
                      }}
                      className="p-2 hover:bg-secondary rounded-lg transition-colors"
                    >
                      <MoreVertical className="h-5 w-5" />
                    </button>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-2">
                    {getPlatformBadge(project.platform)}
                    <span className="text-sm text-muted-foreground">
                      {formatDate(project.updated_at)}
                    </span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
