// TypeScript-based internationalization (i18n) module
import { writable, get } from 'svelte/store'

export type Locale = 'ru' | 'en'
export type TranslationKey =
  | 'home'
  | 'welcome_title'
  | 'welcome_subtitle'
  | 'welcome_badge'
  | 'instructions_title'
  | 'instructions_intro'
  | 'instructions_step1'
  | 'instructions_step2'
  | 'instructions_step3'
  | 'latest_reports_title'
  | 'footer'
  | 'language_label'
  | 'language_label_en'
  | 'instructions_toggle_show'
  | 'instructions_toggle_hide'
  | 'matches_nav'
  | 'matches_page_title'
  | 'loading'
  | 'refresh'
  | 'retry'
  | 'matches_load_error'
  | 'no_live_matches'
  | 'match_status_live'
  | 'match_status_scheduled'
  | 'match_status_completed'
  | 'match_status_cancelled'
  | 'set'
  | 'view_details'
  | 'match_details_title'
  | 'back_to_matches'
  | 'advice_title'
  | 'get_advice'
  | 'loading_advice'
  | 'advice_load_error'
  | 'live_matches_title'
  | 'live_matches_short'
  | 'total_matches'
  | 'ai_powered'
  | 'hide_reports'
  | 'show_reports'
  | 'features_title'
  | 'feature_realtime_title'
  | 'feature_realtime_desc'
  | 'feature_ai_title'
  | 'feature_ai_desc'
  | 'feature_telegram_title'
  | 'feature_telegram_desc'
  | 'feature_analytics_title'
  | 'feature_analytics_desc'
  | 'how_it_works_title'
  | 'step1_title'
  | 'step1_desc'
  | 'step2_title'
  | 'step2_desc'
  | 'step3_title'
  | 'step3_desc'
  | 'privacy'
  | 'terms'
  | 'contact'
  | 'coming_soon_max_title'
  | 'coming_soon_max_desc'
  | 'coming_soon_badge'

// Locale store (default ru)
export const locale = writable<Locale>('ru')

// Helper to get current locale value
export function getLocale() {
  return get(locale)
}

// Translations dictionary
export const translations: Record<Locale, Record<TranslationKey, string>> = {
  ru: {
    home: 'Главная',
    welcome_title: 'Анализ волейбольных матчей',
    welcome_subtitle: 'Современная платформа для отслеживания и анализа волейбольных матчей с AI-рекомендациями в реальном времени',
    welcome_badge: 'Добро пожаловать',
    instructions_title: 'Как пользоваться ботом',
    instructions_intro: 'Следуйте инструкциям ниже, чтобы получать анализ по матчам напрямую в Telegram.',
    instructions_step1: '1) Найдите volleyball_analysis_bot в Telegram',
    instructions_step2: '2) Нажмите кнопку Подключить и следуйте инструкциям',
    instructions_step3: '3) Используйте команды /reports, /live и /summary для получения анализа',
    latest_reports_title: 'Последние отчёты',
    footer: 'VolleyLab — Ваш персональный аналитик волейбольных матчей',
    language_label: 'Русский',
    language_label_en: 'English',
    instructions_toggle_show: 'Показать инструкции',
    instructions_toggle_hide: 'Свернуть',
    matches_nav: 'Матчи',
    matches_page_title: 'Активные матчи',
    loading: 'Загрузка...',
    refresh: 'Обновить',
    retry: 'Повторить',
    matches_load_error: 'Не удалось загрузить матчи',
    no_live_matches: 'Нет активных матчей',
    match_status_live: 'Live',
    match_status_scheduled: 'Запланирован',
    match_status_completed: 'Завершён',
    match_status_cancelled: 'Отменён',
    set: 'Сет',
    view_details: 'Подробнее',
    match_details_title: 'Детали матча',
    back_to_matches: '← Назад к матчам',
    advice_title: 'Совет от ИИ',
    get_advice: 'Получить совет',
    loading_advice: 'Получение совета...',
    advice_load_error: 'Не удалось получить совет',
    live_matches_title: 'Live матчи',
    live_matches_short: 'Live',
    total_matches: 'Всего',
    ai_powered: 'AI Powered',
    hide_reports: 'Свернуть отчёты',
    show_reports: 'Показать отчёты',
    features_title: 'Возможности',
    feature_realtime_title: 'Реальное время',
    feature_realtime_desc: 'Отслеживайте матчи в реальном времени с обновлением счёта и статистики',
    feature_ai_title: 'AI Анализ',
    feature_ai_desc: 'Получайте умные рекомендации и тактические советы на основе данных матча',
    feature_telegram_title: 'Telegram Бот',
    feature_telegram_desc: 'Удобное управление через Telegram — получайте уведомления и анализируйте матчи',
    feature_analytics_title: 'Аналитика',
    feature_analytics_desc: 'Подробная статистика и история матчей для глубокого анализа игры',
    how_it_works_title: 'Как это работает',
    step1_title: 'Подключите бота',
    step1_desc: 'Найдите нашего Telegram бота и нажмите кнопку «Подключить» для начала работы',
    step2_title: 'Создайте матч',
    step2_desc: 'Введите названия команд и составы игроков для начала отслеживания матча',
    step3_title: 'Получайте анализ',
    step3_desc: 'Используйте команду /advice для получения AI-рекомендаций по ходу матча',
    privacy: 'Конфиденциальность',
    terms: 'Условия',
    contact: 'Контакты',
    coming_soon_max_title: 'Бот в Max',
    coming_soon_max_desc: 'Скоро возможность создания матчей прямо в Max',
    coming_soon_badge: 'Скоро',
  },
  en: {
    home: 'Home',
    welcome_title: 'Volleyball Match Analysis',
    welcome_subtitle: 'Modern platform for tracking and analyzing volleyball matches with real-time AI recommendations',
    welcome_badge: 'Welcome',
    instructions_title: 'How to use the bot',
    instructions_intro: 'Follow these steps to receive match analytics directly in Telegram.',
    instructions_step1: '1) Find volleyball_analysis_bot on Telegram',
    instructions_step2: '2) Tap Connect and follow the prompts',
    instructions_step3: '3) Use /reports, /live, and /summary to get insights',
    latest_reports_title: 'Latest Reports',
    footer: 'VolleyLab — Your personal volleyball match analyst',
    language_label: 'Русский',
    language_label_en: 'English',
    instructions_toggle_show: 'Show instructions',
    instructions_toggle_hide: 'Hide',
    matches_nav: 'Matches',
    matches_page_title: 'Live Matches',
    loading: 'Loading...',
    refresh: 'Refresh',
    retry: 'Retry',
    matches_load_error: 'Failed to load matches',
    no_live_matches: 'No live matches',
    match_status_live: 'Live',
    match_status_scheduled: 'Scheduled',
    match_status_completed: 'Completed',
    match_status_cancelled: 'Cancelled',
    set: 'Set',
    view_details: 'View Details',
    match_details_title: 'Match Details',
    back_to_matches: '← Back to Matches',
    advice_title: 'AI Advice',
    get_advice: 'Get Advice',
    loading_advice: 'Getting advice...',
    advice_load_error: 'Failed to get advice',
    live_matches_title: 'Live Matches',
    live_matches_short: 'Live',
    total_matches: 'Total',
    ai_powered: 'AI Powered',
    hide_reports: 'Hide reports',
    show_reports: 'Show reports',
    features_title: 'Features',
    feature_realtime_title: 'Real-time Tracking',
    feature_realtime_desc: 'Track matches in real-time with live score updates and statistics',
    feature_ai_title: 'AI Analysis',
    feature_ai_desc: 'Get smart recommendations and tactical insights based on match data',
    feature_telegram_title: 'Telegram Bot',
    feature_telegram_desc: 'Easy management via Telegram — receive notifications and analyze matches',
    feature_analytics_title: 'Analytics',
    feature_analytics_desc: 'Detailed statistics and match history for deep game analysis',
    how_it_works_title: 'How It Works',
    step1_title: 'Connect the Bot',
    step1_desc: 'Find our Telegram bot and tap "Connect" to get started',
    step2_title: 'Create a Match',
    step2_desc: 'Enter team names and player rosters to start tracking the match',
    step3_title: 'Get Analysis',
    step3_desc: 'Use /advice command to receive AI-powered recommendations during the match',
    privacy: 'Privacy',
    terms: 'Terms',
    contact: 'Contact',
    coming_soon_max_title: 'Bot in Max',
    coming_soon_max_desc: 'Coming soon: Create matches directly in Max',
    coming_soon_badge: 'Coming Soon',
  },
}

// Convenience translation helper
export function t(key: TranslationKey, l?: Locale): string {
  const lang = l ?? get(locale)
  const map = translations[lang] ?? translations.ru
  return map[key] ?? key
}
