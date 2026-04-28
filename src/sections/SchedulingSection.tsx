import { useEffect, useRef } from 'react';
import { Repeat, Move } from 'lucide-react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

export function SchedulingSection() {
  const sectionRef = useRef<HTMLElement>(null);
  const headlineRef = useRef<HTMLDivElement>(null);
  const calendarRef = useRef<HTMLDivElement>(null);
  const badge1Ref = useRef<HTMLDivElement>(null);
  const badge2Ref = useRef<HTMLDivElement>(null);

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
        calendarRef.current,
        { x: '55vw', rotation: 6, opacity: 0 },
        { x: 0, rotation: 0, opacity: 1, ease: 'power2.out' },
        0
      );

      scrollTl.fromTo(
        badge1Ref.current,
        { scale: 0.7, opacity: 0 },
        { scale: 1, opacity: 1, ease: 'power2.out' },
        0.15
      );

      scrollTl.fromTo(
        badge2Ref.current,
        { scale: 0.7, opacity: 0 },
        { scale: 1, opacity: 1, ease: 'power2.out' },
        0.25
      );

      // SETTLE (30-70%) - floating animation handled by CSS

      // EXIT (70-100%)
      scrollTl.fromTo(
        headlineRef.current,
        { x: 0, opacity: 1 },
        { x: '-18vw', opacity: 0, ease: 'power2.in' },
        0.7
      );

      scrollTl.fromTo(
        calendarRef.current,
        { x: 0, opacity: 1 },
        { x: '18vw', opacity: 0, ease: 'power2.in' },
        0.7
      );

      scrollTl.fromTo(
        [badge1Ref.current, badge2Ref.current],
        { opacity: 1 },
        { opacity: 0, ease: 'power2.in' },
        0.75
      );
    }, sectionRef);

    return () => ctx.revert();
  }, []);

  return (
    <section
      ref={sectionRef}
      className="relative w-full h-screen bg-[#F6F7FB] dot-grid overflow-hidden z-30"
    >
      {/* Headline Block */}
      <div
        ref={headlineRef}
        className="absolute left-[7vw] top-[28vh] w-[34vw] max-w-[520px] z-20"
      >
        <span className="inline-block text-xs font-semibold tracking-[0.08em] uppercase text-[#7B61FF] mb-4">
          Scheduling
        </span>
        <h2 className="font-display text-[clamp(32px,3.6vw,52px)] font-semibold leading-[1.0] tracking-[-0.02em] text-[#101114] mb-6">
          Plan lessons in
          <br />
          <span className="text-[#7B61FF]">minutes.</span>
        </h2>
        <p className="text-lg text-[#6B6F7A] leading-relaxed max-w-[400px]">
          Recurring groups, individual slots, holidays, and room bookings—without
          the back-and-forth.
        </p>
      </div>

      {/* Calendar Visual */}
      <div
        ref={calendarRef}
        className="absolute left-[58vw] top-1/2 transform -translate-y-1/2"
      >
        <div className="relative w-[480px] h-[380px] lg:w-[520px] lg:h-[420px] bg-white rounded-[28px] card-shadow overflow-hidden">
          <img
            src="/images/calendar_ui.jpg"
            alt="Calendar Scheduling"
            className="w-full h-full object-cover"
          />
        </div>
      </div>

      {/* Floating Badges */}
      <div
        ref={badge1Ref}
        className="absolute left-[54vw] top-[18vh] bg-white rounded-full px-4 py-2 card-shadow flex items-center gap-2 animate-float"
      >
        <Repeat className="w-4 h-4 text-[#7B61FF]" />
        <span className="text-sm font-medium text-[#101114]">Recurring</span>
      </div>

      <div
        ref={badge2Ref}
        className="absolute left-[78vw] top-[72vh] bg-white rounded-full px-4 py-2 card-shadow flex items-center gap-2 animate-float"
        style={{ animationDelay: '1s' }}
      >
        <Move className="w-4 h-4 text-[#7B61FF]" />
        <span className="text-sm font-medium text-[#101114]">Drag to reschedule</span>
      </div>
    </section>
  );
}
