import LearnMoreBtn from './LearnMoreBtn';
import { PLACEHOLDER_GRADIENT } from '../utils/tracker';
import styles from './NewsCardB.module.css';

const NewsCardB = ({ article }) => {
  const { article_id, headline, teaser, image_url, article_position } = article;

  return (
    <article className={styles.card}>
      <div className={styles.imageWrap}>
        {image_url ? (
          <img src={image_url} alt={headline} className={styles.image} loading="lazy" />
        ) : (
          <div className={styles.placeholder} style={{ background: PLACEHOLDER_GRADIENT }} />
        )}
      </div>
      <div className={styles.body}>
        <h2 className={styles.headline}>{headline}</h2>
        <p className={styles.teaser}>{teaser}</p>
        <LearnMoreBtn articleId={article_id} articlePosition={article_position} />
      </div>
    </article>
  );
};

export default NewsCardB;
