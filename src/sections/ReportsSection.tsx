import { useEffect, useRef } from 'react';
import { FileText, Table } from 'lucide-react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

export function ReportsSection() {
  const sectionRef = useRef<HTMLElement>(null);
  const headlineRef = useRef<HTMLDivElement>(null);
  const reportsRef = useRef<HTMLDivElement>(null);
  const pdfBadgeRef = useRef<HTMLDivElement>(null);
  const csvBadgeRef = useRef<HTMLDivElement>(null);

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
        reportsRef.current,
        { x: '55vw', rotation: 4, opacity: 0 },
        { x: 0, rotation: 0, opacity: 1, ease: 'power2.out' },
        0.05
      );

      scrollTl.fromTo(
        pdfBadgeRef.current,
        { scale: 0.65, opacity: 0 },
        { scale: 1, opacity: 1, ease: 'power2.out' },
        0.15
      );

      scrollTl.fromTo(
        csvBadgeRef.current,
        { scale: 0.65, opacity: 0 },
        { scale: 1, opacity: 1, ease: 'power2.out' },
        0.2
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
        reportsRef.current,
        { x: 0, opacity: 1 },
        { x: '18vw', opacity: 0, ease: 'power2.in' },
        0.7
      );

      scrollTl.fromTo(
        [pdfBadgeRef.current, csvBadgeRef.current],
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
      className="relative w-full h-screen bg-[#F6F7FB] dot-grid overflow-hidden z-[70]"
    >
      {/* Headline Block */}
      <div
        ref={headlineRef}
        className="absolute left-[7vw] top-[28vh] w-[34vw] max-w-[520px] z-20"
      >
        <span className="inline-block text-xs font-semibold tracking-[0.08em] uppercase text-[#7B61FF] mb-4">
          Reports
        </span>
        <h2 className="font-display text-[clamp(32px,3.6vw,52px)] font-semibold leading-[1.0] tracking-[-0.02em] text-[#101114] mb-6">
          See the full
          <br />
          <span className="text-[#7B61FF]">picture.</span>
        </h2>
        <p className="text-lg text-[#6B6F7A] leading-relaxed max-w-[400px]">
          Monthly summaries, attendance trends, and export-ready data for your
          school.
        </p>
      </div>

      {/* Reports Card */}
      <div
        ref={reportsRef}
        className="absolute left-[58vw] top-1/2 transform -translate-y-1/2 w-[480px] lg:w-[540px] h-[360px] lg:h-[400px] bg-white rounded-[28px] card-shadow overflow-hidden"
      >
        <img
          src="/images/reports_ui.jpg"
          alt="Reports Dashboard"
          className="w-full h-full object-cover"
        />
      </div>

      {/* PDF Badge */}
      <div
        ref={pdfBadgeRef}
        className="absolute left-[86vw] top-[24vh] bg-white rounded-full px-4 py-2 card-shadow flex items-center gap-2 animate-float"
      >
        <FileText className="w-4 h-4 text-[#7B61FF]" />
        <span className="text-sm font-medium text-[#101114]">PDF</span>
      </div>

      {/* CSV Badge */}
      <div
        ref={csvBadgeRef}
        className="absolute left-[54vw] top-[70vh] bg-white rounded-full px-4 py-2 card-shadow flex items-center gap-2 animate-float"
        style={{ animationDelay: '1.5s' }}
      >
        <Table className="w-4 h-4 text-[#7B61FF]" />
        <span className="text-sm font-medium text-[#101114]">CSV</span>
      </div>
    </section>
  );
}
