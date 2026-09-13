declare global {
  interface Window {
    Telegram?: any;
  }
}

export const useTelegram = () => {
  const tg = typeof window !== 'undefined' ? window.Telegram?.WebApp : undefined;
  return {
    tg,
    user: tg?.initDataUnsafe?.user,
    queryId: tg?.initDataUnsafe?.query_id,
    onClose: () => tg?.close(),
    expand: () => tg?.expand()
  };
};