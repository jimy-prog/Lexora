import { useEffect, useRef } from 'react';
import { Award } from 'lucide-react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

export function StudentManagementSection() {
  const sectionRef = useRef<HTMLElement>(null);
  const headlineRef = useRef<HTMLDivElement>(null);
  const listRef = useRef<HTMLDivElement>(null);
  const profileRef = useRef<HTMLDivElement>(null);
  const badgeRef = useRef<HTMLDivElement>(null);

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
        listRef.current,
        { x: '60vw', opacity: 0 },
        { x: 0, opacity: 1, ease: 'power2.out' },
        0.05
      );

      scrollTl.fromTo(
        profileRef.current,
        { x: '70vw', y: '10vh', opacity: 0 },
        { x: 0, y: 0, opacity: 1, ease: 'power2.out' },
        0.1
      );

      scrollTl.fromTo(
        badgeRef.current,
        { scale: 0.6, opacity: 0 },
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
        [listRef.current, profileRef.current],
        { x: 0, opacity: 1 },
        { x: '-10vw', opacity: 0, ease: 'power2.in' },
        0.72
      );

      scrollTl.fromTo(
        badgeRef.current,
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
      className="relative w-full h-screen bg-[#F6F7FB] dot-grid overflow-hidden z-40"
    >
      {/* Headline Block */}
      <div
        ref={headlineRef}
        className="absolute left-[7vw] top-[28vh] w-[34vw] max-w-[520px] z-20"
      >
        <span className="inline-block text-xs font-semibold tracking-[0.08em] uppercase text-[#7B61FF] mb-4">
          Students & Groups
        </span>
        <h2 className="font-display text-[clamp(32px,3.6vw,52px)] font-semibold leading-[1.0] tracking-[-0.02em] text-[#101114] mb-6">
          Know every
          <br />
          <span className="text-[#7B61FF]">learner.</span>
        </h2>
        <p className="text-lg text-[#6B6F7A] leading-relaxed max-w-[400px]">
          Profiles, levels, contact history, and progress—all in one place.
        </p>
      </div>

      {/* Student List Card */}
      <div
        ref={listRef}
        className="absolute left-[58vw] top-[22vh] w-[280px] lg:w-[320px] h-[380px] lg:h-[420px] bg-white rounded-[28px] card-shadow overflow-hidden"
      >
        <img
          src="/images/student_list.jpg"
          alt="Student List"
          className="w-full h-full object-cover"
        />
      </div>

      {/* Profile Card */}
      <div
        ref={profileRef}
        className="absolute left-[78vw] top-[26vh] w-[240px] lg:w-[280px] h-[340px] lg:h-[380px] bg-white rounded-[28px] card-shadow overflow-hidden transform translate-x-[-60px]"
      >
        <img
          src="/images/student_profile.jpg"
          alt="Student Profile"
          className="w-full h-full object-cover"
        />
      </div>

      {/* Level Badge */}
      <div
        ref={badgeRef}
        className="absolute left-[54vw] top-[70vh] bg-white rounded-full px-4 py-2 card-shadow flex items-center gap-2"
      >
        <Award className="w-4 h-4 text-[#7B61FF]" />
        <span className="text-sm font-medium text-[#101114]">Level: B1</span>
      </div>
    </section>
  );
}
