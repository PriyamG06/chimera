"use client";

import * as Plot from "@observablehq/plot";
import { useEffect, useRef, useState } from "react";
import { MODELS, FRAUD_CEILING } from "@/app/data/chimera-results";
import { useTheme } from "@/hooks/useTheme";

const ACCENT_ID = "gemini-2.5-flash-lite";

const LABEL_OFFSETS: Record<string, { dx?: number; dy?: number; textAnchor?: string }> = {
  "claude-opus-4-8": { dx: -8, dy: -34, textAnchor: "end" },
  "gemini-3.8-flash": { dx: 8, dy: -34, textAnchor: "start" },
  "gpt-5.6-sol": { dx: 0, dy: -54, textAnchor: "middle" },
  "claude-haiku-4-5": { dx: 0, dy: 28, textAnchor: "middle" },
  "gpt-5-mini": { dx: 0, dy: 28, textAnchor: "middle" },
  "gemini-2.5-flash-lite": { dx: 0, dy: -18, textAnchor: "middle" },
};

interface PlotDatum {
  id: string;
  model: string;
  engWeeks: number;
  fraudLossRate: number;
  color: string;
  dx: number;
  dy: number;
  textAnchor: string;
}

export function FlailVsSolve() {
  const ref = useRef<HTMLDivElement>(null);
  const theme = useTheme();
  const [showTable, setShowTable] = useState(false);

  useEffect(() => {
    const container = ref.current;
    if (!container || showTable) return;
    container.innerHTML = "";

    const cs = getComputedStyle(document.documentElement);
    const accentColor = cs.getPropertyValue("--series-6").trim(); // flash-lite brand green
    const textPrimary = cs.getPropertyValue("--text-primary").trim();
    const textSecondary = cs.getPropertyValue("--text-secondary").trim();
    const textMuted = cs.getPropertyValue("--text-muted").trim();
    const gridline = cs.getPropertyValue("--gridline").trim();
    const baseline = cs.getPropertyValue("--baseline").trim();
    const surface1 = cs.getPropertyValue("--surface-1").trim();

    const plotData: PlotDatum[] = MODELS.map((m) => {
      const o = LABEL_OFFSETS[m.id] ?? {};
      return {
        id: m.id,
        model: m.label,
        engWeeks: m.engWeeks,
        fraudLossRate: m.fraudLossRate,
        color: m.id === ACCENT_ID ? accentColor || "#008300" : baseline || "#898781",
        dx: o.dx ?? 0,
        dy: o.dy ?? -12,
        textAnchor: o.textAnchor ?? "middle",
      };
    });

    const plot = Plot.plot({
      marginLeft: 58,
      marginRight: 20,
      marginTop: 20,
      marginBottom: 42,
      width: Math.max(container.offsetWidth || 820, 460),
      height: 360,
      style: { background: "transparent", color: textPrimary, fontFamily: "inherit", fontSize: "12px" },
      x: { domain: [-0.3, 7.5], label: "Engineering weeks to integrate →", grid: true, ticks: 6 },
      y: {
        domain: [0, 0.028],
        tickFormat: (d: number) => `${(d * 100).toFixed(1)}%`,
        label: "↑ Fraud loss rate",
        grid: true,
      },
      marks: [
        Plot.ruleX([0], { stroke: gridline }),
        Plot.ruleY([0], { stroke: gridline }),
        // fraud ceiling: a threshold reference, dashed by convention
        Plot.ruleY([FRAUD_CEILING], { stroke: textSecondary, strokeDasharray: "5,4", strokeWidth: 1.5 }),
        Plot.text([{ x: 7.4, y: FRAUD_CEILING }], {
          x: "x",
          y: "y",
          text: () => "fraud ceiling · 2.5%",
          dy: -7,
          textAnchor: "end",
          fill: textSecondary,
          fontSize: 11,
        }),
        // surface ring, then dot
        Plot.dot(plotData, { x: "engWeeks", y: "fraudLossRate", fill: surface1, r: 8 }),
        Plot.dot(plotData, {
          x: "engWeeks",
          y: "fraudLossRate",
          fill: (d: PlotDatum) => d.color,
          r: 6,
          tip: true,
          channels: {
            Model: "model",
            "Eng-weeks": "engWeeks",
            "Fraud loss": (d: PlotDatum) => `${(d.fraudLossRate * 100).toFixed(2)}%`,
          },
        }),
        ...plotData.map((d) =>
          Plot.text([d], {
            x: "engWeeks",
            y: "fraudLossRate",
            text: "model",
            dx: d.dx,
            dy: d.dy,
            textAnchor: d.textAnchor as "start" | "middle" | "end",
            fill: d.id === ACCENT_ID ? textPrimary : textMuted,
            fontSize: 11,
            fontWeight: d.id === ACCENT_ID ? 600 : 400,
          })
        ),
      ],
    });

    container.appendChild(plot);
    return () => plot.remove();
  }, [theme, showTable]);

  return (
    <div className="chart-card">
      <div className="chart-card__head">
        <div>
          <h3 className="chart-head">Flail vs. solve</h3>
          <p className="sub">
            Integration cost against fraud outcome. Five models spent the effort and cut the
            fraud lane to 0.8%; flash-lite spent almost nothing and left it at the 1.9% baseline,
            the closest to the ceiling but still under it.
          </p>
        </div>
        <button className="btn" onClick={() => setShowTable((t) => !t)} aria-pressed={showTable}>
          {showTable ? "Chart" : "Table"}
        </button>
      </div>

      <ul className="legend" aria-hidden="true">
        <li>
          <span className="swatch" style={{ background: "var(--series-6)", borderRadius: "50%" }} />
          Gemini 2.5 Flash Lite: left fraud unaddressed
        </li>
        <li>
          <span className="swatch" style={{ background: "var(--baseline)", borderRadius: "50%" }} />
          Other models: cut fraud to 0.8%
        </li>
      </ul>

      {showTable ? (
        <table className="data-table">
          <caption className="sr-only">Engineering weeks and fraud loss rate per model.</caption>
          <thead>
            <tr>
              <th scope="col">Model</th>
              <th scope="col">Eng-weeks</th>
              <th scope="col">Fraud loss</th>
              <th scope="col">Fraud addressed?</th>
            </tr>
          </thead>
          <tbody>
            {[...MODELS]
              .sort((a, b) => a.fraudLossRate - b.fraudLossRate)
              .map((m) => {
                const addressed = m.fraudLossRate <= 0.008;
                return (
                  <tr key={m.id}>
                    <td style={{ fontWeight: m.id === ACCENT_ID ? 600 : 400 }}>{m.label}</td>
                    <td>{m.engWeeks}</td>
                    <td>{(m.fraudLossRate * 100).toFixed(2)}%</td>
                    <td className={addressed ? "muted" : ""} style={{ fontWeight: addressed ? 400 : 600 }}>
                      {addressed ? "Yes" : "No"}
                    </td>
                  </tr>
                );
              })}
          </tbody>
        </table>
      ) : (
        <div ref={ref} className="viz viz--ynum" style={{ width: "100%" }} />
      )}
    </div>
  );
}
