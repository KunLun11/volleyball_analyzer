<script lang="ts">
  import { t } from '$lib/i18n'

  type FeatureCard = {
    id: number
    icon: string
    title: string
    description: string
    gradient: string
    delay: number
    comingSoon?: boolean
  }

  const cards: FeatureCard[] = [
    {
      id: 1,
      icon: '📊',
      title: t('feature_analytics_title'),
      description: t('feature_analytics_desc'),
      gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      delay: 0,
    },
    {
      id: 2,
      icon: '⚡',
      title: t('feature_realtime_title'),
      description: t('feature_realtime_desc'),
      gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
      delay: 0.1,
    },
    {
      id: 3,
      icon: '🤖',
      title: t('feature_ai_title'),
      description: t('feature_ai_desc'),
      gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
      delay: 0.2,
    },
    {
      id: 4,
      icon: '📱',
      title: t('feature_telegram_title'),
      description: t('feature_telegram_desc'),
      gradient: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
      delay: 0.3,
    },
    {
      id: 5,
      icon: '🔜',
      title: t('coming_soon_max_title'),
      description: t('coming_soon_max_desc'),
      gradient: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
      delay: 0.4,
      comingSoon: true,
    },
  ]
</script>

<section class="floating-cards-section">
  <h2 class="section-title">{t('features_title')}</h2>
  <div class="floating-cards-container">
    {#each cards as card (card.id)}
      <div
        class="floating-card"
        style="
          background: {card.gradient};
          animation-delay: {card.delay}s;
        "
        role="article"
        aria-label={card.title}
      >
        <div class="card-content">
          <span class="card-icon">{card.icon}</span>
          <h3 class="card-title">{card.title}</h3>
          <p class="card-description">{card.description}</p>
          {#if card.comingSoon}
            <span class="coming-soon-badge">{t('coming_soon_badge')}</span>
          {/if}
        </div>
        <div class="card-glow"></div>
      </div>
    {/each}
  </div>
</section>

<style>
  .floating-cards-section {
    padding: 60px 40px;
    text-align: center;
  }

  .section-title {
    font-size: 2.5rem;
    margin: 0 0 50px;
    color: #2c5282;
    font-weight: 800;
    text-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  }

  .floating-cards-container {
    display: flex;
    justify-content: center;
    gap: 24px;
    flex-wrap: wrap;
    max-width: 1400px;
    margin: 0 auto;
    perspective: 1000px;
  }

  .floating-card {
    position: relative;
    width: 240px;
    height: 320px;
    border-radius: 24px;
    padding: 32px 24px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
    overflow: hidden;
    animation: float 6s ease-in-out infinite;
    backface-visibility: hidden;
  }

  .floating-card:hover {
    transform: translateY(-20px) scale(1.05) rotateY(5deg);
    box-shadow: 0 25px 60px rgba(0, 0, 0, 0.3);
  }

  .floating-card:nth-child(1):hover {
    transform: translateY(-20px) scale(1.05) rotate(-2deg);
  }

  .floating-card:nth-child(2):hover {
    transform: translateY(-20px) scale(1.05) rotate(2deg);
  }

  .floating-card:nth-child(3):hover {
    transform: translateY(-20px) scale(1.05) rotate(-1deg);
  }

  .floating-card:nth-child(4):hover {
    transform: translateY(-20px) scale(1.05) rotate(1deg);
  }

  .floating-card:nth-child(5):hover {
    transform: translateY(-20px) scale(1.05) rotate(3deg);
  }

  .card-content {
    position: relative;
    z-index: 2;
    text-align: center;
    color: white;
  }

  .card-icon {
    font-size: 4rem;
    display: block;
    margin-bottom: 20px;
    filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.2));
    animation: iconBounce 3s ease-in-out infinite;
  }

  .card-title {
    font-size: 1.3rem;
    font-weight: 700;
    margin: 0 0 12px;
    text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  }

  .card-description {
    font-size: 0.9rem;
    line-height: 1.5;
    margin: 0;
    opacity: 0.95;
    text-shadow: 0 1px 4px rgba(0, 0, 0, 0.2);
  }

  .coming-soon-badge {
    display: inline-block;
    margin-top: 16px;
    padding: 6px 14px;
    background: rgba(255, 255, 255, 0.3);
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.4);
    animation: pulse 2s ease-in-out infinite;
  }

  .card-glow {
    position: absolute;
    top: 50%;
    left: 50%;
    width: 120%;
    height: 120%;
    background: radial-gradient(
      circle,
      rgba(255, 255, 255, 0.3) 0%,
      transparent 70%
    );
    transform: translate(-50%, -50%);
    opacity: 0;
    transition: opacity 0.4s ease;
    pointer-events: none;
  }

  .floating-card:hover .card-glow {
    opacity: 1;
  }

  @keyframes float {
    0%, 100% {
      transform: translateY(0);
    }
    50% {
      transform: translateY(-10px);
    }
  }

  @keyframes iconBounce {
    0%, 100% {
      transform: translateY(0) scale(1);
    }
    50% {
      transform: translateY(-5px) scale(1.1);
    }
  }

  @keyframes pulse {
    0%, 100% {
      opacity: 1;
      transform: scale(1);
    }
    50% {
      opacity: 0.7;
      transform: scale(1.05);
    }
  }

  @media (max-width: 1200px) {
    .floating-card {
      width: 220px;
      height: 300px;
    }
  }

  @media (max-width: 768px) {
    .floating-cards-section {
      padding: 40px 20px;
    }

    .section-title {
      font-size: 2rem;
      margin: 0 0 30px;
    }

    .floating-cards-container {
      gap: 16px;
    }

    .floating-card {
      width: 100%;
      max-width: 280px;
      height: 280px;
    }

    .card-icon {
      font-size: 3.5rem;
    }

    .card-title {
      font-size: 1.2rem;
    }

    .card-description {
      font-size: 0.85rem;
    }
  }
</style>
