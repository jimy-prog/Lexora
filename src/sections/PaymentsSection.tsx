import { useEffect, useRef } from 'react';
import { Calculator, Download } from 'lucide-react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

export function PaymentsSection() {
  const sectionRef = useRef<HTMLElement>(null);
  const headlineRef = useRef<HTMLDivElement>(null);
  const paymentsRef = useRef<HTMLDivElement>(null);
  const badgeRef = useRef<HTMLDivElement>(null);
  const pillRef = useRef<HTMLDivElement>(null);

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
        paymentsRef.current,
        { x: '55vw', opacity: 0 },
        { x: 0, opacity: 1, ease: 'power2.out' },
        0.05
      );

      scrollTl.fromTo(
        badgeRef.current,
        { scale: 0.7, opacity: 0 },
        { scale: 1, opacity: 1, ease: 'power2.out' },
        0.15
      );

      scrollTl.fromTo(
        pillRef.current,
        { scale: 0.7, opacity: 0 },
        { scale: 1, opacity: 1, ease: 'power2.out' },
        0.25
      );

      // SETTLE (30-70%)

      // EXIT (70-100%)
      scrollTl.fromTo(
        headlineRef.current,
        { x: 0, opacity: 1 },
        { x: '-18vw', opacity: 0, ease: 'power2.in' },
        0.7
      );

      scrollTl.fromTo(
        paymentsRef.current,
        { x: 0, opacity: 1 },
        { x: '18vw', opacity: 0, ease: 'power2.in' },
        0.7
      );

      scrollTl.fromTo(
        [badgeRef.current, pillRef.current],
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
      className="relative w-full h-screen bg-[#F6F7FB] dot-grid overflow-hidden z-[60]"
    >
      {/* Headline Block */}
      <div
        ref={headlineRef}
        className="absolute left-[7vw] top-[28vh] w-[34vw] max-w-[520px] z-20"
      >
        <span className="inline-block text-xs font-semibold tracking-[0.08em] uppercase text-[#7B61FF] mb-4">
          Payments & Payrolls
        </span>
        <h2 className="font-display text-[clamp(32px,3.6vw,52px)] font-semibold leading-[1.0] tracking-[-0.02em] text-[#101114] mb-6">
          Get paid.
          <br />
          <span className="text-[#7B61FF]">On time.</span>
        </h2>
        <p className="text-lg text-[#6B6F7A] leading-relaxed max-w-[400px]">
          Student payments, teacher payrolls, and clear balances—without the
          manual math.
        </p>
      </div>

      {/* Payments Card */}
      <div
        ref={paymentsRef}
        className="absolute left-[58vw] top-1/2 transform -translate-y-1/2 w-[480px] lg:w-[540px] h-[360px] lg:h-[400px] bg-white rounded-[28px] card-shadow overflow-hidden"
      >
        <img
          src="/images/payments_ui.jpg"
          alt="Payments & Payroll"
          className="w-full h-full object-cover"
        />
      </div>

      {/* Auto-calc Badge */}
      <div
        ref={badgeRef}
        className="absolute left-[86vw] top-[22vh] bg-white rounded-full px-4 py-2 card-shadow flex items-center gap-2 animate-float"
      >
        <Calculator className="w-4 h-4 text-[#7B61FF]" />
        <span className="text-sm font-medium text-[#101114]">Auto-calc</span>
      </div>

      {/* Export Pill */}
      <div
        ref={pillRef}
        className="absolute left-[54vw] top-[70vh] bg-[#7B61FF] text-white rounded-full px-4 py-2 card-shadow flex items-center gap-2 animate-pulse-subtle"
      >
        <Download className="w-4 h-4" />
        <span className="text-sm font-medium">Export</span>
      </div>
    </section>
  );
}
