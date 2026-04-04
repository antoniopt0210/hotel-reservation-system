import { useState } from 'react';

const Row = ({ label, value, bold = false }) => (
  <div className={`flex justify-between text-sm ${bold ? 'font-bold text-gray-800 text-base mt-1' : 'text-gray-600'}`}>
    <span>{label}</span>
    <span>{value}</span>
  </div>
);

const PriceBreakdown = ({ pricing }) => {
  const [expanded, setExpanded] = useState(false);

  if (!pricing) return null;
  const { nightly_rate, base_rate, nights, nightly_prices, subtotal, tax_rate, tax, total } = pricing;

  const hasDynamic = nightly_prices && nightly_prices.some(p => p.rate !== base_rate);

  return (
    <div className="bg-gray-50 border rounded-xl p-4 space-y-2">
      <h3 className="font-semibold text-gray-700 mb-3">Price breakdown</h3>

      <Row
        label={`~$${nightly_rate?.toFixed(2)} avg × ${nights} night${nights !== 1 ? 's' : ''}`}
        value={`$${subtotal.toFixed(2)}`}
      />

      {/* Expandable per-night detail */}
      {hasDynamic && nightly_prices && (
        <>
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-xs text-blue-600 hover:underline"
          >
            {expanded ? 'Hide nightly rates' : 'View nightly rates'}
          </button>
          {expanded && (
            <div className="space-y-1 pl-2 border-l-2 border-blue-200 ml-1">
              {nightly_prices.map(p => (
                <div key={p.date} className="flex justify-between text-xs text-gray-500">
                  <span>{p.date}</span>
                  <span className={p.rate !== base_rate ? 'text-orange-600 font-medium' : ''}>
                    ${p.rate.toFixed(2)}
                  </span>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      <Row label={`Taxes & fees (${(tax_rate * 100).toFixed(0)}%)`}
           value={`$${tax.toFixed(2)}`} />
      <div className="border-t my-2" />
      <Row label="Total" value={`$${total.toFixed(2)}`} bold />
    </div>
  );
};

export default PriceBreakdown;
