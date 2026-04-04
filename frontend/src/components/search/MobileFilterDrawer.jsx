import { useState } from 'react';
import StarRating from '../common/StarRating';
import Button from '../common/Button';

const MobileFilterDrawer = ({
  amenities,
  minPrice, setMinPrice,
  maxPrice, setMaxPrice,
  selectedStars, toggleStar,
  selectedAmenities, toggleAmenity,
  sort, setSort,
  onApply,
}) => {
  const [open, setOpen] = useState(false);

  const apply = () => { setOpen(false); onApply(); };

  return (
    <>
      {/* Trigger button — only visible on mobile */}
      <button
        onClick={() => setOpen(true)}
        className="md:hidden flex items-center gap-1 border rounded-lg px-3 py-2 text-sm text-gray-600 hover:bg-gray-50"
      >
        <span>Filters</span>
        {(selectedStars.length > 0 || selectedAmenities.length > 0 || minPrice || maxPrice) && (
          <span className="bg-blue-600 text-white text-xs rounded-full px-1.5">
            {selectedStars.length + selectedAmenities.length + (minPrice ? 1 : 0) + (maxPrice ? 1 : 0)}
          </span>
        )}
      </button>

      {/* Backdrop */}
      {open && (
        <div className="fixed inset-0 bg-black/40 z-40 md:hidden" onClick={() => setOpen(false)} />
      )}

      {/* Drawer */}
      <div className={`fixed inset-y-0 left-0 z-50 w-72 bg-white shadow-xl transform transition-transform duration-300 md:hidden ${open ? 'translate-x-0' : '-translate-x-full'}`}>
        <div className="flex items-center justify-between p-4 border-b">
          <h3 className="font-bold text-gray-700">Filters</h3>
          <button onClick={() => setOpen(false)} className="text-gray-400 hover:text-gray-600 text-xl">&times;</button>
        </div>

        <div className="p-4 space-y-6 overflow-y-auto h-[calc(100%-120px)]">
          {/* Sort */}
          <div>
            <p className="text-sm font-semibold text-gray-600 mb-2">Sort by</p>
            <select value={sort} onChange={e => setSort(e.target.value)}
              className="w-full border rounded px-3 py-1 text-sm">
              <option value="rating_desc">Top rated</option>
              <option value="price_asc">Price: low to high</option>
              <option value="price_desc">Price: high to low</option>
            </select>
          </div>

          {/* Price */}
          <div>
            <p className="text-sm font-semibold text-gray-600 mb-2">Price / night</p>
            <div className="flex gap-2 items-center">
              <input type="number" placeholder="Min" value={minPrice}
                onChange={e => setMinPrice(e.target.value)}
                className="w-full border rounded px-2 py-1 text-sm" />
              <span className="text-gray-400">-</span>
              <input type="number" placeholder="Max" value={maxPrice}
                onChange={e => setMaxPrice(e.target.value)}
                className="w-full border rounded px-2 py-1 text-sm" />
            </div>
          </div>

          {/* Stars */}
          <div>
            <p className="text-sm font-semibold text-gray-600 mb-2">Star rating</p>
            {[5, 4, 3, 2, 1].map(s => (
              <label key={s} className="flex items-center gap-2 cursor-pointer mb-1">
                <input type="checkbox" checked={selectedStars.includes(s)}
                  onChange={() => toggleStar(s)} />
                <StarRating rating={s} size="sm" />
              </label>
            ))}
          </div>

          {/* Amenities */}
          {amenities.length > 0 && (
            <div>
              <p className="text-sm font-semibold text-gray-600 mb-2">Amenities</p>
              {amenities.map(a => (
                <label key={a.id} className="flex items-center gap-2 cursor-pointer mb-1 text-sm text-gray-700">
                  <input type="checkbox" checked={selectedAmenities.includes(a.id)}
                    onChange={() => toggleAmenity(a.id)} />
                  {a.name}
                </label>
              ))}
            </div>
          )}
        </div>

        <div className="p-4 border-t">
          <Button className="w-full" onClick={apply}>Apply Filters</Button>
        </div>
      </div>
    </>
  );
};

export default MobileFilterDrawer;
