const API_EVENTS = '/api/events';

export const trackEvent = async (eventType, data = {}) => {
  try {
    await fetch(API_EVENTS, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ event_type: eventType, ...data }),
    });
  } catch (err) {
    // Tracking failure should not break user experience
  }
};

export const trackBeacon = (eventType, data = {}) => {
  const payload = JSON.stringify({ event_type: eventType, ...data });
  const blob = new Blob([payload], { type: 'application/json' });
  navigator.sendBeacon(API_EVENTS, blob);
};

export const createScrollTracker = () => {
  const tracked = new Set();

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const depth = parseInt(entry.target.dataset.depth, 10);
          if (!tracked.has(depth)) {
            tracked.add(depth);
            trackEvent('scroll', { value: depth });
          }
        }
      });
    },
    { threshold: 0.1 }
  );

  return {
    observe: (el) => el && observer.observe(el),
    disconnect: () => observer.disconnect(),
  };
};

export const createImpressionTracker = () => {
  const seen = new Set();

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const { articleId, articlePosition } = entry.target.dataset;
          if (articleId && !seen.has(articleId)) {
            seen.add(articleId);
            trackEvent('card_impression', {
              article_id: articleId,
              article_position: parseInt(articlePosition, 10),
            });
          }
        }
      });
    },
    { threshold: 0.5 }
  );

  return {
    observe: (el) => el && observer.observe(el),
    disconnect: () => observer.disconnect(),
  };
};

export const createTimer = () => {
  let accumulated = 0;
  let segmentStart = Date.now();
  let paused = false;

  const timer = () => {
    const current = paused ? 0 : (Date.now() - segmentStart) / 1000;
    return accumulated + current;
  };

  timer.pause = () => {
    if (!paused) {
      accumulated += (Date.now() - segmentStart) / 1000;
      paused = true;
    }
  };

  timer.resume = () => {
    if (paused) {
      segmentStart = Date.now();
      paused = false;
    }
  };

  return timer;
};

export const PLACEHOLDER_GRADIENT = 'linear-gradient(135deg, #B9D9EB 0%, #87CEEB 100%)';
