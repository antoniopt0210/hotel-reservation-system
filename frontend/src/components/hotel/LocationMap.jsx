const LocationMap = ({ latitude, longitude, name }) => {
  if (!latitude || !longitude) return null;

  // OpenStreetMap embed — free, no API key needed
  const src = `https://www.openstreetmap.org/export/embed.html?bbox=${longitude - 0.01},${latitude - 0.005},${longitude + 0.01},${latitude + 0.005}&layer=mapnik&marker=${latitude},${longitude}`;

  return (
    <div className="rounded-xl overflow-hidden border">
      <iframe
        title={`Map showing ${name}`}
        src={src}
        width="100%"
        height="250"
        style={{ border: 0 }}
        loading="lazy"
        referrerPolicy="no-referrer-when-downgrade"
      />
      <div className="bg-gray-50 px-3 py-2 text-xs text-gray-500">
        <a
          href={`https://www.openstreetmap.org/?mlat=${latitude}&mlon=${longitude}#map=16/${latitude}/${longitude}`}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-600 hover:underline"
        >
          View larger map
        </a>
      </div>
    </div>
  );
};

export default LocationMap;
