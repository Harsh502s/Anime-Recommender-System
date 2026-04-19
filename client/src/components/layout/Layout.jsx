import { Outlet } from 'react-router';
import Navbar from './Navbar';
import Footer from './Footer';

export default function Layout() {
  return (
    <div className="min-h-screen flex flex-col relative overflow-hidden">
      {/* Background Mist Effects */}
      <div className="fixed top-0 left-0 w-full h-[500px] bg-[radial-gradient(ellipse_at_top_left,rgba(120,214,207,0.07),transparent_70%)] pointer-events-none z-0"></div>
      <div className="fixed bottom-0 right-0 w-full h-[500px] bg-[radial-gradient(ellipse_at_bottom_right,rgba(120,214,207,0.05),transparent_70%)] pointer-events-none z-0"></div>

      <Navbar />
      
      <main className="flex-grow pt-24 z-10">
        <Outlet />
      </main>
      
      <Footer />
    </div>
  );
}
