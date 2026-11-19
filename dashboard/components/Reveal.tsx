"use client";

import { useEffect, useRef, useState, type ReactNode } from "react";

interface RevealProps {
  children: ReactNode;
  delay?: number;
  as?: "div" | "section" | "li";
  className?: string;
  id?: string;
}

/**
 * Fades + lifts its children into view the first time they enter the viewport.
 * Load-time elements near the top show immediately (observer fires on mount).
 * Respects prefers-reduced-motion via the .reveal CSS rules.
 */
export function Reveal({
  children,
  delay = 0,
  as = "div",
  className = "",
  id,
}: RevealProps) {
  const ref = useRef<HTMLElement>(null);
  const [shown, setShown] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const io = new IntersectionObserver(
      (entries) => {
        for (const e of entries) {
          if (e.isIntersecting) {
            setShown(true);
            io.disconnect();
          }
        }
      },
      { threshold: 0.12, rootMargin: "0px 0px -8% 0px" }
    );
    io.observe(el);
    // Safety net: if a section is never scrolled into view (print, crawlers,
    // full-page capture), still reveal it so content is never stuck hidden.
    const t = window.setTimeout(() => {
      setShown(true);
      io.disconnect();
    }, 1400);
    return () => {
      io.disconnect();
      window.clearTimeout(t);
    };
  }, []);

  const Tag = as as "div";
  return (
    <Tag
      ref={ref as React.Ref<HTMLDivElement>}
      id={id}
      className={`reveal ${className}`}
      data-shown={shown ? "true" : "false"}
      style={delay ? { animationDelay: `${delay}ms` } : undefined}
    >
      {children}
    </Tag>
  );
}
