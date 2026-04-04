import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { createReview } from '../../api/reviews';
import Button from '../common/Button';

const StarPicker = ({ value, onChange }) => (
  <div className="flex gap-1">
    {[1, 2, 3, 4, 5].map(s => (
      <button
        key={s}
        type="button"
        onClick={() => onChange(s)}
        className={`text-2xl transition ${s <= value ? 'text-yellow-400' : 'text-gray-300 hover:text-yellow-300'}`}
      >
        ★
      </button>
    ))}
  </div>
);

const ReviewForm = ({ hotelId, onSuccess }) => {
  const queryClient = useQueryClient();
  const [rating, setRating]   = useState(0);
  const [title, setTitle]     = useState('');
  const [body, setBody]       = useState('');
  const [formError, setError] = useState('');

  const { mutate, isLoading } = useMutation({
    mutationFn: () => createReview(hotelId, { rating, title, body }),
    onSuccess: () => {
      queryClient.invalidateQueries(['reviews', hotelId]);
      queryClient.invalidateQueries(['review-summary', hotelId]);
      queryClient.invalidateQueries(['hotel', hotelId]);
      setRating(0); setTitle(''); setBody(''); setError('');
      if (onSuccess) onSuccess();
    },
    onError: (err) => {
      setError(err.response?.data?.error || 'Could not submit review.');
    },
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (rating < 1) return setError('Please select a star rating.');
    mutate();
  };

  return (
    <form onSubmit={handleSubmit} className="bg-gray-50 border rounded-xl p-4 space-y-3">
      <h3 className="font-bold text-gray-700">Write a Review</h3>

      <div>
        <label className="block text-sm text-gray-600 mb-1">Your rating</label>
        <StarPicker value={rating} onChange={setRating} />
      </div>

      <div>
        <label className="block text-sm text-gray-600 mb-1">Title <span className="text-gray-400">(optional)</span></label>
        <input
          type="text"
          value={title}
          onChange={e => setTitle(e.target.value)}
          maxLength={120}
          placeholder="Summarise your stay…"
          className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
        />
      </div>

      <div>
        <label className="block text-sm text-gray-600 mb-1">Review</label>
        <textarea
          value={body}
          onChange={e => setBody(e.target.value)}
          rows={3}
          placeholder="Tell future guests about your experience…"
          className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 resize-none"
        />
      </div>

      {formError && (
        <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded p-2">{formError}</p>
      )}

      <Button type="submit" disabled={isLoading}>
        {isLoading ? 'Submitting…' : 'Submit Review'}
      </Button>
    </form>
  );
};

export default ReviewForm;
