import React, { useState } from 'react';
import { Upload, Link as LinkIcon, ArrowRight, Sparkles, CheckCircle, XCircle } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { useNavigate } from 'react-router-dom';
import { api } from '../lib/api';
import { useToast } from '../components/ui/Toast';

interface AnalysisResult {
  strengths: string[];
  weaknesses: string[];
  structure_issues: string;
  copy_rating: string;
  visual_rating: string;
  priority_improvements: string[];
}

interface ImprovementSuggestions {
  new_headline: string;
  new_subheadline: string;
  structure_plan: string[];
  copy_improvements: string[];
  visual_improvements: string[];
  estimated_improvement: string;
}

export const RenewalPage: React.FC = () => {
  const [mode, setMode] = useState<'url' | 'file'>('url');
  const [url, setUrl] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState<'input' | 'analyzing' | 'result'>('input');
  
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [improvements, setImprovements] = useState<ImprovementSuggestions | null>(null);
  const [renewedContent, setRenewedContent] = useState<any>(null);
  
  const navigate = useNavigate();
  const toast = useToast();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleAnalyze = async () => {
    if (mode === 'url' && !url) {
      toast.error('URL을 입력해주세요');
      return;
    }
    if (mode === 'file' && !file) {
      toast.error('HTML 파일을 선택해주세요');
      return;
    }

    try {
      setLoading(true);
      setStep('analyzing');

      if (mode === 'url') {
        // URL 기반 리뉴얼
        const response = await api.post('/renewal/renew-from-url', {
          url: url
        });
        
        setAnalysisResult(response.data.analysis);
        setImprovements(response.data.improvements);
        setRenewedContent(response.data.renewed_content);
        
      } else {
        // HTML 파일 기반 리뉴얼
        const formData = new FormData();
        formData.append('html_file', file!);
        
        const response = await api.post('/renewal/renew-from-html', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
        
        setAnalysisResult(response.data.analysis);
        setImprovements(response.data.improvements);
        setRenewedContent(response.data.renewed_content);
      }

      setStep('result');
      toast.success('리뉴얼 분석 완료!');

    } catch (error: any) {
      console.error('리뉴얼 실패:', error);
      toast.error('리뉴얼에 실패했습니다: ' + (error.response?.data?.detail || error.message));
      setStep('input');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* 헤더 */}
        <div className="space-y-1">
          <h1 className="text-4xl font-bold tracking-tight flex items-center gap-3">
            <Sparkles className="h-10 w-10 text-primary" />
            페이지 리뉴얼
          </h1>
          <p className="text-muted-foreground text-lg">
            기존 페이지를 AI가 분석하고 개선된 버전을 제안합니다
          </p>
        </div>

        {/* Step 1: 입력 */}
        {step === 'input' && (
          <div className="space-y-6 animate-fade-in">
            {/* 모드 선택 */}
            <div className="flex items-center gap-4">
              <button
                onClick={() => setMode('url')}
                className={`flex-1 p-6 rounded-lg border-2 transition-all ${
                  mode === 'url'
                    ? 'border-primary bg-primary/10'
                    : 'border-white/10 hover:border-white/30'
                }`}
              >
                <LinkIcon className="h-8 w-8 mx-auto mb-3 text-primary" />
                <div className="font-semibold text-lg">URL 입력</div>
                <div className="text-sm text-muted-foreground mt-1">
                  와디즈/쿠팡 페이지 URL 붙여넣기
                </div>
              </button>

              <button
                onClick={() => setMode('file')}
                className={`flex-1 p-6 rounded-lg border-2 transition-all ${
                  mode === 'file'
                    ? 'border-primary bg-primary/10'
                    : 'border-white/10 hover:border-white/30'
                }`}
              >
                <Upload className="h-8 w-8 mx-auto mb-3 text-primary" />
                <div className="font-semibold text-lg">HTML 업로드</div>
                <div className="text-sm text-muted-foreground mt-1">
                  HTML 파일 드래그앤드롭
                </div>
              </button>
            </div>

            {/* 입력 영역 */}
            <Card>
              <CardHeader>
                <CardTitle>
                  {mode === 'url' ? 'URL 입력' : 'HTML 파일 업로드'}
                </CardTitle>
                <CardDescription>
                  {mode === 'url'
                    ? '분석할 페이지의 URL을 입력하세요'
                    : 'HTML 파일을 선택하거나 드래그앤드롭하세요'}
                </CardDescription>
              </CardHeader>

              <CardContent className="space-y-4">
                {mode === 'url' ? (
                  <Input
                    type="url"
                    placeholder="https://www.wadiz.kr/web/campaign/detail/..."
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    className="text-lg"
                  />
                ) : (
                  <div
                    className="border-2 border-dashed border-white/20 rounded-lg p-12 text-center hover:border-primary transition-colors cursor-pointer"
                    onClick={() => document.getElementById('file-input')?.click()}
                  >
                    <Upload className="h-16 w-16 mx-auto mb-4 text-muted-foreground" />
                    {file ? (
                      <div>
                        <div className="text-lg font-medium">{file.name}</div>
                        <div className="text-sm text-muted-foreground mt-1">
                          {(file.size / 1024).toFixed(1)} KB
                        </div>
                      </div>
                    ) : (
                      <div>
                        <div className="text-lg font-medium">파일을 선택하거나 드래그하세요</div>
                        <div className="text-sm text-muted-foreground mt-1">
                          HTML 파일만 지원됩니다
                        </div>
                      </div>
                    )}
                    <input
                      id="file-input"
                      type="file"
                      accept=".html,.htm"
                      onChange={handleFileChange}
                      className="hidden"
                    />
                  </div>
                )}

                <div className="bg-secondary/50 rounded-lg p-4">
                  <div className="text-sm text-muted-foreground space-y-2">
                    <div className="flex items-center gap-2">
                      <Sparkles className="h-4 w-4 text-primary" />
                      <span>AI가 자동으로 분석하고 개선안을 제시합니다</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      <span>예상 시간: 10-15초</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      <span>비용: 약 ₩200</span>
                    </div>
                  </div>
                </div>

                <Button
                  size="lg"
                  className="w-full gap-2"
                  onClick={handleAnalyze}
                  disabled={loading || (mode === 'url' && !url) || (mode === 'file' && !file)}
                >
                  <Sparkles className="h-5 w-5" />
                  AI 분석 & 리뉴얼 시작
                  <ArrowRight className="h-5 w-5" />
                </Button>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Step 2: 분석 중 */}
        {step === 'analyzing' && (
          <div className="flex flex-col items-center justify-center py-20 animate-fade-in">
            <div className="animate-spin rounded-full h-20 w-20 border-b-4 border-primary mb-6"></div>
            <h2 className="text-2xl font-bold mb-2">AI가 페이지를 분석하고 있습니다...</h2>
            <p className="text-muted-foreground">10-15초 정도 소요됩니다</p>
            <div className="mt-8 space-y-2 text-sm text-muted-foreground">
              <div>✓ 페이지 콘텐츠 추출 중...</div>
              <div>✓ Gemini로 현재 분석 중...</div>
              <div>✓ GPT-4로 개선안 도출 중...</div>
              <div>✓ 리뉴얼 콘텐츠 생성 중...</div>
            </div>
          </div>
        )}

        {/* Step 3: 결과 */}
        {step === 'result' && analysisResult && improvements && (
          <div className="space-y-6 animate-fade-in">
            {/* Before & After 헤드라인 비교 */}
            <Card className="border-2 border-primary">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="h-6 w-6 text-primary" />
                  Before & After
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-6">
                  <div>
                    <Badge variant="error" className="mb-3">Before</Badge>
                    <div className="text-xl font-semibold text-muted-foreground">
                      {renewedContent?.before_after_comparison?.before?.title || '기존 헤드라인'}
                    </div>
                  </div>
                  <div>
                    <Badge variant="success" className="mb-3">After (AI 개선)</Badge>
                    <div className="text-xl font-bold text-primary">
                      {improvements.new_headline}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* 분석 결과 */}
            <div className="grid grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <CheckCircle className="h-6 w-6 text-green-500" />
                    강점 (유지)
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {analysisResult.strengths.map((strength, idx) => (
                      <li key={idx} className="flex items-start gap-2">
                        <span className="text-green-500">✓</span>
                        <span>{strength}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <XCircle className="h-6 w-6 text-red-500" />
                    약점 (개선)
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {analysisResult.weaknesses.map((weakness, idx) => (
                      <li key={idx} className="flex items-start gap-2">
                        <span className="text-red-500">✗</span>
                        <span>{weakness}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            </div>

            {/* 개선 제안 */}
            <Card>
              <CardHeader>
                <CardTitle>AI 개선 제안</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h3 className="font-semibold mb-2">카피 개선 포인트</h3>
                  <ul className="space-y-1">
                    {improvements.copy_improvements.map((imp, idx) => (
                      <li key={idx} className="text-sm">• {imp}</li>
                    ))}
                  </ul>
                </div>

                <div>
                  <h3 className="font-semibold mb-2">시각적 개선 포인트</h3>
                  <ul className="space-y-1">
                    {improvements.visual_improvements.map((imp, idx) => (
                      <li key={idx} className="text-sm">• {imp}</li>
                    ))}
                  </ul>
                </div>

                <div className="bg-primary/10 rounded-lg p-4">
                  <div className="font-semibold text-primary mb-1">예상 개선 효과</div>
                  <div>{improvements.estimated_improvement}</div>
                </div>
              </CardContent>
            </Card>

            {/* 액션 버튼 */}
            <div className="flex gap-4">
              <Button variant="secondary" className="flex-1" onClick={() => setStep('input')}>
                다시 분석하기
              </Button>
              <Button variant="primary" className="flex-1 gap-2">
                <Sparkles className="h-5 w-5" />
                리뉴얼 페이지 생성하기
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
