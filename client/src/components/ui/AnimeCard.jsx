import { Play, Star, Calendar, Info } from 'lucide-react';

export default function AnimeCard({ anime, matchPercentage, size = 'default' }) {
  if (!anime) return null;

  const dimensions = {
    small: 'h-[200px]',
    default: 'h-[320px]',
    large: 'h-[420px]',
  };

  const genres = Array.isArray(anime.genres) 
    ? anime.genres 
    : anime.genres?.replace(/\[|\]|'/g, '').split(',').map(s => s.trim()) || [];

  return (
    <div className="relative group perspective-1000">
      <a 
        href={anime.urls && anime.urls !== 'NA' ? anime.urls : '#'} 
        target={anime.urls && anime.urls !== 'NA' ? '_blank' : '_self'}
        rel="noopener noreferrer"
        className={`block relative rounded-[16px] overflow-hidden cursor-pointer transition-all duration-300 group-hover:scale-105 group-hover:-translate-y-2 group-hover:shadow-[0_20px_50px_rgba(0,0,0,0.5)] z-10 bg-surface-container ${dimensions[size]}`}
      >
        {/* Background Image */}
        <div 
          className="absolute inset-0 bg-cover bg-center blur-2xl opacity-40 scale-110 z-0"
          style={{ backgroundImage: `url(${anime.poster && anime.poster !== 'NA' ? anime.poster : ''})` }}
        />
        
        <img 
          src={anime.poster && anime.poster !== 'NA' ? anime.poster.replace('200x280', '500x700') : 'https://placehold.co/400x600/191f2f/78d6cf?text=No+Poster'} 
          alt={anime.title}
          onError={(e) => { 
             if (anime.poster && anime.poster !== 'NA' && e.target.src !== anime.poster) {
                e.target.src = anime.poster; 
                e.target.className = "w-full h-full object-cover relative z-10 transition-transform duration-500";
             }
          }}
          className="w-full h-full object-cover relative z-10 transition-transform duration-500"
          loading="lazy"
        />

        <div className="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent z-20 pointer-events-none opacity-80" />

        {/* Basic Overlay Info */}
        <div className="absolute bottom-0 left-0 w-full p-4 z-30 pointer-events-none">
           {matchPercentage && (
             <div className="mb-2">
               <span className="bg-primary/20 text-primary text-[10px] uppercase font-bold px-2 py-1 rounded-full border border-primary/20 backdrop-blur-md">
                 {matchPercentage}% Match
               </span>
             </div>
           )}
           <h3 className="text-white font-display font-bold text-base leading-tight line-clamp-1 group-hover:hidden">
             {anime.title}
           </h3>
        </div>
      </a>

      {/* FLOATING DETAIL WINDOW (NETFLIX STYLE) */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[340px] opacity-0 pointer-events-none group-hover:opacity-100 group-hover:pointer-events-auto transition-all duration-300 z-50 group-hover:scale-110 group-hover:-translate-y-[60%]">
        <div className="glass-card bg-surface-container-high/95 p-5 rounded-[24px] shadow-[0_30px_70px_rgba(0,0,0,0.8)] border border-white/10 backdrop-blur-2xl">
          <div className="relative h-40 mb-4 rounded-xl overflow-hidden">
             <img src={anime.poster} className="w-full h-full object-cover blur-sm opacity-50 absolute inset-0" />
             <div className="absolute inset-0 bg-gradient-to-t from-surface-container-high to-transparent" />
             <div className="absolute bottom-4 left-4 right-4">
                <h4 className="text-white font-bold text-xl line-clamp-2 leading-tight drop-shadow-lg">{anime.title}</h4>
             </div>
          </div>

          <div className="flex items-center gap-4 mb-4">
             <div className="flex items-center gap-1 text-primary font-bold">
               <Star size={16} fill="currentColor" />
               <span>{anime.score !== 'NA' ? anime.score : 'N/A'}</span>
             </div>
             <div className="text-[11px] text-on-surface-variant font-medium uppercase tracking-wider flex items-center gap-2">
               <Info size={14} />
               <span className="line-clamp-1">{Array.isArray(anime.anime_studio) ? anime.anime_studio[0] : anime.anime_studio || 'Generic Studio'}</span>
             </div>
          </div>

          <p className="text-on-surface-variant text-xs leading-relaxed line-clamp-3 mb-6 italic">
            "{anime.overview !== 'NA' ? anime.overview : 'No synopsis available for this title.'}"
          </p>

          <div className="flex gap-2 mb-4">
             {genres.slice(0, 3).map(g => (
               <span key={g} className="text-[10px] px-2 py-1 bg-white/5 border border-white/10 rounded-md text-on-surface-variant uppercase tracking-tighter">
                 {g}
               </span>
             ))}
          </div>

          <a 
            href={anime.urls && anime.urls !== 'NA' ? anime.urls : '#'} 
            target="_blank"
            className="w-full gradient-primary text-on-primary font-bold py-3 rounded-xl flex items-center justify-center gap-2 hover:brightness-110 transition-all shadow-lg shadow-primary/20 text-sm"
          >
            <Play size={16} fill="white" />
            Watch Now
          </a>
        </div>
      </div>
    </div>
  );
}

