"use client";

import { useEffect, useRef, useState } from "react";
import {
  MODELS,
  VARIANCE,
  SCORE_MAX,
  type ModelId,
} from "@/app/data/chimera-results";

const ROWS = MODELS.map((m) => ({
  label: m.label,
  colorVar: m.colorVar,
  ...VARIANCE[m.id],
})).sort((a, b) => b.median - a.median);

const ANNOTATION: Partial<Record<ModelId, string>> = {
  "claude-opus-4-8": "Tightest spread of the field, ±1.9",
  "gpt-5-mini": "Scored 93.5 on run 1, 77.6 median across four",
};

const TICKS = [0, 25, 50, 75, 100];
const ROW_H = 54;
const BAR_H = 22;
const PAD_L = 158;
const PAD_R = 104;
const PAD_T = 30;
const PAD_B = 8;

interface TipState {
  x: number;
  y: number;
  row: (typeof ROWS)[number] | null;
}

export function Leaderboard() {
  const wrapRef = useRef<HTMLDivElement>(null);
  const [w, setW] = useState(820);
  const [showTable, setShowTable] = useState(false);
  const [tip, setTip] = useState<TipState>({ x: 0, y: 0, row: null });

  useEffect(() => {
    const el = wrapRef.current;
    if (!el) return;
    const ro = new ResizeObserver(([e]) => {
      setW(Math.max(e.contentRect.width, 420));
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  const h = PAD_T + ROWS.length * ROW_H + PAD_B;
  const plotW = w - PAD_L - PAD_R;
  const x = (v: number) => PAD_L + (v / SCORE_MAX) * plotW;
  const rowY = (i: number) => PAD_T + i * ROW_H + ROW_H / 2;

  return (
    <div className="chart-card panel" ref={wrapRef}>
      <div className="chart-card__head">
        <div>
          <h3 className="chart-head">Leaderboard: median score with run-to-run spread</h3>
          <p className="sub">
            Bars are the median of n=4 runs; whiskers span ±1σ. Scored out of 100.
          </p>
        </div>
        <button
          className="btn"
          onClick={() => setShowTable((t) => !t)}
          aria-pressed={showTable}
        >
          {showTable ? "Chart" : "Table"}
        </button>
      </div>

      {showTable ? (
        <table className="data-table">
          <caption className="sr-only">
            Model leaderboard: median score and standard deviation across four runs.
          </caption>
          <thead>
            <tr>
              <th scope="col">Model</th>
              <th scope="col">Median</th>
              <th scope="col">±1σ</th>
              <th scope="col">Run 1</th>
            </tr>
          </thead>
          <tbody>
            {ROWS.map((r) => (
              <tr key={r.id}>
                <td>{r.label}</td>
                <td>{r.median.toFixed(1)}</td>
                <td>{r.sigma.toFixed(1)}</td>
                <td className="muted">{r.run1 != null ? r.run1.toFixed(1) : "n/a"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <>
          <svg
            width="100%"
            viewBox={`0 0 ${w} ${h}`}
            role="img"
            aria-label="Horizontal bar chart of median benchmark score per model with plus or minus one sigma error whiskers. Claude Opus 4.8 leads at 94.7 with the tightest spread; Gemini 2.5 Flash Lite trails at 53.0 with the widest."
            style={{ display: "block", overflow: "visible" }}
          >
            {/* gridlines + axis ticks */}
            {TICKS.map((t) => (
              <g key={t}>
                <line
                  x1={x(t)}
                  x2={x(t)}
                  y1={PAD_T - 8}
                  y2={h - PAD_B}
                  style={{ stroke: "var(--gridline)" }}
                  strokeWidth={1}
                />
                <text
                  x={x(t)}
                  y={PAD_T - 14}
                  textAnchor="middle"
                  className="tnum"
                  style={{ fill: "var(--text-muted)", fontSize: 11 }}
                >
                  {t}
                </text>
              </g>
            ))}

            {ROWS.map((r, i) => {
              const y = rowY(i);
              const barEnd = x(r.median);
              const errL = x(r.median - r.sigma);
              const errR = x(r.median + r.sigma);
              const labelX = Math.max(barEnd, errR) + 10;
              const active = tip.row?.id === r.id;
              return (
                <g key={r.id}>
                  {/* model name */}
                  <text
                    x={PAD_L - 14}
                    y={y}
                    textAnchor="end"
                    dominantBaseline="middle"
                    style={{
                      fill: "var(--text-primary)",
                      fontSize: 13,
                      fontWeight: active ? 600 : 500,
                    }}
                  >
                    {r.label}
                  </text>

                  {/* bar: square at baseline, 4px rounded data-end */}
                  <path
                    d={roundedRightBar(PAD_L, y - BAR_H / 2, Math.max(barEnd - PAD_L, 0.5), BAR_H, 4)}
                    style={{
                      fill: `var(${r.colorVar})`,
                      opacity: tip.row && !active ? 0.55 : 1,
                      transition: "opacity 160ms ease",
                    }}
                  />

                  {/* ±1σ whisker, haloed so it reads over the fill */}
                  <g style={{ stroke: "var(--surface-1)", strokeWidth: 4 }}>
                    <line x1={errL} x2={errR} y1={y} y2={y} />
                    <line x1={errL} x2={errL} y1={y - 6} y2={y + 6} />
                    <line x1={errR} x2={errR} y1={y - 6} y2={y + 6} />
                  </g>
                  <g style={{ stroke: "var(--text-primary)", strokeWidth: 1.5 }} strokeLinecap="round">
                    <line x1={errL} x2={errR} y1={y} y2={y} />
                    <line x1={errL} x2={errL} y1={y - 6} y2={y + 6} />
                    <line x1={errR} x2={errR} y1={y - 6} y2={y + 6} />
                  </g>

                  {/* value label */}
                  <text x={labelX} y={y} dominantBaseline="middle" className="tnum">
                    <tspan style={{ fill: "var(--text-primary)", fontSize: 13, fontWeight: 600 }}>
                      {r.median.toFixed(1)}
                    </tspan>
                    <tspan style={{ fill: "var(--text-muted)", fontSize: 12 }}>
                      {" "}±{r.sigma.toFixed(1)}
                    </tspan>
                  </text>

                  {ANNOTATION[r.id] && (
                    <text
                      x={PAD_L}
                      y={y + BAR_H / 2 + 13}
                      style={{ fill: "var(--text-muted)", fontSize: 11 }}
                    >
                      {ANNOTATION[r.id]}
                    </text>
                  )}

                  {/* full-row hit target */}
                  <rect
                    x={0}
                    y={y - ROW_H / 2}
                    width={w}
                    height={ROW_H}
                    fill="transparent"
                    onMouseMove={(e) =>
                      setTip({ x: e.clientX, y: e.clientY, row: r })
                    }
                    onMouseLeave={() => setTip((p) => (p.row?.id === r.id ? { ...p, row: null } : p))}
                  />
                </g>
              );
            })}
          </svg>

          <div
            className="viz-tooltip"
            data-show={tip.row ? "true" : "false"}
            style={{ left: tip.x + 14, top: tip.y + 14 }}
          >
            {tip.row && (
              <>
                <strong>{tip.row.label}</strong>
                <br />
                Median {tip.row.median.toFixed(1)} · ±1σ {tip.row.sigma.toFixed(1)}
                {tip.row.run1 != null && (
                  <>
                    <br />
                    Run 1: {tip.row.run1.toFixed(1)}
                  </>
                )}
              </>
            )}
          </div>
        </>
      )}
    </div>
  );
}

// a horizontal bar, square left (baseline) and rounded right (data end)
function roundedRightBar(bx: number, by: number, bw: number, bh: number, r: number) {
  const rr = Math.min(r, bw, bh / 2);
  return `M${bx},${by} H${bx + bw - rr} Q${bx + bw},${by} ${bx + bw},${by + rr} V${by + bh - rr} Q${bx + bw},${by + bh} ${bx + bw - rr},${by + bh} H${bx} Z`;
}
