import { useEffect, useState, useRef, useCallback } from 'react';
import NewsCardA from '../components/NewsCardA';
import NewsCardB from '../components/NewsCardB';
import {
  trackEvent,
  trackBeacon,
  createScrollTracker,
  createImpressionTracker,
  createTimer,
} from '../utils/tracker';
import styles from './NewsFeed.module.css';

const DEPTH_MARKS = [25, 50, 75, 100];

const NewsFeed = ({ group }) => {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const scrollTrackerRef = useRef(null);
  const impressionTrackerRef = useRef(null);
  const feedTimerRef = useRef(null);
  const sessionSentRef = useRef(false);

  const sentinelRef = useCallback((el) => {
    if (el) {
      if (!scrollTrackerRef.current) {
        scrollTrackerRef.current = createScrollTracker();
      }
      scrollTrackerRef.current.observe(el);
    }
  }, []);

  const cardRef = useCallback((el) => {
    if (el) {
      if (!impressionTrackerRef.current) {
        impressionTrackerRef.current = createImpressionTracker();
      }
      impressionTrackerRef.current.observe(el);
    }
  }, []);

  useEffect(() => {
    fetch('/api/articles')
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => {
        setArticles(data.articles);
        trackEvent('page_view');
        feedTimerRef.current = createTimer();
        sessionSentRef.current = false;
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    return () => {
      scrollTrackerRef.current?.disconnect();
      impressionTrackerRef.current?.disconnect();
    };
  }, []);

  // Session end tracking with pause/resume on tab visibility
  useEffect(() => {
    const sendSessionEnd = () => {
      if (feedTimerRef.current && !sessionSentRef.current) {
        sessionSentRef.current = true;
        trackBeacon('session_end', { value: feedTimerRef.current() });
      }
    };

    const onVisChange = () => {
      if (!feedTimerRef.current) return;
      if (document.visibilityState === 'hidden') {
        feedTimerRef.current.pause();
      } else {
        feedTimerRef.current.resume();
      }
    };

    document.addEventListener('visibilitychange', onVisChange);
    window.addEventListener('beforeunload', sendSessionEnd);

    return () => {
      sendSessionEnd();
      document.removeEventListener('visibilitychange', onVisChange);
      window.removeEventListener('beforeunload', sendSessionEnd);
    };
  }, []);

  if (loading) {
    return <p className={styles.loader}>Fetching campus news...</p>;
  }

  const CardComponent = group === 'A' ? NewsCardA : NewsCardB;

  const sentinelAfterIndex = (idx) => {
    const total = articles.length;
    return DEPTH_MARKS.filter((d) => Math.floor((total * d) / 100) - 1 === idx);
  };

  return (
    <div className={styles.feed}>
      {articles.map((article, idx) => (
        <div key={article.article_id}>
          <div
            ref={cardRef}
            data-article-id={article.article_id}
            data-article-position={article.article_position}
          >
            <CardComponent article={article} />
          </div>
          {sentinelAfterIndex(idx).map((depth) => (
            <div
              key={depth}
              className={styles.sentinel}
              data-depth={depth}
              ref={sentinelRef}
            />
          ))}
        </div>
      ))}
      <div className={styles.sentinel} data-depth="100" ref={sentinelRef} />
    </div>
  );
};

export default NewsFeed;
