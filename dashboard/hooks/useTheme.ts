"use client";

import { useState, useEffect } from "react";

export function useTheme(): string {
  const [theme, setTheme] = useState<string>("light");

  useEffect(() => {
    function resolve(): string {
      const attr = document.documentElement.getAttribute("data-theme");
      if (attr === "light" || attr === "dark") return attr;
      return window.matchMedia("(prefers-color-scheme: dark)").matches
        ? "dark"
        : "light";
    }

    setTheme(resolve());

    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    const onMq = () => setTheme(resolve());
    mq.addEventListener("change", onMq);

    const observer = new MutationObserver(() => setTheme(resolve()));
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["data-theme"],
    });

    return () => {
      mq.removeEventListener("change", onMq);
      observer.disconnect();
    };
  }, []);

  return theme;
}
