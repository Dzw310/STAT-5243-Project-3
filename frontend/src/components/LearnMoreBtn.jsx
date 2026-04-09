import { Link } from 'react-router-dom';
import { trackEvent } from '../utils/tracker';
import styles from './LearnMoreBtn.module.css';

const LearnMoreBtn = ({ articleId, articlePosition }) => {
  const handleClick = () => {
    trackEvent('click', { article_id: articleId, article_position: articlePosition });
  };

  return (
    <Link
      to={`/article/${articleId}`}
      onClick={handleClick}
      className={styles.button}
    >
      Learn More
    </Link>
  );
};

export default LearnMoreBtn;
