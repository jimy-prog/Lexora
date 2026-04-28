import { useEffect, useRef } from 'react';
import { Video, BookOpen } from 'lucide-react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

export function OnlineLearningSection() {
  const sectionRef = useRef<HTMLElement>(null);
  const headlineRef = useRef<HTMLDivElement>(null);
  const onlineRef = useRef<HTMLDivElement>(null);
  const zoomBadgeRef = useRef<HTMLDivElement>(null);
  const homeworkRef = useRef<HTMLDivElement>(null);

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
        onlineRef.current,
        { x: '55vw', opacity: 0 },
        { x: 0, opacity: 1, ease: 'power2.out' },
        0.05
      );

      scrollTl.fromTo(
        zoomBadgeRef.current,
        { y: '-20vh', scale: 0.7, opacity: 0 },
        { y: 0, scale: 1, opacity: 1, ease: 'power2.out' },
        0.15
      );

      scrollTl.fromTo(
        homeworkRef.current,
        { y: '25vh', scale: 0.75, opacity: 0 },
        { y: 0, scale: 1, opacity: 1, ease: 'power2.out' },
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
        onlineRef.current,
        { x: 0, opacity: 1 },
        { x: '18vw', opacity: 0, ease: 'power2.in' },
        0.7
      );

      scrollTl.fromTo(
        [zoomBadgeRef.current, homeworkRef.current],
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
      className="relative w-full h-screen bg-[#F6F7FB] dot-grid overflow-hidden z-[80]"
    >
      {/* Headline Block */}
      <div
        ref={headlineRef}
        className="absolute left-[7vw] top-[28vh] w-[34vw] max-w-[520px] z-20"
      >
        <span className="inline-block text-xs font-semibold tracking-[0.08em] uppercase text-[#7B61FF] mb-4">
          Online Lessons
        </span>
        <h2 className="font-display text-[clamp(32px,3.6vw,52px)] font-semibold leading-[1.0] tracking-[-0.02em] text-[#101114] mb-6">
          Teach from
          <br />
          <span className="text-[#7B61FF]">anywhere.</span>
        </h2>
        <p className="text-lg text-[#6B6F7A] leading-relaxed max-w-[400px]">
          Zoom links, homework, materials, and messaging—integrated with your
          schedule.
        </p>
      </div>

      {/* Online Lesson Card */}
      <div
        ref={onlineRef}
        className="absolute left-[58vw] top-1/2 transform -translate-y-1/2 w-[480px] lg:w-[540px] h-[360px] lg:h-[400px] bg-white rounded-[28px] card-shadow overflow-hidden"
      >
        <img
          src="/images/online_lesson.jpg"
          alt="Online Learning"
          className="w-full h-full object-cover"
        />
      </div>

      {/* Zoom Badge */}
      <div
        ref={zoomBadgeRef}
        className="absolute left-[86vw] top-[22vh] bg-white rounded-full px-4 py-2 card-shadow flex items-center gap-2 animate-pulse-subtle"
      >
        <Video className="w-4 h-4 text-[#7B61FF]" />
        <span className="text-sm font-medium text-[#101114]">Zoom</span>
      </div>

      {/* Homework Card */}
      <div
        ref={homeworkRef}
        className="absolute left-[54vw] top-[68vh] w-[180px] lg:w-[200px] h-[100px] lg:h-[110px] bg-white rounded-[18px] card-shadow flex items-center gap-3 px-4 animate-float"
      >
        <div className="w-10 h-10 rounded-full bg-[#7B61FF]/10 flex items-center justify-center">
          <BookOpen className="w-5 h-5 text-[#7B61FF]" />
        </div>
        <div>
          <p className="text-xs text-[#6B6F7A]">Homework</p>
          <p className="text-sm font-semibold text-[#101114]">Assigned</p>
        </div>
      </div>
    </section>
  );
}
