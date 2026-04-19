import { Dna, Palette, TrendingUp } from 'lucide-react';
import { Link } from 'react-router';

export default function AboutPage() {
  return (
    <div className="w-full flex-col flex gap-24 relative pb-24">
      {/* Hero Section */}
      <section className="px-8 pt-24 max-w-4xl mx-auto text-center relative z-10">
        <h1 className="text-4xl md:text-6xl font-display font-bold leading-tight mb-8">
          Curating the <br />
          <span className="text-gradient">Digital Proscenium</span>
        </h1>
        <p className="text-on-surface-variant text-lg leading-relaxed max-w-2xl mx-auto">
          Cinematic Canvas is more than an algorithm. It is a premium editorial space dedicated to treating anime as high art, guiding you through narratives that resonate with your personal aesthetic.
        </p>
      </section>

      {/* The Engine Section */}
      <section className="px-8 max-w-5xl mx-auto relative z-10">
        <div className="flex flex-col md:flex-row gap-12 items-start">
          <div className="md:w-1/3">
            <h2 className="text-2xl font-display font-bold mb-4">The Content-Based Engine</h2>
            <div className="w-12 h-1 bg-primary rounded-full mb-6"></div>
            <p className="text-on-surface-variant text-sm leading-relaxed">
              Our recommendation system abandons superficial genre-matching in favor of deep structural analysis. We examine the core DNA of what you watch.
            </p>
          </div>
          
          <div className="md:w-2/3 grid grid-cols-1 sm:grid-cols-2 gap-6">
            <div className="glass-card p-6 rounded-[20px] shadow-[0_10px_30px_rgba(0,0,0,0.2)]">
              <div className="w-10 h-10 rounded-full bg-surface-container flex items-center justify-center mb-4 text-primary">
                <Dna size={20} />
              </div>
              <h3 className="font-bold mb-2">Narrative DNA</h3>
              <p className="text-xs text-on-surface-variant leading-relaxed">
                We analyze thematic elements, character arcs, and pacing structures. If you appreciate slow-burn psychological thrillers, the engine prioritizes tension over mere action categorization.
              </p>
            </div>
            
            <div className="glass-card p-6 rounded-[20px] shadow-[0_10px_30px_rgba(0,0,0,0.2)]">
              <div className="w-10 h-10 rounded-full bg-surface-container flex items-center justify-center mb-4 text-primary">
                <Palette size={20} />
              </div>
              <h3 className="font-bold mb-2">Aesthetic Profiling</h3>
              <p className="text-xs text-on-surface-variant leading-relaxed">
                Visual language matters. The system evaluates color palettes, animation fluidity, and directorial style to ensure recommended titles match your visual appetite.
              </p>
            </div>
            
            <div className="glass-card p-6 rounded-[20px] shadow-[0_10px_30px_rgba(0,0,0,0.2)] sm:col-span-2">
              <div className="w-10 h-10 rounded-full bg-surface-container flex items-center justify-center mb-4 text-primary">
                <TrendingUp size={20} />
              </div>
              <h3 className="font-bold mb-2">Evolutionary Taste Tracking</h3>
              <p className="text-xs text-on-surface-variant leading-relaxed">
                Your preferences are not static. The content-based engine maps your journey, recognizing when you pivot from lighter slice-of-life narratives into darker, more complex thematic territories, adjusting its curation seamlessly.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* The Architect Section */}
      <section className="px-8 max-w-4xl mx-auto w-full relative z-10">
        <div className="glass-card rounded-[20px] p-8 md:p-12 shadow-[0_20px_40px_rgba(0,0,0,0.3)] flex flex-col md:flex-row items-center gap-10 border border-outline-variant/20">
          <div className="w-40 h-40 shrink-0 rounded-full overflow-hidden border-2 border-primary/30 p-1">
             {/* Using a placeholder avatar for Harshit */}
            <img 
              src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&q=80&w=400&h=400" 
              alt="Harshit Singh" 
              className="w-full h-full object-cover rounded-full"
            />
          </div>
          
          <div className="text-center md:text-left flex-1">
            <span className="text-[10px] tracking-widest font-bold uppercase text-primary mb-2 block">
              The Architect
            </span>
            <h2 className="text-3xl font-display font-bold mb-4">Harshit Singh</h2>
            <p className="text-sm text-on-surface-variant leading-relaxed mb-6">
              Driven by a passion for narrative structure and visual design, Harshit engineered Cinematic Canvas to bridge the gap between algorithmic utility and editorial curation. The goal was simple: build a space that respects the medium.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center md:justify-start">
              <Link to="#" className="border border-outline-variant text-on-surface text-sm font-bold px-6 py-2 rounded-[20px] hover:bg-surface-container-high transition-colors text-center">
                View Portfolio
              </Link>
              <Link to="#" className="gradient-primary text-on-primary text-sm font-bold px-6 py-2 rounded-[20px] hover:scale-105 transition-transform text-center">
                Contact
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
