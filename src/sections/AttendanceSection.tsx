import { useEffect, useRef } from 'react';
import { TrendingUp } from 'lucide-react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

export function AttendanceSection() {
  const sectionRef = useRef<HTMLElement>(null);
  const headlineRef = useRef<HTMLDivElement>(null);
  const attendanceRef = useRef<HTMLDivElement>(null);
  const miniReportRef = useRef<HTMLDivElement>(null);

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
        attendanceRef.current,
        { x: '55vw', rotation: -5, opacity: 0 },
        { x: 0, rotation: 0, opacity: 1, ease: 'power2.out' },
        0.05
      );

      scrollTl.fromTo(
        miniReportRef.current,
        { y: '30vh', scale: 0.75, opacity: 0 },
        { y: 0, scale: 1, opacity: 1, ease: 'power2.out' },
        0.15
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
        attendanceRef.current,
        { x: 0, opacity: 1 },
        { x: '18vw', opacity: 0, ease: 'power2.in' },
        0.7
      );

      scrollTl.fromTo(
        miniReportRef.current,
        { y: 0, opacity: 1 },
        { y: '10vh', opacity: 0, ease: 'power2.in' },
        0.72
      );
    }, sectionRef);

    return () => ctx.revert();
  }, []);

  return (
    <section
      ref={sectionRef}
      className="relative w-full h-screen bg-[#F6F7FB] dot-grid overflow-hidden z-50"
    >
      {/* Headline Block */}
      <div
        ref={headlineRef}
        className="absolute left-[7vw] top-[28vh] w-[34vw] max-w-[520px] z-20"
      >
        <span className="inline-block text-xs font-semibold tracking-[0.08em] uppercase text-[#7B61FF] mb-4">
          Attendance & Progress
        </span>
        <h2 className="font-display text-[clamp(32px,3.6vw,52px)] font-semibold leading-[1.0] tracking-[-0.02em] text-[#101114] mb-6">
          Track what
          <br />
          <span className="text-[#7B61FF]">matters.</span>
        </h2>
        <p className="text-lg text-[#6B6F7A] leading-relaxed max-w-[400px]">
          Mark attendance in seconds. See progress at a glance.
        </p>
      </div>

      {/* Attendance Card */}
      <div
        ref={attendanceRef}
        className="absolute left-[58vw] top-[22vh] w-[480px] lg:w-[540px] h-[360px] lg:h-[400px] bg-white rounded-[28px] card-shadow overflow-hidden"
      >
        <img
          src="/images/attendance_ui.jpg"
          alt="Attendance Tracking"
          className="w-full h-full object-cover"
        />
      </div>

      {/* Mini Report Card */}
      <div
        ref={miniReportRef}
        className="absolute left-[54vw] top-[68vh] w-[180px] lg:w-[200px] h-[100px] lg:h-[110px] bg-white rounded-[18px] card-shadow flex items-center gap-3 px-4 animate-float"
      >
        <div className="w-10 h-10 rounded-full bg-[#7B61FF]/10 flex items-center justify-center">
          <TrendingUp className="w-5 h-5 text-[#7B61FF]" />
        </div>
        <div>
          <p className="text-xs text-[#6B6F7A]">Weekly Report</p>
          <p className="text-lg font-semibold text-[#101114]">94%</p>
        </div>
      </div>
    </section>
  );
}
