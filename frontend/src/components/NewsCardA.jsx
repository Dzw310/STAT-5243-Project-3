import { useRef } from 'react';
import LearnMoreBtn from './LearnMoreBtn';
import { trackEvent, PLACEHOLDER_GRADIENT } from '../utils/tracker';
import styles from './NewsCardA.module.css';

const NewsCardA = ({ article }) => {
  const { article_id, headline, full_summary, author, date, category, image_url, article_position } = article;
  const hoverStart = useRef(null);

  const onMouseEnter = () => { hoverStart.current = Date.now(); };
  const onMouseLeave = () => {
    if (hoverStart.current) {
      const seconds = (Date.now() - hoverStart.current) / 1000;
      if (seconds >= 0.5) {
        trackEvent('card_hover', {
          article_id,
          article_position,
          value: seconds,
        });
      }
      hoverStart.current = null;
    }
  };

  return (
    <article
      className={styles.card}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
    >
      <div className={styles.imageWrap}>
        {image_url ? (
          <img src={image_url} alt={headline} className={styles.image} loading="lazy" />
        ) : (
          <div className={styles.placeholder} style={{ background: PLACEHOLDER_GRADIENT }} />
        )}
      </div>
      <div className={styles.body}>
        <div className={styles.meta}>
          <span className={styles.category}>{category}</span>
          <span className={styles.date}>{date}</span>
        </div>
        <h2 className={styles.headline}>{headline}</h2>
        <p className={styles.author}>By {author}</p>
        <p className={styles.summary}>{full_summary}</p>
        <LearnMoreBtn articleId={article_id} articlePosition={article_position} />
      </div>
    </article>
  );
};

export default NewsCardA;
