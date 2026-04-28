import { useEffect, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { ArrowRight, Calendar, Users, CreditCard, Video } from 'lucide-react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

function goTo(path: '/register') {
  window.history.pushState({}, '', path);
  window.dispatchEvent(new PopStateEvent('popstate'));
  window.scrollTo({ top: 0, behavior: 'instant' as ScrollBehavior });
}

gsap.registerPlugin(ScrollTrigger);

const orbitCards = [
  { icon: Calendar, label: 'Schedule', position: 'top-[12vh] left-[62vw]' },
  { icon: Users, label: 'Attendance', position: 'top-[30vh] left-[86vw]' },
  { icon: CreditCard, label: 'Payments', position: 'top-[66vh] left-[86vw]' },
  { icon: Video, label: 'Online', position: 'top-[80vh] left-[62vw]' },
];

export function HeroSection() {
  const sectionRef = useRef<HTMLElement>(null);
  const headlineRef = useRef<HTMLDivElement>(null);
  const orbitRef = useRef<HTMLDivElement>(null);
  const ringRef = useRef<HTMLDivElement>(null);
  const coreCardRef = useRef<HTMLDivElement>(null);
  const cardsRef = useRef<(HTMLDivElement | null)[]>([]);

  useEffect(() => {
    const ctx = gsap.context(() => {
      // Initial load animation
      const loadTl = gsap.timeline({ defaults: { ease: 'power3.out' } });

      // Headline entrance
      loadTl.fromTo(
        headlineRef.current,
        { x: '-40vw', opacity: 0 },
        { x: 0, opacity: 1, duration: 0.9 }
      );

      // Orbit ring entrance
      loadTl.fromTo(
        ringRef.current,
        { scale: 0.6, rotation: -25, opacity: 0 },
        { scale: 1, rotation: 0, opacity: 1, duration: 1, ease: 'back.out(1.2)' },
        '-=0.7'
      );

      // Core card entrance
      loadTl.fromTo(
        coreCardRef.current,
        { scale: 0.85, y: '8vh', opacity: 0 },
        { scale: 1, y: 0, opacity: 1, duration: 0.8 },
        '-=0.65'
      );

      // Orbit cards entrance
      cardsRef.current.forEach((card, i) => {
        if (card) {
          const directions = [
            { x: '-30vw', y: '-20vh' },
            { x: '30vw', y: '-20vh' },
            { x: '30vw', y: '20vh' },
            { x: '-30vw', y: '20vh' },
          ];
          loadTl.fromTo(
            card,
            { x: directions[i].x, y: directions[i].y, opacity: 0 },
            { x: 0, y: 0, opacity: 1, duration: 0.7 },
            `-=${0.62 - i * 0.08}`
          );
        }
      });

      // Scroll-driven exit animation
      const scrollTl = gsap.timeline({
        scrollTrigger: {
          trigger: sectionRef.current,
          start: 'top top',
          end: '+=130%',
          pin: true,
          scrub: 0.6,
          onLeaveBack: () => {
            // Reset all elements to visible when scrolling back
            gsap.set(headlineRef.current, { x: 0, opacity: 1 });
            gsap.set(orbitRef.current, { x: 0, scale: 1, opacity: 1 });
            gsap.set(ringRef.current, { rotation: 0 });
          },
        },
      });

      // EXIT phase (70-100%)
      scrollTl.fromTo(
        headlineRef.current,
        { x: 0, opacity: 1 },
        { x: '-18vw', opacity: 0, ease: 'power2.in' },
        0.7
      );

      scrollTl.fromTo(
        orbitRef.current,
        { x: 0, scale: 1, opacity: 1 },
        { x: '18vw', scale: 0.92, opacity: 0, ease: 'power2.in' },
        0.7
      );

      scrollTl.fromTo(
        ringRef.current,
        { rotation: 0 },
        { rotation: 45, ease: 'none' },
        0.7
      );
    }, sectionRef);

    return () => ctx.revert();
  }, []);

  return (
    <section
      ref={sectionRef}
      className="relative w-full h-screen bg-[#F6F7FB] dot-grid overflow-hidden z-10"
    >
      {/* Headline Block */}
      <div
        ref={headlineRef}
        className="absolute left-[7vw] top-[26vh] w-[38vw] max-w-[600px] z-20"
      >
        <h1 className="font-display text-[clamp(40px,5vw,72px)] font-semibold leading-[0.95] tracking-[-0.02em] text-[#101114] mb-6">
          Teach English.
          <br />
          <span className="text-[#7B61FF]">Smarter.</span>
        </h1>
        <p className="text-lg lg:text-xl text-[#6B6F7A] leading-relaxed mb-8 max-w-[480px]">
          Lexora is the all-in-one platform for teachers and language
          schools—scheduling, attendance, progress tracking, payments, and online
          lessons.
        </p>
        <div className="flex flex-wrap items-center gap-4">
          <Button
            className="bg-[#7B61FF] hover:bg-[#6B51EF] text-white rounded-full px-8 py-6 text-base font-medium"
            onClick={() => goTo('/register')}
          >
            Start free
          </Button>
          <button
            onClick={() => document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' })}
            className="flex items-center gap-2 text-[#6B6F7A] hover:text-[#101114] transition-colors font-medium"
          >
            See how it works
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Orbit System */}
      <div
        ref={orbitRef}
        className="absolute left-[72vw] top-[52vh] transform -translate-x-1/2 -translate-y-1/2"
      >
        {/* Orbit Ring */}
        <div
          ref={ringRef}
          className="absolute left-1/2 top-1/2 w-[520px] h-[520px] rounded-full border-2 border-[rgba(123,97,255,0.35)] transform -translate-x-1/2 -translate-y-1/2"
        />

        {/* Core Dashboard Card */}
        <div
          ref={coreCardRef}
          className="relative w-[260px] h-[320px] lg:w-[280px] lg:h-[340px] bg-white rounded-[28px] card-shadow overflow-hidden"
        >
          <img
            src="/images/dashboard_preview.jpg"
            alt="Lexora Dashboard"
            className="w-full h-full object-cover"
          />
        </div>

        {/* Floating Orbit Cards */}
        {orbitCards.map((card, index) => {
          const positions = [
            'top-[-80px] left-[-100px]',
            'top-[-40px] right-[-120px]',
            'bottom-[-60px] right-[-100px]',
            'bottom-[-80px] left-[-80px]',
          ];
          return (
            <div
              key={card.label}
              ref={(el) => { cardsRef.current[index] = el; }}
              className={`absolute ${positions[index]} w-[140px] h-[90px] lg:w-[160px] lg:h-[100px] bg-white rounded-[18px] card-shadow flex flex-col items-center justify-center gap-2 hover:scale-105 transition-transform cursor-pointer`}
            >
              <card.icon className="w-6 h-6 text-[#7B61FF]" />
              <span className="text-sm font-medium text-[#101114]">{card.label}</span>
            </div>
          );
        })}
      </div>
    </section>
  );
}
