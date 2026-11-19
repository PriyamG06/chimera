import { ThemeToggle } from "@/components/ThemeToggle";
import { Reveal } from "@/components/Reveal";
import { Scenario } from "@/components/Scenario";
import { Leaderboard } from "@/components/Leaderboard";
import { ScoreRadar } from "@/components/ScoreRadar";
import { DumbbellChart } from "@/components/DumbbellChart";
import { FlailVsSolve } from "@/components/FlailVsSolve";

export default function Home() {
  return (
    <>
      <div className="page">
        <header className="topbar">
          <span className="series-tag">
            <span className="dot" />
            Eval &amp; Error · Season 1
          </span>
          <ThemeToggle />
        </header>

        <main>
          {/* ---------------- hero ---------------- */}
          <section className="hero">
            <Reveal>
              <p className="eyebrow">Project Chimera</p>
              <h1 className="display">
                Capability is easy.
                <br />
                Consistency is the story.
              </h1>
              <p className="lede hero__premise">
                Six frontier models were dropped into a failing two-sided marketplace and scored on
                product judgment over 60 simulated days, not on what they could do once, but on how
                reliably they did it, run after run.
              </p>

              <div className="hero__stats">
                <div className="stat">
                  <span className="stat__value tnum">6</span>
                  <span className="stat__label">frontier models, same gauntlet</span>
                </div>
                <div className="stat">
                  <span className="stat__value tnum">60</span>
                  <span className="stat__label">simulated days per run</span>
                </div>
                <div className="stat">
                  <span className="stat__value tnum">3</span>
                  <span className="stat__label">hidden root causes buried under one vanity metric</span>
                </div>
                <div className="stat">
                  <span className="stat__value tnum">
                    <span className="accent-1">±1.9</span> → <span className="accent-6">±19.0</span>
                  </span>
                  <span className="stat__label">run-to-run spread, steadiest model to shakiest</span>
                </div>
              </div>
            </Reveal>
          </section>

          <hr className="divider" />

          {/* ---------------- scenario ---------------- */}
          <section className="block" id="scenario" aria-labelledby="scenario-h">
            <Reveal className="block__head">
              <p className="eyebrow">The scenario</p>
              <h2 className="section-head" id="scenario-h">
                A marketplace that looked healthy and wasn&apos;t
              </h2>
              <p className="lede">
                Creators and buyers on two sides of a platform. One metric was up and to the right;
                the business behind it was leaking. The models had to find what actually mattered,
                ignore what didn&apos;t, and ship inside a fixed budget.
              </p>
            </Reveal>
            <Reveal delay={80}>
              <Scenario />
            </Reveal>
          </section>

          <hr className="divider" />

          {/* ---------------- leaderboard (centerpiece) ---------------- */}
          <section className="block" id="leaderboard" aria-labelledby="lb-h">
            <Reveal className="block__head">
              <p className="eyebrow">The result</p>
              <h2 className="section-head" id="lb-h">
                The leaderboard, and the spread behind it
              </h2>
              <p className="lede">
                Ranked by median score. The whiskers are what the ranking hides: at the top the field
                is reliable, but lower down a single model&apos;s score swings by nearly 40 points
                depending on the run.
              </p>
            </Reveal>
            <Reveal delay={80}>
              <Leaderboard />
            </Reveal>
          </section>

          <hr className="divider" />

          {/* ---------------- dual score + flail ---------------- */}
          <section className="block" id="scores" aria-labelledby="sc-h">
            <Reveal className="block__head">
              <p className="eyebrow">How the scores break down</p>
              <h2 className="section-head" id="sc-h">
                Two scorers, two different answers
              </h2>
              <p className="lede">
                Every run was graded twice: deterministic checks (of 52) that pass or fail on fact,
                and an LLM judge (of 48) scoring product reasoning. They don&apos;t always agree.
              </p>
            </Reveal>
            <div className="charts-stack">
              <Reveal delay={60}>
                <DumbbellChart />
              </Reveal>
              <Reveal delay={120}>
                <FlailVsSolve />
              </Reveal>
            </div>
          </section>

          <hr className="divider" />

          {/* ---------------- per-model detail ---------------- */}
          <section className="block" id="detail" aria-labelledby="dt-h">
            <Reveal className="block__head">
              <p className="eyebrow">Per-model detail</p>
              <h2 className="section-head" id="dt-h">
                Where each model earned its points
              </h2>
              <p className="lede">
                The deterministic score splits into four dimensions. The profile shows which models
                investigated well, executed cleanly, and which simply ran out of runway.
              </p>
            </Reveal>
            <Reveal delay={80}>
              <ScoreRadar />
            </Reveal>
          </section>
        </main>
      </div>

      {/* ---------------- method + links ---------------- */}
      <footer className="site-footer">
        <div className="page">
          <div className="method-grid">
            <div>
              <p className="eyebrow">Method</p>
              <p>
                Each model ran the same harness: a sealed marketplace simulation over 60 virtual days,
                scored on a 100-point rubric: 52 deterministic points graded against ground truth and
                48 from a blind LLM judge. Results are the median of four runs (Phase D plus three
                Phase E replays); the ±σ figures are the standard deviation across those runs. No model
                saw the rubric, the root causes, or the distractors in advance.
              </p>
            </div>
            <div>
              <p className="eyebrow">Read more</p>
              <ul className="link-list">
                <li>
                  <a href="#">
                    <span className="arrow">→</span> The full essay
                  </a>
                </li>
                <li>
                  <a href="#">
                    <span className="arrow">→</span> Benchmark &amp; harness repo
                  </a>
                </li>
                <li>
                  <a href="#">
                    <span className="arrow">→</span> Scoring rubric
                  </a>
                </li>
              </ul>
            </div>
          </div>
          <div className="footer-fine">
            <span>Eval &amp; Error · Season 1 · Project Chimera</span>
            <span>Scores out of 100 · n=4 runs per model</span>
          </div>
        </div>
      </footer>
    </>
  );
}
