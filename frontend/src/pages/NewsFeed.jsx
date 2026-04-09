import { useEffect, useState, useRef, useCallback } from 'react';
import NewsCardA from '../components/NewsCardA';
import NewsCardB from '../components/NewsCardB';
import { trackEvent, createScrollTracker } from '../utils/tracker';
import styles from './NewsFeed.module.css';

const DEPTH_MARKS = [25, 50, 75, 100];

const NewsFeed = ({ group }) => {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const scrollTrackerRef = useRef(null);

  const sentinelRef = useCallback((el) => {
    if (el && scrollTrackerRef.current) {
      scrollTrackerRef.current.observe(el);
    }
  }, []);

  useEffect(() => {
    fetch('/api/articles')
      .then((res) => res.json())
      .then((data) => {
        setArticles(data.articles);
        trackEvent('page_view');
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    scrollTrackerRef.current = createScrollTracker();
    return () => scrollTrackerRef.current?.disconnect();
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
          <CardComponent article={article} />
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
