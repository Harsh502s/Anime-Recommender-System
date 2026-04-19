import { NavLink } from 'react-router';
import { User, Bell } from 'lucide-react';

export default function Navbar() {
  return (
    <nav className="fixed top-0 w-full z-50 glass-card border-b border-outline-variant/30 px-8 py-4">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <NavLink to="/" className="text-xl font-bold tracking-tight">
          CINEMATIC CANVAS
        </NavLink>
        
        <div className="hidden md:flex items-center space-x-8 text-sm font-medium">
          <NavLink 
            to="/" 
            className={({ isActive }) => `uppercase text-xs tracking-wider transition-colors ${isActive ? 'text-primary' : 'text-on-surface-variant hover:text-on-surface'}`}
          >
            Home
          </NavLink>
          <NavLink 
            to="/discover" 
            className={({ isActive }) => `uppercase text-xs tracking-wider transition-colors ${isActive ? 'text-primary' : 'text-on-surface-variant hover:text-on-surface'}`}
          >
            Discover
          </NavLink>
          <NavLink 
            to="/about" 
            className={({ isActive }) => `uppercase text-xs tracking-wider transition-colors ${isActive ? 'text-primary' : 'text-on-surface-variant hover:text-on-surface'}`}
          >
            About
          </NavLink>
        </div>

        <div className="flex items-center space-x-4">
          <button className="p-2 text-on-surface-variant hover:text-primary transition-colors cursor-pointer">
            <Bell size={20} />
          </button>
          <button className="p-2 text-on-surface-variant hover:text-primary transition-colors cursor-pointer rounded-full bg-surface-container">
            <User size={20} />
          </button>
        </div>
      </div>
    </nav>
  );
}
