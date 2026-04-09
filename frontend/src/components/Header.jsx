import { Link } from 'react-router-dom';
import styles from './Header.module.css';

const Header = () => (
  <header className={styles.header}>
    <div className={styles.container}>
      <Link to="/" className={styles.branding}>
        <h1 className={styles.title}>Lion's Feed</h1>
        <p className={styles.subtitle}>Columbia Campus News</p>
      </Link>
    </div>
  </header>
);

export default Header;
