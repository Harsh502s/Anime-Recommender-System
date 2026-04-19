import { useState, useEffect } from 'react';
import { Search, Zap, Shield, Eye, Skull, Activity, Filter, Loader2, Sparkles, Tv, Flame, Heart, Cpu, Ghost, Laugh, Compass, ChevronLeft, ChevronRight, ChevronDown } from 'lucide-react';
import api from '../lib/api';
import AnimeCard from '../components/ui/AnimeCard';

// Map common genres to icons
const getGenreIcon = (genreName) => {
  const map = {
    'action': Zap,
    'adventure': Compass,
    'comedy': Laugh,
    'sci-fi': Cpu,
    'shounen': Flame,
    'seinen': Eye,
    'horror': Skull,
    'romance': Heart,
    'supernatural': Ghost,
  };
  const key = genreName.toLowerCase();
  for (const [k, Icon] of Object.entries(map)) {
    if (key.includes(k)) return Icon;
  }
  return Tv; // Default
};

export default function DiscoverPage() {
  const [query, setQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  
  const [selectedGenre, setSelectedGenre] = useState('');
  const [allGenres, setAllGenres] = useState({ top: [], more: [] });
  const [showMoreFilters, setShowMoreFilters] = useState(false);
  
  const [trending, setTrending] = useState([]);
  const [isLoadingInitial, setIsLoadingInitial] = useState(true);

  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 8;

  // Debounced search for suggestions
  useEffect(() => {
    const fetchSuggestions = async () => {
      if (!query.trim() || query.length < 2) {
        setSuggestions([]);
        return;
      }
      try {
        const { data } = await api.get(`/anime?search=${encodeURIComponent(query.trim())}&limit=5`);
        setSuggestions(data?.data || []);
      } catch (err) {
        // Silently ignore autocomplete errors
      }
    };
    
    const timeoutId = setTimeout(fetchSuggestions, 250);
    return () => clearTimeout(timeoutId);
  }, [query]);

  // Fetch initial data
  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        const [animeRes, genresRes] = await Promise.all([
          api.get('/anime?limit=40'), // Fetch up to 40 for pagination
          api.get('/genres')
        ]);
        
        const fetchedTrending = animeRes.data?.data || [];
        setTrending(fetchedTrending);
        
        // Backend returns genres sorted by frequency
        const fetchedGenres = genresRes.data?.data || [];
        const top5 = fetchedGenres.slice(0, 5).map(name => ({ name, icon: getGenreIcon(name) }));
        const rest = fetchedGenres.slice(5).map(name => ({ name, icon: getGenreIcon(name) }));
        
        setAllGenres({ top: top5, more: rest });
      } catch (err) {
        console.error("Failed to load initial data", err);
      } finally {
        setIsLoadingInitial(false);
      }
    };
    fetchInitialData();
  }, []);

  const executeSearch = async (searchQuery) => {
    setIsSearching(true);
    setError(null);
    setResults(null);
    setCurrentPage(1);

    try {
      const { data } = await api.post('/recommend', { title: searchQuery.trim(), k: 40 });
      setResults(data.data);
    } catch (err) {
      if (err.response && err.response.status === 404) {
        setError(`Anime "${searchQuery}" not found in our database. Try falling back to partial names.`);
      } else {
        setError("An error occurred while generating recommendations.");
      }
    } finally {
      setIsSearching(false);
    }
  };

  const handleRecommend = async (e) => {
    if (e) e.preventDefault();
    if (!query.trim()) return;
    executeSearch(query.trim());
  };

  const handleGenreClick = async (genreName) => {
    setIsSearching(true);
    setError(null);
    setResults(null);
    setSelectedGenre(genreName);
    setQuery(''); // clear query when browsing genre
    setCurrentPage(1); // Reset page on genre click
    
    try {
      const { data } = await api.get(`/anime?genre=${encodeURIComponent(genreName)}&limit=40`);
      setResults({ seed: `Genre: ${genreName}`, recommendations: data?.data || [] });
    } catch (err) {
      setError("Failed to fetch animes by genre.");
    } finally {
      setIsSearching(false);
    }
  };

  const getDisplayedItems = () => {
    const arr = results ? results.recommendations : trending;
    return arr.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);
  };
  
  const getTotalPages = () => {
    const arr = results ? results.recommendations : trending;
    return Math.ceil(arr.length / itemsPerPage);
  };

  return (
    <div className="flex flex-col md:flex-row min-h-screen">
      {/* Sidebar Filter */}
      <aside className="w-full md:w-64 border-r border-outline-variant/30 glass-card p-6 flex flex-col pt-12 md:sticky md:top-20 md:h-[calc(100vh-80px)] z-10 shrink-0">
        <h2 className="text-sm font-bold tracking-widest uppercase mb-1">Filter Library</h2>
        <p className="text-xs text-on-surface-variant mb-8">Immersive Curation</p>
        
        <div className="flex flex-col space-y-2 flex-grow overflow-y-auto pr-2 custom-scrollbar">
          {isLoadingInitial ? (
             [1,2,3,4,5].map(i => <div key={i} className="h-10 bg-surface-container animate-pulse rounded-[12px] mb-2 w-full"></div>)
          ) : (
             <>
                {allGenres.top.map((g) => {
                  const Icon = g.icon;
                  const isActive = selectedGenre === g.name;
                  return (
                    <button
                      key={g.name}
                      onClick={() => handleGenreClick(g.name)}
                      className={`flex items-center gap-3 px-4 py-3 rounded-[16px] text-sm font-medium transition-all ${isActive ? 'gradient-primary text-on-primary shadow-lg shadow-primary/20 scale-105' : 'text-on-surface-variant hover:bg-surface-container hover:text-on-surface'}`}
                    >
                      <Icon size={18} />
                      {g.name}
                    </button>
                  )
                })}
                
                {allGenres.more.length > 0 && (
                   <div className="pt-4 border-t border-outline-variant/20 mt-2">
                      <button 
                         onClick={() => setShowMoreFilters(!showMoreFilters)}
                         className="flex items-center justify-between w-full px-4 py-2 text-xs text-on-surface-variant hover:text-on-surface transition-colors"
                      >
                        <span>More Filters</span>
                        <ChevronDown size={14} className={`transition-transform duration-300 ${showMoreFilters ? 'rotate-180': ''}`} />
                      </button>
                      
                      {showMoreFilters && (
                         <div className="mt-2 flex flex-col space-y-2">
                            {allGenres.more.map((g) => {
                              const Icon = g.icon;
                              const isActive = selectedGenre === g.name;
                              return (
                                <button
                                  key={g.name}
                                  onClick={() => handleGenreClick(g.name)}
                                  className={`flex items-center gap-3 px-4 py-2 rounded-[12px] text-xs text-left transition-colors ${isActive ? 'gradient-primary text-on-primary font-bold' : 'text-on-surface-variant hover:bg-surface-container hover:text-on-surface'}`}
                                >
                                  <Icon size={14} />
                                  {g.name}
                                </button>
                              )
                            })}
                         </div>
                      )}
                    </div>
                )}
             </>
          )}
        </div>

        <button 
           onClick={() => { setSelectedGenre(''); setResults(null); setQuery(''); setCurrentPage(1); }} 
           className="w-full border border-outline-variant text-on-surface font-bold py-3 rounded-[20px] mt-8 hover:bg-surface-container transition-colors cursor-pointer"
        >
          Clear Filters
        </button>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-6 md:p-12 relative z-10 overflow-hidden">
        <div className="max-w-5xl mx-auto">
          <div className="glass-card rounded-[20px] p-8 mb-12 shadow-[0_20px_40px_rgba(0,0,0,0.3)] border border-outline-variant/20">
            <h1 className="text-3xl font-display font-bold mb-6 flex items-center gap-3">
              <Sparkles className="text-primary" size={28} />
              Discover Your Next Masterpiece
            </h1>
            
            <form onSubmit={handleRecommend} className="flex flex-col md:flex-row gap-4 relative z-50">
              <div className="relative flex-1">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-on-surface-variant" size={20} />
                <input 
                  type="text" 
                  value={query}
                  onChange={(e) => {
                     setQuery(e.target.value);
                     setShowSuggestions(true);
                  }}
                  onFocus={() => setShowSuggestions(true)}
                  onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
                  placeholder="Enter a Seed Anime (e.g., Akira) for AI recs" 
                  className="w-full bg-surface-container border border-outline-variant/20 rounded-[20px] py-3 pl-12 pr-4 text-on-surface focus:outline-none focus:border-primary/50 focus:bg-surface-container-highest transition-colors"
                />
                
                {/* AUTOCOMPLETE DROPDOWN */}
                {showSuggestions && suggestions.length > 0 && (
                   <div className="absolute top-[calc(100%+8px)] left-0 right-0 bg-surface-container-high rounded-[16px] border border-outline-variant/30 shadow-[0_10px_40px_rgba(0,0,0,0.6)] overflow-hidden z-50 animate-in fade-in slide-in-from-top-2 duration-200">
                     {suggestions.map((anime, index) => (
                        <div 
                           key={`sugg-${anime.anime_id || index}`}
                           className="px-4 py-3 hover:bg-primary/20 cursor-pointer flex items-center gap-4 transition-colors border-b border-outline-variant/10 last:border-b-0"
                           onClick={() => {
                              setQuery(anime.title);
                              setShowSuggestions(false);
                              executeSearch(anime.title);
                           }}
                        >
                           <img 
                             src={anime.poster && anime.poster !== 'NA' ? anime.poster : 'https://placehold.co/80x120/191f2f/78d6cf?text=Anime'} 
                             alt={anime.title} 
                             className="w-10 h-14 object-cover rounded shadow-md shrink-0" 
                           />
                           <div className="min-w-0">
                              <div className="text-on-surface font-bold text-sm line-clamp-1">{anime.title}</div>
                              <div className="text-on-surface-variant text-[11px] mt-1 flex items-center gap-2">
                                {anime.score && anime.score !== "NA" && <span className="text-primary font-bold">★ {anime.score}</span>}
                                <span className="line-clamp-1">{Array.isArray(anime.genres) ? anime.genres.slice(0, 2).join(' • ') : anime.genres}</span>
                              </div>
                           </div>
                        </div>
                     ))}
                   </div>
                )}
              </div>
              
              <button 
                type="submit" 
                disabled={isSearching || !query.trim()}
                className="gradient-primary text-on-primary font-bold px-8 py-3 rounded-[20px] hover:scale-105 transition-transform disabled:opacity-50 disabled:hover:scale-100 flex items-center justify-center gap-2 whitespace-nowrap cursor-pointer z-10 relative"
              >
                {isSearching ? <Loader2 size={20} className="animate-spin" /> : <span>✨ Get Recommendation</span>}
              </button>
            </form>
            {error && <p className="text-error text-sm mt-4 bg-error/10 px-4 py-2 rounded-lg border border-error/20 inline-block">{error}</p>}
          </div>

          <div>
            <h2 className="text-2xl font-display font-bold mb-6">
              {results ? (
                 selectedGenre ? `Curated Matches for ${results.seed}` : `Recommendations built on "${results.seed}"`
              ) : "Trending Curations"}
            </h2>
            
            {(isSearching || isLoadingInitial) && (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                {[1,2,3,4,5,6,7,8].map(i => (
                  <div key={i} className="h-[300px] w-full bg-surface-container animate-pulse rounded-[20px]"></div>
                ))}
              </div>
            )}

            {!isSearching && !isLoadingInitial && (
               <>
                 <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                   {getDisplayedItems().map((rec, i) => (
                      <AnimeCard 
                        key={rec.anime_id} 
                        anime={rec} 
                        matchPercentage={results && !selectedGenre ? 99 - (((currentPage-1)*itemsPerPage + i) * 2) : null} 
                      />
                   ))}
                 </div>

                 {getTotalPages() > 1 && (
                    <div className="flex justify-center items-center gap-6 mt-12 bg-surface-container-high/50 p-4 rounded-full max-w-fit mx-auto border border-outline-variant/30 backdrop-blur-md">
                       <button 
                         onClick={() => {
                           setCurrentPage(p => Math.max(1, p - 1));
                           window.scrollTo({ top: 400, behavior: 'smooth' });
                         }}
                         disabled={currentPage === 1}
                         className="w-12 h-12 rounded-full bg-surface-container flex items-center justify-center disabled:opacity-30 disabled:cursor-not-allowed hover:bg-primary hover:text-on-primary transition-colors cursor-pointer shadow-lg"
                       >
                         <ChevronLeft size={24} />
                       </button>
                       <div className="flex items-center gap-2 font-display">
                         <span className="text-primary font-bold text-lg">{currentPage}</span>
                         <span className="text-on-surface-variant">/</span>
                         <span className="text-on-surface-variant font-medium">{getTotalPages()}</span>
                       </div>
                       <button 
                         onClick={() => {
                           setCurrentPage(p => Math.min(getTotalPages(), p + 1));
                           window.scrollTo({ top: 400, behavior: 'smooth' });
                         }}
                         disabled={currentPage === getTotalPages()}
                         className="w-12 h-12 rounded-full bg-surface-container flex items-center justify-center disabled:opacity-30 disabled:cursor-not-allowed hover:bg-primary hover:text-on-primary transition-colors cursor-pointer shadow-lg"
                       >
                         <ChevronRight size={24} />
                       </button>
                    </div>
                 )}
               </>
            )}
            
            {!isSearching && !isLoadingInitial && getDisplayedItems().length === 0 && (
               <div className="text-center py-20 text-on-surface-variant glass-card rounded-[20px]">
                 <Search size={48} className="mx-auto mb-4 opacity-50" />
                 <p>No titles found blending those parameters.</p>
               </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
