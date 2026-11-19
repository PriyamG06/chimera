"use client";

import * as Plot from "@observablehq/plot";
import { useEffect, useRef, useState } from "react";
import { MODELS, DIM_MAXES } from "@/app/data/chimera-results";
import { useTheme } from "@/hooks/useTheme";

const DIMS = ["investigation", "execution", "outcomes", "safety"] as const;
type Dim = (typeof DIMS)[number];

const DIM_LABELS: Record<Dim, string> = {
  investigation: "Investigation",
  execution: "Execution",
  outcomes: "Outcomes",
  safety: "Safety",
};

interface PlotDatum {
  model: string;
  dim: string;
  value: number;
  raw: number;
  max: number;
  color: string;
}

const SORTED = [...MODELS].sort((a, b) => b.total - a.total);

export function ScoreRadar() {
  const ref = useRef<HTMLDivElement>(null);
  const theme = useTheme();
  const [showTable, setShowTable] = useState(false);

  useEffect(() => {
    const container = ref.current;
    if (!container || showTable) return;
    container.innerHTML = "";

    const cs = getComputedStyle(document.documentElement);
    const resolvedColors = Object.fromEntries(
      MODELS.map((m) => [m.id, cs.getPropertyValue(m.colorVar).trim()])
    );
    const textPrimary = cs.getPropertyValue("--text-primary").trim();
    const textMuted = cs.getPropertyValue("--text-muted").trim();
    const gridline = cs.getPropertyValue("--gridline").trim();
    const monoFont = cs.getPropertyValue("--font-mono").trim() || "monospace";

    const plotData: PlotDatum[] = SORTED.flatMap((m) =>
      DIMS.map((dim) => ({
        model: m.label,
        dim: DIM_LABELS[dim],
        value: m.scorecard[dim] / DIM_MAXES[dim],
        raw: m.scorecard[dim],
        max: DIM_MAXES[dim],
        color: resolvedColors[m.id] || "#888",
      }))
    );

    const plot = Plot.plot({
      marginLeft: 96,
      marginRight: 128,
      marginTop: 8,
      marginBottom: 28,
      width: Math.max(container.offsetWidth || 820, 460),
      style: { background: "transparent", color: textPrimary, fontFamily: "inherit", fontSize: "12px" },
      fy: { domain: SORTED.map((m) => m.label), label: null },
      x: {
        domain: [0, 1],
        tickFormat: (d: number) => `${Math.round(d * 100)}%`,
        label: "Score (% of dimension max)",
        grid: true,
        ticks: 4,
      },
      y: { domain: ["Safety", "Outcomes", "Execution", "Investigation"], label: null },
      marks: [
        Plot.ruleX([0], { stroke: gridline }),
        Plot.barX(plotData, {
          x: "value",
          y: "dim",
          fy: "model",
          fill: (d: PlotDatum) => d.color,
          rx: 3,
          tip: true,
          channels: { Model: "model", Dimension: "dim", Score: (d: PlotDatum) => `${d.raw} / ${d.max}` },
        }),
        Plot.text(plotData, {
          x: "value",
          y: "dim",
          fy: "model",
          text: (d: PlotDatum) => `${d.raw}/${d.max}`,
          dx: 6,
          textAnchor: "start",
          fill: textMuted,
          fontSize: 10.5,
          fontFamily: monoFont,
        }),
      ],
    });

    container.appendChild(plot);
    return () => plot.remove();
  }, [theme, showTable]);

  return (
    <div className="chart-card">
      <div className="chart-card__head">
        <div>
          <h3 className="chart-head">Per-model scorecard profile</h3>
          <p className="sub">
            The four deterministic dimensions as a share of their own max: one panel per model,
            ordered by total. Shows where each model earned, or lost, its deterministic points.
          </p>
        </div>
        <button className="btn" onClick={() => setShowTable((t) => !t)} aria-pressed={showTable}>
          {showTable ? "Chart" : "Table"}
        </button>
      </div>

      {showTable ? (
        <table className="data-table">
          <caption className="sr-only">Deterministic scorecard dimensions per model.</caption>
          <thead>
            <tr>
              <th scope="col">Model</th>
              <th scope="col">Investigation (12)</th>
              <th scope="col">Execution (20)</th>
              <th scope="col">Outcomes (10)</th>
              <th scope="col">Safety (10)</th>
              <th scope="col">Det total (52)</th>
            </tr>
          </thead>
          <tbody>
            {SORTED.map((m) => (
              <tr key={m.id}>
                <td>{m.label}</td>
                <td>{m.scorecard.investigation}</td>
                <td>{m.scorecard.execution}</td>
                <td>{m.scorecard.outcomes}</td>
                <td>{m.scorecard.safety}</td>
                <td style={{ fontWeight: 600 }}>{m.scorecard.detSubtotal.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <div ref={ref} className="viz" style={{ width: "100%" }} />
      )}
    </div>
  );
}
