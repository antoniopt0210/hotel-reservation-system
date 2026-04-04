import { useState, useEffect } from 'react';

const PhotoGalleryModal = ({ photos, initialIndex = 0, onClose }) => {
  const [index, setIndex] = useState(initialIndex);

  useEffect(() => {
    const handler = (e) => {
      if (e.key === 'Escape') onClose();
      if (e.key === 'ArrowLeft')  setIndex(i => (i - 1 + photos.length) % photos.length);
      if (e.key === 'ArrowRight') setIndex(i => (i + 1) % photos.length);
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [photos.length, onClose]);

  return (
    <div className="fixed inset-0 z-50 bg-black/90 flex items-center justify-center" onClick={onClose}>
      <div className="relative max-w-4xl w-full mx-4" onClick={e => e.stopPropagation()}>
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute -top-10 right-0 text-white/70 hover:text-white text-3xl z-10"
        >
          &times;
        </button>

        {/* Image */}
        <img
          src={photos[index]?.url}
          alt={photos[index]?.caption || ''}
          className="w-full max-h-[80vh] object-contain rounded-lg"
        />

        {/* Caption */}
        {photos[index]?.caption && (
          <p className="text-center text-white/70 text-sm mt-3">{photos[index].caption}</p>
        )}

        {/* Counter */}
        <p className="text-center text-white/50 text-xs mt-1">
          {index + 1} / {photos.length}
        </p>

        {/* Nav arrows */}
        {photos.length > 1 && (
          <>
            <button
              onClick={() => setIndex(i => (i - 1 + photos.length) % photos.length)}
              className="absolute left-2 top-1/2 -translate-y-1/2 bg-white/20 hover:bg-white/40 text-white rounded-full w-10 h-10 flex items-center justify-center text-xl"
            >
              ‹
            </button>
            <button
              onClick={() => setIndex(i => (i + 1) % photos.length)}
              className="absolute right-2 top-1/2 -translate-y-1/2 bg-white/20 hover:bg-white/40 text-white rounded-full w-10 h-10 flex items-center justify-center text-xl"
            >
              ›
            </button>
          </>
        )}
      </div>
    </div>
  );
};

export default PhotoGalleryModal;
