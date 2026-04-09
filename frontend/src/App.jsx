import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import NewsFeed from './pages/NewsFeed';
import Article from './pages/Article';
import styles from './App.module.css';

function App() {
  const [assignment, setAssignment] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('/api/assign')
      .then((res) => {
        if (!res.ok) throw new Error('Assignment failed');
        return res.json();
      })
      .then(setAssignment)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className={styles.loadingContainer}>
        <div className={styles.spinner} />
        <p>Loading Lion's Feed...</p>
      </div>
    );
  }

  if (error) {
    return <div className={styles.errorContainer}>Something went wrong. Please refresh.</div>;
  }

  return (
    <BrowserRouter>
      <div className={styles.appShell}>
        <Header />
        <main className={styles.mainContent}>
          <Routes>
            <Route path="/" element={<NewsFeed group={assignment.group} />} />
            <Route path="/article/:id" element={<Article />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
