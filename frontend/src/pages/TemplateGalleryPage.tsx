import React, { useState, useEffect } from 'react';
import { Search, Star, TrendingUp, Clock, Eye } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { api } from '../lib/api';
import { useNavigate } from 'react-router-dom';

interface TemplateCategory {
  id: number;
  name: string;
  display_name: string;
  description: string;
  icon_emoji: string;
}

interface Template {
  id: number;
  name: string;
  description: string;
  category_id: number;
  category_name?: string;
  preview_image_url?: string;
  thumbnail_url?: string;
  success_rate: number;
  usage_count: number;
  avg_funding_amount: number;
  color_scheme?: any;
}

export const TemplateGalleryPage: React.FC = () => {
  const [categories] = useState<TemplateCategory[]>([]);
  const [templates, setTemplates] = useState<Template[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<'popular' | 'success' | 'recent'>('popular');
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const templatesData = await api.getTemplates();
      setTemplates(templatesData);
    } catch (error) {
      console.error('데이터 로딩 실패:', error);
      setTemplates([]);
    } finally {
      setLoading(false);
    }
  };

  const filteredTemplates = templates
    .filter((template) => {
      const matchesCategory = !selectedCategory || template.category_id === selectedCategory;
      const matchesSearch =
        template.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        template.description.toLowerCase().includes(searchQuery.toLowerCase());
      return matchesCategory && matchesSearch;
    })
    .sort((a, b) => {
      if (sortBy === 'popular') return b.usage_count - a.usage_count;
      if (sortBy === 'success') return b.success_rate - a.success_rate;
      return b.id - a.id;
    });

  const formatFundingAmount = (amount: number) => {
    if (amount >= 100000000) return `${(amount / 100000000).toFixed(1)}억`;
    if (amount >= 10000) return `${(amount / 10000).toFixed(0)}만`;
    return `${amount}`;
  };

  const selectTemplate = (template: Template) => {
    navigate('/create', { state: { templateId: template.id } });
  };

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto space-y-8">
        <div className="space-y-1">
          <h1 className="text-4xl font-bold tracking-tight">템플릿 갤러리</h1>
          <p className="text-muted-foreground">
            검증된 펀딩 성공 템플릿으로 빠르게 시작하세요
          </p>
        </div>

        <div className="flex items-center gap-3 overflow-x-auto pb-2">
          <button
            onClick={() => setSelectedCategory(null)}
            className={`px-6 py-3 rounded-lg font-medium transition-all whitespace-nowrap ${
              !selectedCategory
                ? 'bg-primary text-primary-foreground shadow-lg shadow-primary/50'
                : 'bg-secondary text-foreground hover:bg-secondary/80'
            }`}
          >
            전체
          </button>
          {categories.map((category) => (
            <button
              key={category.id}
              onClick={() => setSelectedCategory(category.id)}
              className={`px-6 py-3 rounded-lg font-medium transition-all whitespace-nowrap flex items-center gap-2 ${
                selectedCategory === category.id
                  ? 'bg-primary text-primary-foreground shadow-lg shadow-primary/50'
                  : 'bg-secondary text-foreground hover:bg-secondary/80'
              }`}
            >
              <span className="text-xl">{category.icon_emoji}</span>
              {category.display_name}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-muted-foreground" />
            <Input
              type="text"
              placeholder="템플릿 검색..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
          <div className="flex items-center gap-2 bg-secondary rounded-lg p-1">
            <button
              onClick={() => setSortBy('popular')}
              className={`px-4 py-2 rounded transition-colors text-sm font-medium flex items-center gap-2 ${
                sortBy === 'popular' ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              <TrendingUp className="h-4 w-4" />
              인기순
            </button>
            <button
              onClick={() => setSortBy('success')}
              className={`px-4 py-2 rounded transition-colors text-sm font-medium flex items-center gap-2 ${
                sortBy === 'success' ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              <Star className="h-4 w-4" />
              성공률순
            </button>
            <button
              onClick={() => setSortBy('recent')}
              className={`px-4 py-2 rounded transition-colors text-sm font-medium flex items-center gap-2 ${
                sortBy === 'recent' ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              <Clock className="h-4 w-4" />
              최신순
            </button>
          </div>
        </div>

        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredTemplates.map((template) => (
              <Card
                key={template.id}
                hoverable
                className="animate-fade-in overflow-hidden group"
              >
                <div
                  className="h-48 bg-gradient-to-br from-primary/20 via-accent/10 to-secondary/20 relative overflow-hidden"
                  style={template.color_scheme ? {
                    background: `linear-gradient(135deg, ${template.color_scheme.primary}20, ${template.color_scheme.accent}20)`
                  } : undefined}
                >
                  <div className="absolute inset-0 flex items-center justify-center text-6xl opacity-50">
                    {categories.find(c => c.id === template.category_id)?.icon_emoji || '📄'}
                  </div>
                  <div className="absolute inset-0 bg-black/0 group-hover:bg-black/60 transition-all flex items-center justify-center">
                    <Button
                      variant="primary"
                      className="opacity-0 group-hover:opacity-100 transform scale-95 group-hover:scale-100 transition-all"
                      onClick={() => selectTemplate(template)}
                    >
                      <Eye className="h-5 w-5 mr-2" />
                      미리보기
                    </Button>
                  </div>
                </div>

                <CardHeader>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Badge variant="default">
                        {categories.find(c => c.id === template.category_id)?.display_name || '일반'}
                      </Badge>
                      <Badge variant="success">
                        ✓ {template.success_rate}% 달성
                      </Badge>
                    </div>
                    <CardTitle className="text-lg">{template.name}</CardTitle>
                    <CardDescription className="line-clamp-2">
                      {template.description}
                    </CardDescription>
                  </div>
                </CardHeader>

                <CardContent>
                  <div className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-1 text-muted-foreground">
                      <TrendingUp className="h-4 w-4" />
                      평균 {formatFundingAmount(template.avg_funding_amount)}원
                    </div>
                    <div className="flex items-center gap-1 text-muted-foreground">
                      <Eye className="h-4 w-4" />
                      {template.usage_count}회 사용
                    </div>
                  </div>
                </CardContent>

                <CardFooter>
                  <Button
                    className="w-full"
                    onClick={() => selectTemplate(template)}
                  >
                    이 템플릿 사용하기
                  </Button>
                </CardFooter>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
