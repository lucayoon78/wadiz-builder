import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { ArrowLeft, Sparkles, FileText, Image as ImageIcon, Palette, Zap } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { api } from '../lib/api';
import { useToast } from '../hooks/useToast';
import type { Template } from '../types';

interface GenerateRequest {
  project_name: string;
  product_name: string;
  product_description: string;
  target_audience: string;
  key_features: string[];
  template_id?: number;
}

export const CreateProjectPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { toast } = useToast();
  
  const [templates, setTemplates] = useState<Template[]>([]);
  const [selectedTemplateId, setSelectedTemplateId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<GenerateRequest>({
    project_name: '',
    product_name: '',
    product_description: '',
    target_audience: '',
    key_features: ['']
  });

  useEffect(() => {
    loadTemplates();
    if (location.state?.templateId) {
      setSelectedTemplateId(location.state.templateId);
    }
  }, [location.state]);

  const loadTemplates = async () => {
    try {
      const data = await api.getTemplates();
      setTemplates(data);
    } catch (error) {
      console.error('템플릿 로딩 실패:', error);
      toast({
        title: '템플릿 로딩 실패',
        description: '템플릿 목록을 불러올 수 없습니다.',
        variant: 'destructive'
      });
    }
  };

  const handleFeatureChange = (index: number, value: string) => {
    const newFeatures = [...formData.key_features];
    newFeatures[index] = value;
    setFormData({ ...formData, key_features: newFeatures });
  };

  const addFeature = () => {
    if (formData.key_features.length < 10) {
      setFormData({ ...formData, key_features: [...formData.key_features, ''] });
    }
  };

  const removeFeature = (index: number) => {
    if (formData.key_features.length > 1) {
      const newFeatures = formData.key_features.filter((_, i) => i !== index);
      setFormData({ ...formData, key_features: newFeatures });
    }
  };

  const handleGenerate = async () => {
    if (!formData.project_name || !formData.product_name || !formData.product_description) {
      toast({
        title: '필수 항목을 입력해주세요',
        description: '프로젝트명, 제품명, 제품 설명은 필수입니다.',
        variant: 'destructive'
      });
      return;
    }

    try {
      setLoading(true);
      const payload = {
        ...formData,
        template_id: selectedTemplateId || undefined,
        key_features: formData.key_features.filter(f => f.trim() !== '')
      };
      
      const result = await api.generateWadizPage(payload);
      
      toast({
        title: '페이지 생성 완료!',
        description: 'AI가 와디즈 상세페이지를 생성했습니다.',
        variant: 'default'
      });
      
      navigate(`/project/${result.project_id}`);
    } catch (error: any) {
      console.error('생성 실패:', error);
      toast({
        title: '생성 실패',
        description: error.response?.data?.detail || '페이지 생성 중 오류가 발생했습니다.',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-4xl mx-auto">
        <Button
          variant="ghost"
          className="mb-6"
          onClick={() => navigate('/dashboard')}
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          돌아가기
        </Button>

        <div className="space-y-8">
          <div>
            <h1 className="text-4xl font-bold mb-2">새 프로젝트 만들기</h1>
            <p className="text-muted-foreground">
              AI가 와디즈 펀딩 상세페이지를 자동으로 생성해드립니다
            </p>
          </div>

          {/* 템플릿 선택 섹션 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Palette className="h-5 w-5" />
                템플릿 선택 (선택사항)
              </CardTitle>
              <CardDescription>
                성공한 펀딩 프로젝트의 레이아웃을 기반으로 생성합니다
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {templates.slice(0, 6).map((template) => (
                  <div
                    key={template.id}
                    className={`border-2 rounded-lg p-4 cursor-pointer transition-all hover:shadow-lg ${
                      selectedTemplateId === template.id
                        ? 'border-primary bg-primary/5'
                        : 'border-border'
                    }`}
                    onClick={() => setSelectedTemplateId(template.id)}
                  >
                    <div className="aspect-video bg-gradient-to-br from-primary/20 to-primary/5 rounded mb-3"></div>
                    <h4 className="font-semibold mb-1">{template.name}</h4>
                    <p className="text-sm text-muted-foreground line-clamp-2">
                      {template.description}
                    </p>
                    {selectedTemplateId === template.id && (
                      <Badge className="mt-2">선택됨</Badge>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* 프로젝트 정보 입력 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                프로젝트 정보
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  프로젝트명 <span className="text-destructive">*</span>
                </label>
                <Input
                  placeholder="예: 혁신적인 무선 이어폰 출시 프로젝트"
                  value={formData.project_name}
                  onChange={(e) => setFormData({ ...formData, project_name: e.target.value })}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  제품명 <span className="text-destructive">*</span>
                </label>
                <Input
                  placeholder="예: AirPods Ultra Pro"
                  value={formData.product_name}
                  onChange={(e) => setFormData({ ...formData, product_name: e.target.value })}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  제품 설명 <span className="text-destructive">*</span>
                </label>
                <textarea
                  className="w-full min-h-[120px] rounded-md border border-input bg-background px-3 py-2 text-sm"
                  placeholder="제품의 핵심 가치와 특징을 자유롭게 작성해주세요..."
                  value={formData.product_description}
                  onChange={(e) => setFormData({ ...formData, product_description: e.target.value })}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  타겟 고객
                </label>
                <Input
                  placeholder="예: 20-30대 직장인, 운동을 즐기는 사람들"
                  value={formData.target_audience}
                  onChange={(e) => setFormData({ ...formData, target_audience: e.target.value })}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  주요 특징 (최대 10개)
                </label>
                <div className="space-y-2">
                  {formData.key_features.map((feature, index) => (
                    <div key={index} className="flex gap-2">
                      <Input
                        placeholder={`특징 ${index + 1}`}
                        value={feature}
                        onChange={(e) => handleFeatureChange(index, e.target.value)}
                      />
                      {formData.key_features.length > 1 && (
                        <Button
                          variant="outline"
                          size="icon"
                          onClick={() => removeFeature(index)}
                        >
                          ✕
                        </Button>
                      )}
                    </div>
                  ))}
                  {formData.key_features.length < 10 && (
                    <Button
                      variant="outline"
                      onClick={addFeature}
                      className="w-full"
                    >
                      + 특징 추가
                    </Button>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 생성 버튼 */}
          <div className="flex justify-end gap-4">
            <Button
              variant="outline"
              onClick={() => navigate('/dashboard')}
              disabled={loading}
            >
              취소
            </Button>
            <Button
              onClick={handleGenerate}
              disabled={loading}
              className="min-w-[200px]"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  AI 생성 중...
                </>
              ) : (
                <>
                  <Zap className="mr-2 h-4 w-4" />
                  AI로 페이지 생성하기
                </>
              )}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CreateProjectPage;
