import { useEffect, useState } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { ArrowLeft } from 'lucide-react';
import { Navigation } from './components/Navigation';
import { HeroSection } from './sections/HeroSection';
import { FeatureOrbitSection } from './sections/FeatureOrbitSection';
import { SchedulingSection } from './sections/SchedulingSection';
import { StudentManagementSection } from './sections/StudentManagementSection';
import { AttendanceSection } from './sections/AttendanceSection';
import { PaymentsSection } from './sections/PaymentsSection';
import { ReportsSection } from './sections/ReportsSection';
import { OnlineLearningSection } from './sections/OnlineLearningSection';
import { AllFeaturesSection } from './sections/AllFeaturesSection';
import { CTAFooterSection } from './sections/CTAFooterSection';
import { useAuth } from './context/AuthContext';

gsap.registerPlugin(ScrollTrigger);

type RoutePath = '/' | '/login' | '/register' | '/dashboard';

function navigateTo(path: RoutePath) {
  window.history.pushState({}, '', path);
  window.dispatchEvent(new PopStateEvent('popstate'));
  window.scrollTo({ top: 0, behavior: 'instant' as ScrollBehavior });
}

function AuthPage({ mode }: { mode: 'login' | 'register' }) {
  const isRegister = mode === 'register';
  const { login } = useAuth();
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError('');
    
    if (isRegister) {
      alert('Registration endpoint is next!');
      return;
    }

    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ identifier, password })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Login failed');
      
      login(data.user);
      navigateTo('/dashboard');
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div className="min-h-screen bg-[#f6f7fb] px-6 py-8">
      <div className="mx-auto flex max-w-6xl items-center justify-between pb-8">
        <button
          onClick={() => navigateTo('/')}
          className="inline-flex items-center gap-2 text-sm font-medium text-[#6B6F7A] transition-colors hover:text-[#101114]"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to home
        </button>
        <div className="font-display text-2xl font-semibold text-[#101114]">Lexora</div>
      </div>

      <div className="mx-auto grid max-w-6xl overflow-hidden rounded-[32px] bg-white shadow-[0_30px_80px_rgba(16,17,20,0.08)] lg:grid-cols-[1.1fr_0.9fr]">
        <div className="hidden bg-[#101114] p-10 text-white lg:flex lg:flex-col lg:justify-between">
          <div>
            <div className="mb-6 inline-flex rounded-full border border-white/15 px-4 py-2 text-xs uppercase tracking-[0.2em] text-white/70">
              Lexora access
            </div>
            <h1 className="font-display text-5xl leading-[0.95] tracking-[-0.03em]">
              {isRegister ? 'Create your teaching workspace.' : 'Welcome back inside Lexora.'}
            </h1>
            <p className="mt-6 max-w-md text-base leading-7 text-white/70">
              {isRegister
                ? 'This is the first access layer for your future online school. New users can create an account and continue into the platform.'
                : 'Sign in to continue into the platform, review classes, and manage your system from one place.'}
            </p>
          </div>
        </div>

        <div className="p-8 sm:p-10">
          <div className="mb-8">
            <div className="font-display text-4xl leading-none tracking-[-0.03em] text-[#101114]">
              {isRegister ? 'Create account' : 'Sign in'}
            </div>
            <p className="mt-3 text-sm leading-6 text-[#6B6F7A]">
              We have now connected the login endpoint.
            </p>
          </div>

          <form className="space-y-5" onSubmit={handleSubmit}>
            {error && (
              <div className="rounded-xl bg-red-50 p-4 text-xs font-medium text-red-600">
                {error}
              </div>
            )}
            {isRegister && (
              <div className="space-y-2">
                <label className="text-xs font-semibold uppercase tracking-[0.18em] text-[#6B6F7A]">
                  Full name
                </label>
                <input
                  className="w-full rounded-2xl border border-[#E6E8F0] bg-[#F8F9FC] px-4 py-4 outline-none transition focus:border-[#7B61FF]"
                  placeholder="Jamshid Mahkamov"
                />
              </div>
            )}

            <div className="space-y-2">
              <label className="text-xs font-semibold uppercase tracking-[0.18em] text-[#6B6F7A]">
                {isRegister ? 'Email' : 'Username or email'}
              </label>
              <input
                value={identifier}
                onChange={(e) => setIdentifier(e.target.value)}
                className="w-full rounded-2xl border border-[#E6E8F0] bg-[#F8F9FC] px-4 py-4 outline-none transition focus:border-[#7B61FF]"
                placeholder={isRegister ? 'teacher@lexora.app' : 'owner@lexora.local'}
              />
            </div>

            <div className="space-y-2">
              <label className="text-xs font-semibold uppercase tracking-[0.18em] text-[#6B6F7A]">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full rounded-2xl border border-[#E6E8F0] bg-[#F8F9FC] px-4 py-4 outline-none transition focus:border-[#7B61FF]"
                placeholder="••••••••"
              />
            </div>

            <button type="submit" className="w-full rounded-full bg-[#7B61FF] px-6 py-4 text-sm font-semibold text-white transition hover:bg-[#6B51EF]">
              {isRegister ? 'Create account' : 'Continue'}
            </button>
          </form>

          <div className="mt-6 text-sm text-[#6B6F7A]">
            {isRegister ? 'Already have an account?' : 'Need a new account?'}{' '}
            <button
              type="button"
              className="font-semibold text-[#7B61FF]"
              onClick={() => navigateTo(isRegister ? '/login' : '/register')}
            >
              {isRegister ? 'Sign in' : 'Register'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function LandingPage() {
  useEffect(() => {
    const timer = setTimeout(() => {
      const pinned = ScrollTrigger.getAll()
        .filter((st) => st.vars.pin)
        .sort((a, b) => a.start - b.start);

      const maxScroll = ScrollTrigger.maxScroll(window);

      if (!maxScroll || pinned.length === 0) return;

      const pinnedRanges = pinned.map((st) => ({
        start: st.start / maxScroll,
        end: (st.end ?? st.start) / maxScroll,
        center: (st.start + ((st.end ?? st.start) - st.start) * 0.5) / maxScroll,
      }));

      ScrollTrigger.create({
        snap: {
          snapTo: (value) => {
            const inPinned = pinnedRanges.some(
              (r) => value >= r.start - 0.02 && value <= r.end + 0.02
            );

            if (!inPinned) return value;

            return pinnedRanges.reduce(
              (closest, r) =>
                Math.abs(r.center - value) < Math.abs(closest - value) ? r.center : closest,
              pinnedRanges[0]?.center ?? 0
            );
          },
          duration: { min: 0.15, max: 0.35 },
          delay: 0,
          ease: 'power2.out',
        },
      });
    }, 500);

    return () => {
      clearTimeout(timer);
      ScrollTrigger.getAll().forEach((st) => st.kill());
    };
  }, []);

  return (
    <div className="relative">
      <Navigation />
      <main className="relative">
        <HeroSection />
        <FeatureOrbitSection />
        <SchedulingSection />
        <StudentManagementSection />
        <AttendanceSection />
        <PaymentsSection />
        <ReportsSection />
        <OnlineLearningSection />
        <AllFeaturesSection />
        <CTAFooterSection />
      </main>
    </div>
  );
}

function DashboardPage() {
  const { user, logout } = useAuth();
  
  if (!user) {
    navigateTo('/login');
    return null;
  }

  return (
    <div className="min-h-screen bg-[#F8F9FC] p-8">
      <div className="mx-auto max-w-6xl rounded-3xl bg-white p-8 shadow-sm">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-display font-semibold text-[#101114]">Welcome back, {user.full_name || user.username}</h1>
            <p className="text-[#6B6F7A]">Logged in as {user.role}</p>
          </div>
          <button 
            onClick={logout}
            className="rounded-full bg-[#F6F7FB] px-6 py-3 text-sm font-semibold text-[#101114] transition hover:bg-[#E6E8F0]"
          >
            Sign out
          </button>
        </div>
        
        <div className="grid grid-cols-3 gap-6">
          <div className="rounded-2xl border border-[#E6E8F0] p-6">
            <h3 className="font-semibold text-[#101114] mb-2">Lexora Architecture</h3>
            <p className="text-sm text-[#6B6F7A]">You have successfully connected the React frontend to the FastAPI + SQLite backend.</p>
          </div>
          <div className="rounded-2xl border border-[#E6E8F0] p-6">
            <h3 className="font-semibold text-[#101114] mb-2">Phase 4 Active</h3>
            <p className="text-sm text-[#6B6F7A]">You are looking at the new Student Portal foundation layer.</p>
          </div>
        </div>
      </div>
    </div>
  );
}

function App() {
  const { loading } = useAuth();

  const getPath = () => {
    const path = window.location.pathname as RoutePath;
    if (path === '/login' || path === '/register' || path === '/dashboard') return path;
    return '/';
  };

  const [path, setPath] = useState<RoutePath>(getPath);

  useEffect(() => {
    const handlePopState = () => setPath(getPath());
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  if (loading) return <div className="min-h-screen flex items-center justify-center">Loading context...</div>;

  if (path === '/login') return <AuthPage mode="login" />;
  if (path === '/register') return <AuthPage mode="register" />;
  if (path === '/dashboard') return <DashboardPage />;
  return <LandingPage />;
}

export default App;
