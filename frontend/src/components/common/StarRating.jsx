const StarRating = ({ rating = 0, max = 5, size = 'md' }) => {
  const sizes = { sm: 'text-sm', md: 'text-base', lg: 'text-xl' };
  return (
    <span className={`${sizes[size]} select-none`} aria-label={`${rating} out of ${max} stars`}>
      {Array.from({ length: max }, (_, i) => (
        <span key={i} className={i < Math.round(rating) ? 'text-yellow-400' : 'text-gray-300'}>
          ★
        </span>
      ))}
    </span>
  );
};

export default StarRating;
