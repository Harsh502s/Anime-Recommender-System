import { useState, useEffect } from 'react';
import { Link } from 'react-router';
import AnimeCard from '../components/ui/AnimeCard';
import api from '../lib/api';

export default function HomePage() {
  const [curated, setCurated] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchCurated = async () => {
      try {
        const { data } = await api.get('/anime?limit=3');
        setCurated(data?.data || []);
      } catch (err) {
        console.error("Failed to fetch curated anime", err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchCurated();
  }, []);

  return (
    <div className="w-full flex-col flex gap-24 relative">
      <section className="relative px-8 pt-12 lg:pt-24 min-h-[70vh] flex flex-col justify-center items-center text-center">
        {/* Placeholder Hero Background Image directly in code */}
        <div className="absolute inset-0 z-0 opacity-40">
           <img 
              src="https://images.unsplash.com/photo-1578632767115-351597cf2477?auto=format&fit=crop&q=80&w=2000" 
              className="w-full h-full object-cover object-top mask-image-b"
              style={{ maskImage: 'linear-gradient(to bottom, black 40%, transparent 100%)', WebkitMaskImage: 'linear-gradient(to bottom, black 40%, transparent 100%)' }}
              alt="Anime Hero Background" />
        </div>
        
        <div className="relative z-10 max-w-4xl mx-auto flex flex-col items-center">
          <span className="text-[10px] tracking-[0.2em] font-bold uppercase text-primary border border-primary/30 px-3 py-1 rounded-full mb-6 bg-surface-container/50 backdrop-blur-md">
            Featured Premiere
          </span>
          <h1 className="text-5xl md:text-7xl font-display font-bold leading-tight mb-6">
            Discover Your Next <br/> 
            <span className="text-gradient">Obsession</span>
          </h1>
          <p className="max-w-xl text-on-surface-variant mb-10 text-lg">
            Step into the digital proscenium. Curated masterpieces of animation,
            meticulously selected to push the boundaries of storytelling and visual art.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4">
            <Link to="/discover" className="gradient-primary text-on-primary font-bold px-8 py-3 rounded-[20px] hover:scale-105 transition-transform flex items-center justify-center gap-2">
              <div className="w-2 h-2 bg-on-primary rounded-full animate-pulse"></div>
              Start Watching
            </Link>
            <Link to="/about" className="border border-outline-variant text-on-surface font-bold px-8 py-3 rounded-[20px] hover:bg-surface-container-high transition-colors text-center">
              About the Engine
            </Link>
          </div>
        </div>
      </section>
      
      <section className="max-w-7xl mx-auto px-8 w-full">
        <div className="flex justify-between items-end mb-8">
          <div>
            <h2 className="text-3xl font-display font-bold mb-1">Curated For You</h2>
            <p className="text-xs text-on-surface-variant uppercase tracking-wider">Based on your cinematic taste</p>
          </div>
          <Link to="/discover" className="text-primary text-sm font-bold hover:underline">View All</Link>
        </div>
        
        {isLoading ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 h-[400px] bg-surface-container animate-pulse rounded-[20px]"></div>
            <div className="flex flex-col gap-6">
               <div className="h-[200px] bg-surface-container animate-pulse rounded-[20px]"></div>
               <div className="h-[200px] bg-surface-container animate-pulse rounded-[20px]"></div>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                 <AnimeCard 
                    anime={(curated && curated[0]) || { title: "Neon Resonance", genres: ['Sci-Fi', 'Psychological'], poster: "https://images.unsplash.com/photo-1541562232579-512a21360020?auto=format&fit=crop&q=80&w=800" }} 
                    matchPercentage={96} size="large" />
              </div>
              <div className="flex flex-col gap-6">
                  <AnimeCard 
                     anime={(curated && curated[1]) || { title: "Crimson Protocol", genres: ['Action', 'Thriller'], poster: "https://images.unsplash.com/photo-1560972550-aba3456b5564?auto=format&fit=crop&q=80&w=800" }} 
                     matchPercentage={92} size="small" />
                  <AnimeCard 
                     anime={(curated && curated[2]) || { title: "Ethereal Shift", genres: ['Fantasy', 'Drama'], poster: "https://images.unsplash.com/photo-1614583225154-5fc20fbcf394?auto=format&fit=crop&q=80&w=800" }} 
                     matchPercentage={88} size="small" />
              </div>
          </div>
        )}
      </section>
      
      <section className="pb-24 max-w-7xl mx-auto px-8 w-full text-center">
         <h3 className="text-lg font-bold mb-6">Explore Atmospheres</h3>
         <div className="flex flex-wrap justify-center gap-3">
            {['All Atmospheres', 'Cyberpunk Dystopia', 'Ethereal Fantasy', 'Gritty Realism', 'Cosmic Horror', 'Urban Noir'].map((atm, i) => (
                <button key={atm} className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${i === 0 ? 'gradient-primary text-on-primary' : 'bg-surface-container-highest text-on-surface border border-outline-variant hover:border-primary/50'}`}>
                    {atm}
                </button>
            ))}
         </div>
      </section>
    </div>
  );
}
