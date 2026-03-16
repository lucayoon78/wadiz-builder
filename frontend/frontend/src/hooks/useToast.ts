import { useState, useCallback } from 'react';

interface Toast {
  title: string;
  description?: string;
  variant?: 'default' | 'destructive' | 'success';
}

export const useToast = () => {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const toast = useCallback((toastData: Toast) => {
    setToasts((prev) => [...prev, toastData]);
    
    // 3초 후 자동 제거
    setTimeout(() => {
      setToasts((prev) => prev.slice(1));
    }, 3000);
    
    // 콘솔에도 출력
    console.log(`[Toast ${toastData.variant || 'default'}] ${toastData.title}`, toastData.description);
  }, []);

  return { toast, toasts };
};
