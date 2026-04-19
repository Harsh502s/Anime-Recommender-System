import { Link } from 'react-router';

export default function Footer() {
  return (
    <footer className="w-full border-t border-outline-variant/30 py-8 mt-12 bg-surface text-xs text-on-surface-variant z-10">
      <div className="max-w-7xl mx-auto px-8 flex flex-col md:flex-row items-center justify-between">
        <div className="font-bold tracking-tight text-on-surface mb-4 md:mb-0">
          CINEMATIC CANVAS
        </div>
        
        <div className="flex space-x-6 uppercase tracking-wider mb-4 md:mb-0">
          <Link to="#" className="hover:text-primary transition-colors">ARCHIVES</Link>
          <Link to="#" className="hover:text-primary transition-colors">CURATORS</Link>
          <Link to="#" className="hover:text-primary transition-colors">LEGAL</Link>
          <Link to="#" className="hover:text-primary transition-colors">SUPPORT</Link>
        </div>
        
        <div className="text-on-surface-variant/70">
          © 2026 THE DIGITAL PROSCENIUM. ALL RIGHTS RESERVED.
        </div>
      </div>
    </footer>
  );
}
