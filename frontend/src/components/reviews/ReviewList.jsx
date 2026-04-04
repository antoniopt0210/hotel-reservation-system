import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchReviews, fetchReviewSummary } from '../../api/reviews';
import StarRating from '../common/StarRating';
import Button from '../common/Button';

const RatingBar = ({ count, total, stars }) => {
  const pct = total > 0 ? Math.round((count / total) * 100) : 0;
  return (
    <div className="flex items-center gap-2 text-sm">
      <span className="w-4 text-gray-500">{stars}</span>
      <span className="text-yellow-400 text-xs">★</span>
      <div className="flex-1 bg-gray-100 rounded-full h-2">
        <div className="bg-yellow-400 h-2 rounded-full transition-all" style={{ width: `${pct}%` }} />
      </div>
      <span className="w-6 text-right text-gray-400 text-xs">{count}</span>
    </div>
  );
};

const ReviewList = ({ hotelId }) => {
  const [page, setPage] = useState(1);

  const { data: summary } = useQuery({
    queryKey: ['review-summary', hotelId],
    queryFn: () => fetchReviewSummary(hotelId),
  });

  const { data, isLoading } = useQuery({
    queryKey: ['reviews', hotelId, page],
    queryFn: () => fetchReviews(hotelId, page),
    keepPreviousData: true,
  });

  if (!summary && isLoading) return <p className="text-sm text-gray-400">Loading reviews…</p>;

  const total = summary?.total || 0;
  const avg   = summary?.avg_rating;

  return (
    <div className="space-y-6">
      {/* Summary strip */}
      <div className="flex flex-col sm:flex-row gap-6">
        <div className="flex flex-col items-center justify-center bg-blue-50 rounded-xl px-6 py-4 min-w-[100px]">
          <span className="text-4xl font-bold text-blue-700">{avg ? avg.toFixed(1) : '—'}</span>
          {avg && <StarRating rating={avg} size="sm" />}
          <span className="text-xs text-gray-500 mt-1">{total} review{total !== 1 ? 's' : ''}</span>
        </div>
        {total > 0 && (
          <div className="flex-1 space-y-1">
            {[5, 4, 3, 2, 1].map(s => (
              <RatingBar
                key={s}
                stars={s}
                count={summary?.breakdown?.[String(s)] || 0}
                total={total}
              />
            ))}
          </div>
        )}
      </div>

      {/* Review cards */}
      {total === 0 && (
        <p className="text-sm text-gray-400 italic">No reviews yet. Be the first to review!</p>
      )}

      {data?.reviews?.map(rv => (
        <div key={rv.id} className="border-b pb-4 last:border-0">
          <div className="flex items-center justify-between mb-1">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-blue-100 text-blue-700 rounded-full flex items-center justify-center text-sm font-bold">
                {rv.reviewer?.[0]?.toUpperCase() || 'G'}
              </div>
              <span className="font-medium text-gray-800 text-sm">{rv.reviewer}</span>
            </div>
            <StarRating rating={rv.rating} size="sm" />
          </div>
          {rv.title && <p className="font-semibold text-gray-700 text-sm">{rv.title}</p>}
          {rv.body  && <p className="text-gray-600 text-sm mt-1">{rv.body}</p>}
          <p className="text-xs text-gray-400 mt-1">
            {new Date(rv.created_at).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })}
          </p>
        </div>
      ))}

      {/* Pagination */}
      {data?.pages > 1 && (
        <div className="flex gap-2 justify-center pt-2">
          <Button variant="secondary" disabled={page <= 1} onClick={() => setPage(p => p - 1)}>← Prev</Button>
          <span className="text-sm text-gray-500 self-center">Page {page} of {data.pages}</span>
          <Button variant="secondary" disabled={page >= data.pages} onClick={() => setPage(p => p + 1)}>Next →</Button>
        </div>
      )}
    </div>
  );
};

export default ReviewList;
