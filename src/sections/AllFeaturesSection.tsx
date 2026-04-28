import { useEffect, useRef } from 'react';
import {
  Calendar,
  Users,
  CheckSquare,
  GraduationCap,
  CreditCard,
  Banknote,
  FileBarChart,
  Download,
  Video,
  BookOpen,
  Bell,
  UsersRound,
} from 'lucide-react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

const features = [
  { icon: Calendar, title: 'Calendar & Scheduling', description: 'Plan lessons with drag-and-drop simplicity' },
  { icon: UsersRound, title: 'Groups & Individual', description: 'Manage any class size or format' },
  { icon: CheckSquare, title: 'Attendance Tracking', description: 'Mark presence in seconds' },
  { icon: Users, title: 'Student Profiles', description: 'Complete learner information' },
  { icon: GraduationCap, title: 'Progress & Tests', description: 'Track improvement over time' },
  { icon: CreditCard, title: 'Payments & Invoices', description: 'Automated billing system' },
  { icon: Banknote, title: 'Teacher Payroll', description: 'Calculate salaries automatically' },
  { icon: FileBarChart, title: 'Monthly Reports', description: 'Insightful analytics' },
  { icon: Download, title: 'Export (PDF/CSV)', description: 'Share data easily' },
  { icon: Video, title: 'Online Lessons', description: 'Integrated Zoom support' },
  { icon: BookOpen, title: 'Homework & Materials', description: 'Share resources with students' },
  { icon: Bell, title: 'Notifications', description: 'Keep everyone informed' },
];

export function AllFeaturesSection() {
  const sectionRef = useRef<HTMLElement>(null);
  const titleRef = useRef<HTMLDivElement>(null);
  const cardsRef = useRef<(HTMLDivElement | null)[]>([]);

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.fromTo(
        titleRef.current,
        { y: 40, opacity: 0 },
        {
          y: 0,
          opacity: 1,
          duration: 0.8,
          ease: 'power2.out',
          scrollTrigger: {
            trigger: titleRef.current,
            start: 'top 80%',
            toggleActions: 'play none none reverse',
          },
        }
      );

      cardsRef.current.forEach((card, i) => {
        if (card) {
          gsap.fromTo(
            card,
            { y: 60, opacity: 0 },
            {
              y: 0,
              opacity: 1,
              duration: 0.6,
              delay: i * 0.08,
              ease: 'power2.out',
              scrollTrigger: {
                trigger: card,
                start: 'top 85%',
                toggleActions: 'play none none reverse',
              },
            }
          );
        }
      });
    }, sectionRef);

    return () => ctx.revert();
  }, []);

  return (
    <section
      ref={sectionRef}
      id="all-features"
      className="relative w-full bg-[#F6F7FB] dot-grid py-20 lg:py-32 z-[90]"
    >
      <div className="max-w-[980px] mx-auto px-6">
        <div ref={titleRef} className="text-center mb-12 lg:mb-16">
          <span className="inline-block text-xs font-semibold tracking-[0.08em] uppercase text-[#7B61FF] mb-4">
            Features
          </span>
          <h2 className="font-display text-[clamp(32px,3.6vw,52px)] font-semibold leading-[1.0] tracking-[-0.02em] text-[#101114] mb-4">
            A complete toolkit for
            <br />
            <span className="text-[#7B61FF]">language schools</span>
          </h2>
          <p className="text-lg text-[#6B6F7A]">Built by teachers, for teachers.</p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <div
              key={feature.title}
              ref={(el) => { cardsRef.current[index] = el; }}
              className="bg-white rounded-[22px] p-6 card-shadow hover:scale-[1.02] hover:shadow-lg transition-all duration-300 cursor-pointer group"
            >
              <div className="w-10 h-10 rounded-xl bg-[#7B61FF]/10 flex items-center justify-center mb-4 group-hover:bg-[#7B61FF] transition-colors">
                <feature.icon className="w-5 h-5 text-[#7B61FF] group-hover:text-white transition-colors" />
              </div>
              <h3 className="font-display text-lg font-semibold text-[#101114] mb-2">
                {feature.title}
              </h3>
              <p className="text-sm text-[#6B6F7A]">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
