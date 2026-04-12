import { useEffect, useState, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import { trackBeacon, createTimer, PLACEHOLDER_GRADIENT } from '../utils/tracker';
import styles from './Article.module.css';

const Article = () => {
  const { id } = useParams();
  const [article, setArticle] = useState(null);
  const [loading, setLoading] = useState(true);
  const getElapsed = useRef(null);
  const hasSent = useRef(false);

  useEffect(() => {
    fetch(`/api/articles/${id}`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => {
        setArticle(data);
        getElapsed.current = createTimer();
        hasSent.current = false;
      })
      .catch(() => {})
      .finally(() => setLoading(false));

    const sendTime = () => {
      if (getElapsed.current && !hasSent.current) {
        hasSent.current = true;
        trackBeacon('article_time', {
          article_id: id,
          value: getElapsed.current(),
        });
      }
    };

    const onVisChange = () => {
      if (!getElapsed.current) return;
      if (document.visibilityState === 'hidden') {
        getElapsed.current.pause();
      } else {
        getElapsed.current.resume();
      }
    };

    document.addEventListener('visibilitychange', onVisChange);
    window.addEventListener('beforeunload', sendTime);

    return () => {
      sendTime();
      document.removeEventListener('visibilitychange', onVisChange);
      window.removeEventListener('beforeunload', sendTime);
    };
  }, [id]);

  if (loading) return <p className={styles.loader}>Loading article...</p>;
  if (!article) return <p className={styles.error}>Article not found. <Link to="/">Back to feed</Link></p>;

  return (
    <div className={styles.container}>
      <Link to="/" className={styles.backLink}>&larr; Back to Feed</Link>
      <article>
        <header className={styles.header}>
          <div className={styles.meta}>
            <span className={styles.category}>{article.category}</span>
            <span className={styles.date}>{article.date}</span>
          </div>
          <h1 className={styles.headline}>{article.headline}</h1>
          <p className={styles.author}>By {article.author}</p>
        </header>

        <div className={styles.imageWrap}>
          {article.image_url ? (
            <img src={article.image_url} alt={article.headline} className={styles.image} />
          ) : (
            <div className={styles.placeholder} style={{ background: PLACEHOLDER_GRADIENT }} />
          )}
        </div>

        <div className={styles.content}>{article.full_content}</div>

        {article.source_url && (
          <a
            href={article.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className={styles.sourceBtn}
          >
            Visit Original Source
          </a>
        )}
      </article>
    </div>
  );
};

export default Article;
