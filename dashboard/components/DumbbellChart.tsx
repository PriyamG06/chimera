"use client";

import * as Plot from "@observablehq/plot";
import { useEffect, useRef, useState } from "react";
import { MODELS, DET_MAX, JUDGE_MAX } from "@/app/data/chimera-results";
import { useTheme } from "@/hooks/useTheme";

interface PlotDatum {
  model: string;
  detNorm: number;
  judgeNorm: number;
  detRaw: number;
  judgeRaw: number;
  total: number;
  color: string;
}

const SORTED_MODELS = [...MODELS].sort((a, b) => b.total - a.total);
const STORY_ID = "gpt-5.6-sol"; // top judge score, mid-pack deterministic checks

export function DumbbellChart() {
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
    const surface1 = cs.getPropertyValue("--surface-1").trim();

    const plotData: PlotDatum[] = SORTED_MODELS.map((m) => ({
      model: m.label,
      detNorm: m.scorecard.detSubtotal / DET_MAX,
      judgeNorm: m.judgeTotal / JUDGE_MAX,
      detRaw: m.scorecard.detSubtotal,
      judgeRaw: m.judgeTotal,
      total: m.total,
      color: resolvedColors[m.id] || "#888",
    }));

    const sortedLabels = SORTED_MODELS.map((m) => m.label);
    const storyLabel = MODELS.find((m) => m.id === STORY_ID)?.label;

    const plot = Plot.plot({
      marginLeft: 150,
      marginRight: 56,
      marginTop: 12,
      marginBottom: 34,
      height: 300,
      width: Math.max(container.offsetWidth || 820, 460),
      style: { background: "transparent", color: textPrimary, fontFamily: "inherit", fontSize: "12px" },
      x: {
        domain: [0, 1],
        tickFormat: (d: number) => `${Math.round(d * 100)}%`,
        label: "Score (% of each track's max)",
        grid: true,
        ticks: 5,
      },
      y: { domain: sortedLabels, label: null },
      marks: [
        Plot.ruleX([0], { stroke: gridline }),
        Plot.link(plotData, {
          x1: "detNorm",
          x2: "judgeNorm",
          y1: "model",
          y2: "model",
          stroke: (d: PlotDatum) => d.color,
          strokeWidth: 2,
          strokeOpacity: 0.45,
        }),
        // surface ring under markers
        Plot.dot(plotData, { x: "detNorm", y: "model", fill: surface1, r: 7 }),
        Plot.dot(plotData, { x: "judgeNorm", y: "model", fill: surface1, r: 7 }),
        Plot.dot(plotData, {
          x: "detNorm",
          y: "model",
          fill: (d: PlotDatum) => d.color,
          r: 5,
          tip: true,
          channels: {
            Deterministic: (d: PlotDatum) => `${d.detRaw.toFixed(1)} / ${DET_MAX}`,
            Judge: (d: PlotDatum) => `${d.judgeRaw.toFixed(1)} / ${JUDGE_MAX}`,
            Total: (d: PlotDatum) => d.total.toFixed(1),
          },
        }),
        Plot.dot(plotData, {
          x: "judgeNorm",
          y: "model",
          fill: surface1,
          stroke: (d: PlotDatum) => d.color,
          strokeWidth: 2,
          r: 5,
        }),
        // selective annotation: the judge-high / det-lower story
        Plot.text(
          plotData.filter((d) => d.model === storyLabel),
          {
            x: "detNorm",
            y: "model",
            text: () => "top judge score · weakest checks of the leaders",
            dx: -10,
            dy: -15,
            textAnchor: "end",
            fill: textMuted,
            fontSize: 11,
          }
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
          <h3 className="chart-head">Deterministic checks vs. the LLM judge</h3>
          <p className="sub">
            Each track as a share of its own max. The gap is the story: a model can win the
            judge while leaving deterministic checks on the table.
          </p>
        </div>
        <button className="btn" onClick={() => setShowTable((t) => !t)} aria-pressed={showTable}>
          {showTable ? "Chart" : "Table"}
        </button>
      </div>

      <ul className="legend" aria-hidden="true">
        <li>
          <span className="swatch" style={{ background: "var(--text-primary)", borderRadius: "50%" }} />
          Deterministic (of {DET_MAX})
        </li>
        <li>
          <span className="swatch swatch--ring" style={{ color: "var(--text-primary)" }} />
          LLM-judge (of {JUDGE_MAX})
        </li>
      </ul>

      {showTable ? (
        <table className="data-table">
          <caption className="sr-only">Deterministic and judge scores per model, with combined total.</caption>
          <thead>
            <tr>
              <th scope="col">Model</th>
              <th scope="col">Det ({DET_MAX})</th>
              <th scope="col">Det %</th>
              <th scope="col">Judge ({JUDGE_MAX})</th>
              <th scope="col">Judge %</th>
              <th scope="col">Total (100)</th>
            </tr>
          </thead>
          <tbody>
            {SORTED_MODELS.map((m) => (
              <tr key={m.id}>
                <td>{m.label}</td>
                <td>{m.scorecard.detSubtotal.toFixed(2)}</td>
                <td className="muted">{Math.round((m.scorecard.detSubtotal / DET_MAX) * 100)}%</td>
                <td>{m.judgeTotal.toFixed(2)}</td>
                <td className="muted">{Math.round((m.judgeTotal / JUDGE_MAX) * 100)}%</td>
                <td style={{ fontWeight: 600 }}>{m.total.toFixed(1)}</td>
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
