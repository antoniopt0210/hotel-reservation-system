const PageWrapper = ({ children, className = '' }) => (
  <main className={`max-w-7xl mx-auto px-4 py-8 ${className}`}>
    {children}
  </main>
);

export default PageWrapper;
