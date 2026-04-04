import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchAutocomplete } from '../../api/search';

const SearchAutocomplete = ({ value, onChange, checkIn, checkOut, guests }) => {
  const navigate = useNavigate();
  const [suggestions, setSuggestions] = useState([]);
  const [open, setOpen]     = useState(false);
  const timerRef = useRef(null);
  const wrapRef  = useRef(null);

  useEffect(() => {
    if (value.length < 2) { setSuggestions([]); return; }

    clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => {
      fetchAutocomplete(value)
        .then(d => { setSuggestions(d.suggestions || []); setOpen(true); })
        .catch(() => {});
    }, 250);

    return () => clearTimeout(timerRef.current);
  }, [value]);

  // Close dropdown on outside click
  useEffect(() => {
    const handler = (e) => {
      if (wrapRef.current && !wrapRef.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const pick = (s) => {
    setOpen(false);
    if (s.type === 'hotel') {
      navigate(`/hotels/${s.slug}?check_in=${checkIn}&check_out=${checkOut}&guests=${guests}`);
    } else {
      onChange(s.value);
    }
  };

  return (
    <div ref={wrapRef} className="relative">
      <input
        type="text"
        placeholder="City or hotel name"
        value={value}
        onChange={e => onChange(e.target.value)}
        onFocus={() => suggestions.length > 0 && setOpen(true)}
        className="border border-gray-300 rounded-md px-3 py-2 text-sm w-full focus:outline-none focus:ring-2 focus:ring-blue-400"
      />
      {open && suggestions.length > 0 && (
        <ul className="absolute z-50 top-full left-0 right-0 mt-1 bg-white border rounded-lg shadow-lg max-h-60 overflow-y-auto">
          {suggestions.map((s, i) => (
            <li
              key={i}
              onClick={() => pick(s)}
              className="px-3 py-2 hover:bg-blue-50 cursor-pointer flex items-center gap-2 text-sm"
            >
              <span className="text-gray-400 text-xs w-10 shrink-0">
                {s.type === 'city' ? 'City' : 'Hotel'}
              </span>
              <span className="text-gray-800">{s.value}</span>
              {s.city && s.type === 'hotel' && (
                <span className="text-gray-400 text-xs ml-auto">{s.city}</span>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default SearchAutocomplete;
