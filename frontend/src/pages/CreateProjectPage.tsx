import React, { useState, useEffect } from 'react';
import { ArrowLeft, ArrowRight, Sparkles, Check } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Card, CardContent } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { api } from '../lib/api';
import { useNavigate, useLocation } from 'react-router-dom';

interface Template {
  id: number;
  name: string;
  description: string;
  category_id: number;
  success_rate: number;
  preview_image_url?: string;
}

export const CreateProjectPage: React.FC = () => {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [templates, setTemplates] = useState<Template[]>([]);
  const navigate = useNavigate();
  const location = useLocation();

  // Form data
  const [formData, setFormData] = useState({
    template_id: (location.state as any)?.templateId || null,
    project_name: '',
    product_name: '',
    usp: '',
    target_audience: '',
    brand_tone: 'professional' as 'professional' | 'friendly' | 'premium',
    platforms: ['wadiz'] as string[],
  });

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      const response = await api.get('/templates-enhanced/');
      setTemplates(response.data);
      // 상태에서 전달받은 템플릿이 있으면 자동 선택
      if ((location.state as any)?.templateId) {
        setFormData(prev => ({ ...prev, template_id: (location.state as any).templateId }));
        setStep(2); // 템플릿 이미 선택되었으므로 2단계로
      }
    } catch (error) {
      console.error('템플릿 로딩 실패:', error);
    }
  };

  const handleNext = () => {
    if (step < 3) setStep(step + 1);
  };

  const handleBack = () => {
    if (step > 1) setStep(step - 1);
  };

  const handleGenerate = async () => {
    try {
      setLoading(true);
      const response = await api.post('/multi-platform/quick-generate', {
        template_id: formData.template_id,
        product_name: formData.product_name,
        usp: formData.usp,
        target_audience: formData.target_audience,
        brand_tone: formData.brand_tone,
        platforms: formData.platforms,
        project_name: formData.project_name,
      });
      
      // 생성 완료 후 프로젝트 상세 페이지로 이동
      navigate(`/project/${response.data.project_id}`);
    } catch (error) {
      console.error('생성 실패:', error);
      alert('프로젝트 생성에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const isStepValid = () => {
    if (step === 1) return formData.template_id !== null;
    if (step === 2) return formData.project_name && formData.product_name && formData.usp && formData.target_audience;
    return true;
  };

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-5xl mx-auto space-y-8">
        {/* 헤더 */}
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/dashboard')}
            className="p-2 hover:bg-secondary rounded-lg transition-colors"
          >
            <ArrowLeft className="h-6 w-6" />
          </button>
          <div className="flex-1">
            <h1 className="text-3xl font-bold">새 프로젝트 만들기</h1>
            <p className="text-muted-foreground">3단계로 빠르게 시작하세요</p>
          </div>
        </div>

        {/* 진행 단계 */}
        <div className="flex items-center justify-between max-w-2xl mx-auto">
          {[
            { num: 1, label: '템플릿 선택' },
            { num: 2, label: '정보 입력' },
            { num: 3, label: 'AI 생성' },
          ].map((s, idx) => (
            <React.Fragment key={s.num}>
              <div className="flex flex-col items-center gap-2">
                <div
                  className={`
                    w-12 h-12 rounded-full flex items-center justify-center font-bold transition-all
                    ${step === s.num
                      ? 'bg-primary text-primary-foreground shadow-lg shadow-primary/50 scale-110'
                      : step > s.num
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-secondary text-muted-foreground'
                    }
                  `}
                >
                  {step > s.num ? <Check className="h-6 w-6" /> : s.num}
                </div>
                <span className={`text-sm font-medium ${step >= s.num ? 'text-foreground' : 'text-muted-foreground'}`}>
                  {s.label}
                </span>
              </div>
              {idx < 2 && (
                <div className={`flex-1 h-1 mx-4 rounded transition-colors ${step > s.num ? 'bg-primary' : 'bg-secondary'}`} />
              )}
            </React.Fragment>
          ))}
        </div>

        {/* Step 1: 템플릿 선택 */}
        {step === 1 && (
          <div className="space-y-6 animate-fade-in">
            <div className="text-center space-y-2">
              <h2 className="text-2xl font-bold">템플릿을 선택하세요</h2>
              <p className="text-muted-foreground">검증된 템플릿으로 시작하면 성공 확률이 높아집니다</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {templates.map((template) => (
                <Card
                  key={template.id}
                  hoverable
                  className={`cursor-pointer transition-all ${
                    formData.template_id === template.id ? 'ring-2 ring-primary shadow-lg shadow-primary/50' : ''
                  }`}
                  onClick={() => setFormData(prev => ({ ...prev, template_id: template.id }))}
                >
                  <div className="h-32 bg-gradient-to-br from-primary/20 via-accent/10 to-secondary/20 flex items-center justify-center text-4xl">
                    📄
                  </div>
                  <CardContent className="pt-4">
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <h3 className="font-semibold">{template.name}</h3>
                        {formData.template_id === template.id && (
                          <div className="w-6 h-6 rounded-full bg-primary flex items-center justify-center">
                            <Check className="h-4 w-4 text-primary-foreground" />
                          </div>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground line-clamp-2">{template.description}</p>
                      <Badge variant="success">✓ {template.success_rate}% 달성</Badge>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* Step 2: 정보 입력 */}
        {step === 2 && (
          <div className="space-y-6 animate-fade-in">
            <div className="text-center space-y-2">
              <h2 className="text-2xl font-bold">프로젝트 정보를 입력하세요</h2>
              <p className="text-muted-foreground">AI가 이 정보를 바탕으로 최적의 페이지를 생성합니다</p>
            </div>

            <Card className="max-w-2xl mx-auto">
              <CardContent className="pt-6 space-y-6">
                <Input
                  label="프로젝트 이름 *"
                  placeholder="예: 2024 스마트 텀블러 펀딩"
                  value={formData.project_name}
                  onChange={(e) => setFormData(prev => ({ ...prev, project_name: e.target.value }))}
                />

                <Input
                  label="제품명 *"
                  placeholder="예: 스마트 온도 유지 텀블러"
                  value={formData.product_name}
                  onChange={(e) => setFormData(prev => ({ ...prev, product_name: e.target.value }))}
                />

                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">핵심 강점 (USP) *</label>
                  <textarea
                    className="w-full h-24 rounded-lg border border-white/10 bg-secondary px-4 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
                    placeholder="예: 24시간 온도 유지 + UV-C 자동 살균 기능"
                    value={formData.usp}
                    onChange={(e) => setFormData(prev => ({ ...prev, usp: e.target.value }))}
                  />
                </div>

                <Input
                  label="타겟 고객 *"
                  placeholder="예: 바쁜 일상 속 건강을 챙기고 싶은 20-30대 직장인"
                  value={formData.target_audience}
                  onChange={(e) => setFormData(prev => ({ ...prev, target_audience: e.target.value }))}
                />

                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">브랜드 톤앤매너</label>
                  <div className="grid grid-cols-3 gap-3">
                    {[
                      { value: 'professional', label: '전문적', emoji: '💼' },
                      { value: 'friendly', label: '친근한', emoji: '😊' },
                      { value: 'premium', label: '프리미엄', emoji: '✨' },
                    ].map((tone) => (
                      <button
                        key={tone.value}
                        onClick={() => setFormData(prev => ({ ...prev, brand_tone: tone.value as any }))}
                        className={`
                          p-4 rounded-lg border transition-all
                          ${formData.brand_tone === tone.value
                            ? 'border-primary bg-primary/10 text-primary'
                            : 'border-white/10 hover:border-white/30'
                          }
                        `}
                      >
                        <div className="text-2xl mb-2">{tone.emoji}</div>
                        <div className="font-medium">{tone.label}</div>
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">플랫폼 선택</label>
                  <div className="grid grid-cols-2 gap-3">
                    {[
                      { value: 'wadiz', label: '와디즈', emoji: '🚀' },
                      { value: 'smartstore', label: '스마트스토어', emoji: '🛒' },
                      { value: 'coupang', label: '쿠팡', emoji: '📦' },
                      { value: 'gmarket', label: 'G마켓', emoji: '🏪' },
                    ].map((platform) => (
                      <label
                        key={platform.value}
                        className={`
                          flex items-center gap-3 p-4 rounded-lg border cursor-pointer transition-all
                          ${formData.platforms.includes(platform.value)
                            ? 'border-primary bg-primary/10'
                            : 'border-white/10 hover:border-white/30'
                          }
                        `}
                      >
                        <input
                          type="checkbox"
                          checked={formData.platforms.includes(platform.value)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setFormData(prev => ({ ...prev, platforms: [...prev.platforms, platform.value] }));
                            } else {
                              setFormData(prev => ({ ...prev, platforms: prev.platforms.filter(p => p !== platform.value) }));
                            }
                          }}
                          className="w-5 h-5 rounded border-primary text-primary focus:ring-primary"
                        />
                        <span className="text-2xl">{platform.emoji}</span>
                        <span className="font-medium">{platform.label}</span>
                      </label>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Step 3: AI 생성 */}
        {step === 3 && (
          <div className="space-y-6 animate-fade-in">
            <div className="text-center space-y-2">
              <h2 className="text-2xl font-bold">생성 준비 완료!</h2>
              <p className="text-muted-foreground">AI가 약 3초 안에 최적의 페이지를 만들어드립니다</p>
            </div>

            <Card className="max-w-2xl mx-auto">
              <CardContent className="pt-6 space-y-6">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <div className="text-sm text-muted-foreground">프로젝트 이름</div>
                    <div className="font-medium">{formData.project_name}</div>
                  </div>
                  <div className="space-y-2">
                    <div className="text-sm text-muted-foreground">제품명</div>
                    <div className="font-medium">{formData.product_name}</div>
                  </div>
                  <div className="space-y-2 col-span-2">
                    <div className="text-sm text-muted-foreground">핵심 강점</div>
                    <div className="font-medium">{formData.usp}</div>
                  </div>
                  <div className="space-y-2">
                    <div className="text-sm text-muted-foreground">타겟 고객</div>
                    <div className="font-medium">{formData.target_audience}</div>
                  </div>
                  <div className="space-y-2">
                    <div className="text-sm text-muted-foreground">브랜드 톤</div>
                    <div className="font-medium capitalize">{formData.brand_tone}</div>
                  </div>
                  <div className="space-y-2 col-span-2">
                    <div className="text-sm text-muted-foreground">플랫폼</div>
                    <div className="flex gap-2">
                      {formData.platforms.map(p => (
                        <Badge key={p}>{p}</Badge>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="pt-4 border-t border-white/10">
                  <div className="flex items-center gap-3 text-sm text-muted-foreground mb-4">
                    <Sparkles className="h-5 w-5 text-primary" />
                    <span>AI가 다음을 생성합니다:</span>
                  </div>
                  <ul className="space-y-2 text-sm">
                    <li className="flex items-center gap-2">
                      <Check className="h-4 w-4 text-green-500" />
                      와디즈 5단계 황금구조 페이지
                    </li>
                    <li className="flex items-center gap-2">
                      <Check className="h-4 w-4 text-green-500" />
                      감성적 카피라이팅 + 3가지 대안
                    </li>
                    <li className="flex items-center gap-2">
                      <Check className="h-4 w-4 text-green-500" />
                      플랫폼별 최적화 레이아웃
                    </li>
                    <li className="flex items-center gap-2">
                      <Check className="h-4 w-4 text-green-500" />
                      썸네일 + GIF 추천
                    </li>
                  </ul>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* 네비게이션 버튼 */}
        <div className="flex items-center justify-between max-w-2xl mx-auto pt-8">
          <Button
            variant="ghost"
            onClick={handleBack}
            disabled={step === 1 || loading}
            className="gap-2"
          >
            <ArrowLeft className="h-5 w-5" />
            이전
          </Button>

          {step < 3 ? (
            <Button
              onClick={handleNext}
              disabled={!isStepValid()}
              className="gap-2"
            >
              다음
              <ArrowRight className="h-5 w-5" />
            </Button>
          ) : (
            <Button
              onClick={handleGenerate}
              loading={loading}
              disabled={loading}
              size="lg"
              className="gap-2"
            >
              <Sparkles className="h-5 w-5" />
              {loading ? 'AI 생성 중...' : 'AI로 생성하기'}
            </Button>
          )}
        </div>
      </div>
    </div>
  );
};
