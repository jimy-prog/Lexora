import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Menu, X } from 'lucide-react';

function goTo(path: '/login' | '/register') {
  window.history.pushState({}, '', path);
  window.dispatchEvent(new PopStateEvent('popstate'));
  window.scrollTo({ top: 0, behavior: 'instant' as ScrollBehavior });
}

export function Navigation() {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToSection = (id: string) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
    setIsMobileMenuOpen(false);
  };

  return (
    <nav
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled
          ? 'bg-white/80 backdrop-blur-xl shadow-sm'
          : 'bg-transparent'
      }`}
    >
      <div className="w-full px-6 lg:px-12">
        <div className="flex items-center justify-between h-16 lg:h-20">
          {/* Logo */}
          <a
            href="#"
            className="font-display text-xl lg:text-2xl font-bold text-[#101114]"
          >
            Lexora
          </a>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-8">
            <button
              onClick={() => scrollToSection('features')}
              className="text-sm font-medium text-[#6B6F7A] hover:text-[#101114] transition-colors"
            >
              Product
            </button>
            <button
              onClick={() => scrollToSection('all-features')}
              className="text-sm font-medium text-[#6B6F7A] hover:text-[#101114] transition-colors"
            >
              Features
            </button>
            <button
              onClick={() => scrollToSection('cta')}
              className="text-sm font-medium text-[#6B6F7A] hover:text-[#101114] transition-colors"
            >
              Pricing
            </button>
            <a
              href="/login"
              onClick={(event) => {
                event.preventDefault();
                goTo('/login');
              }}
              className="text-sm font-medium text-[#6B6F7A] hover:text-[#101114] transition-colors"
            >
              Login
            </a>
            <Button
              className="bg-[#7B61FF] hover:bg-[#6B51EF] text-white rounded-full px-6"
              onClick={() => goTo('/register')}
            >
              Start free
            </Button>
          </div>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden p-2"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          >
            {isMobileMenuOpen ? (
              <X className="w-6 h-6 text-[#101114]" />
            ) : (
              <Menu className="w-6 h-6 text-[#101114]" />
            )}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      {isMobileMenuOpen && (
        <div className="md:hidden bg-white/95 backdrop-blur-xl border-t border-gray-100">
          <div className="px-6 py-4 space-y-4">
            <button
              onClick={() => scrollToSection('features')}
              className="block w-full text-left text-base font-medium text-[#6B6F7A] hover:text-[#101114]"
            >
              Product
            </button>
            <button
              onClick={() => scrollToSection('all-features')}
              className="block w-full text-left text-base font-medium text-[#6B6F7A] hover:text-[#101114]"
            >
              Features
            </button>
            <button
              onClick={() => scrollToSection('cta')}
              className="block w-full text-left text-base font-medium text-[#6B6F7A] hover:text-[#101114]"
            >
              Pricing
            </button>
            <a
              href="/login"
              onClick={(event) => {
                event.preventDefault();
                goTo('/login');
              }}
              className="block w-full text-left text-base font-medium text-[#6B6F7A] hover:text-[#101114]"
            >
              Login
            </a>
            <Button
              className="w-full bg-[#7B61FF] hover:bg-[#6B51EF] text-white rounded-full"
              onClick={() => goTo('/register')}
            >
              Start free
            </Button>
          </div>
        </div>
      )}
    </nav>
  );
}
