import { useEffect, useRef } from 'react';
import { ArrowRight, Calendar, Users, UsersRound, CheckSquare, CreditCard, BarChart3 } from 'lucide-react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

const featureCards = [
  { icon: Calendar, label: 'Calendar' },
  { icon: Users, label: 'Students' },
  { icon: UsersRound, label: 'Groups' },
  { icon: CheckSquare, label: 'Attendance' },
  { icon: CreditCard, label: 'Payments' },
  { icon: BarChart3, label: 'Reports' },
];

export function FeatureOrbitSection() {
  const sectionRef = useRef<HTMLElement>(null);
  const headlineRef = useRef<HTMLDivElement>(null);
  const orbitRef = useRef<HTMLDivElement>(null);
  const ringRef = useRef<HTMLDivElement>(null);
  const coreCardRef = useRef<HTMLDivElement>(null);
  const cardsRef = useRef<(HTMLDivElement | null)[]>([]);

  useEffect(() => {
    const ctx = gsap.context(() => {
      const scrollTl = gsap.timeline({
        scrollTrigger: {
          trigger: sectionRef.current,
          start: 'top top',
          end: '+=130%',
          pin: true,
          scrub: 0.6,
        },
      });

      // ENTRANCE (0-30%)
      scrollTl.fromTo(
        headlineRef.current,
        { x: '-55vw', opacity: 0 },
        { x: 0, opacity: 1, ease: 'power2.out' },
        0
      );

      scrollTl.fromTo(
        ringRef.current,
        { scale: 0.55, rotation: -70, opacity: 0 },
        { scale: 1, rotation: 0, opacity: 1, ease: 'power2.out' },
        0
      );

      scrollTl.fromTo(
        coreCardRef.current,
        { scale: 0.75, y: '18vh', opacity: 0 },
        { scale: 1, y: 0, opacity: 1, ease: 'power2.out' },
        0.05
      );

      cardsRef.current.forEach((card, i) => {
        if (card) {
          scrollTl.fromTo(
            card,
            { x: `${i % 2 === 0 ? '-' : '+'}60vw`, y: `${i < 2 ? '-' : '+'}70vh`, opacity: 0 },
            { x: 0, y: 0, opacity: 1, ease: 'power2.out' },
            0.06 + i * 0.02
          );
        }
      });

      // SETTLE (30-70%) - subtle ring rotation
      scrollTl.fromTo(
        ringRef.current,
        { rotation: 0 },
        { rotation: 8, ease: 'none' },
        0.3
      );

      // EXIT (70-100%)
      scrollTl.fromTo(
        headlineRef.current,
        { x: 0, opacity: 1 },
        { x: '-18vw', opacity: 0, ease: 'power2.in' },
        0.7
      );

      scrollTl.fromTo(
        orbitRef.current,
        { x: 0, scale: 1, opacity: 1 },
        { x: '18vw', scale: 0.9, opacity: 0, ease: 'power2.in' },
        0.7
      );

      cardsRef.current.forEach((card, i) => {
        if (card) {
          scrollTl.fromTo(
            card,
            { x: 0, y: 0, opacity: 1 },
            { x: `${i % 2 === 0 ? '-' : '+'}10vw`, y: `${i < 3 ? '-' : '+'}10vh`, opacity: 0, ease: 'power2.in' },
            0.72 + i * 0.02
          );
        }
      });
    }, sectionRef);

    return () => ctx.revert();
  }, []);

  return (
    <section
      ref={sectionRef}
      id="features"
      className="relative w-full h-screen bg-[#F6F7FB] dot-grid overflow-hidden z-20"
    >
      {/* Headline Block */}
      <div
        ref={headlineRef}
        className="absolute left-[7vw] top-[26vh] w-[36vw] max-w-[560px] z-20"
      >
        <span className="inline-block text-xs font-semibold tracking-[0.08em] uppercase text-[#7B61FF] mb-4">
          All-in-One Platform
        </span>
        <h2 className="font-display text-[clamp(32px,3.6vw,52px)] font-semibold leading-[1.0] tracking-[-0.02em] text-[#101114] mb-6">
          Everything you need.
          <br />
          <span className="text-[#6B6F7A]">Nothing you don't.</span>
        </h2>
        <p className="text-lg text-[#6B6F7A] leading-relaxed mb-8 max-w-[420px]">
          Plan lessons, track attendance, manage students, and get paid—without
          the spreadsheet chaos.
        </p>
        <button
          onClick={() => document.getElementById('all-features')?.scrollIntoView({ behavior: 'smooth' })}
          className="flex items-center gap-2 text-[#7B61FF] hover:text-[#6B51EF] transition-colors font-medium"
        >
          Explore features
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>

      {/* Orbit System */}
      <div
        ref={orbitRef}
        className="absolute left-[72vw] top-[52vh] transform -translate-x-1/2 -translate-y-1/2"
      >
        {/* Orbit Ring */}
        <div
          ref={ringRef}
          className="absolute left-1/2 top-1/2 w-[560px] h-[560px] rounded-full border-2 border-[rgba(123,97,255,0.35)] transform -translate-x-1/2 -translate-y-1/2"
        />

        {/* Core Dashboard Card */}
        <div
          ref={coreCardRef}
          className="relative w-[280px] h-[340px] lg:w-[300px] lg:h-[360px] bg-white rounded-[28px] card-shadow overflow-hidden"
        >
          <img
            src="/images/dashboard_preview.jpg"
            alt="Lexora Dashboard"
            className="w-full h-full object-cover"
          />
        </div>

        {/* Floating Feature Cards */}
        {featureCards.map((card, index) => {
          const angle = (index * 60 - 90) * (Math.PI / 180);
          const radius = 320;
          const x = Math.cos(angle) * radius;
          const y = Math.sin(angle) * radius;
          
          return (
            <div
              key={card.label}
              ref={(el) => { cardsRef.current[index] = el; }}
              className="absolute w-[130px] h-[85px] lg:w-[150px] lg:h-[100px] bg-white rounded-[18px] card-shadow flex flex-col items-center justify-center gap-2 hover:scale-105 transition-transform cursor-pointer"
              style={{
                left: `calc(50% + ${x}px - 75px)`,
                top: `calc(50% + ${y}px - 50px)`,
              }}
            >
              <card.icon className="w-5 h-5 lg:w-6 lg:h-6 text-[#7B61FF]" />
              <span className="text-xs lg:text-sm font-medium text-[#101114]">{card.label}</span>
            </div>
          );
        })}
      </div>
    </section>
  );
}
