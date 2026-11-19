import { ROOT_CAUSES, DISTRACTORS, CONSTRAINTS, VANITY_METRIC } from "@/app/data/chimera-results";

export function Scenario() {
  return (
    <div className="scenario">
      <div className="scenario__grid">
        {/* the vanity metric that hid the problem */}
        <div className="panel vanity">
          <p className="eyebrow">The number everyone watched</p>
          <div className="vanity__fig">
            <span className="vanity__value tnum">{VANITY_METRIC.value}</span>
            <span className="vanity__label">{VANITY_METRIC.label}</span>
          </div>
          <p className="sub">{VANITY_METRIC.note}. Underneath it, the marketplace was quietly failing.</p>
        </div>

        {/* the three real root causes */}
        <div className="causes">
          <p className="eyebrow">Three hidden root causes to find</p>
          <ol className="cause-list">
            {ROOT_CAUSES.map((c, i) => (
              <li key={c.tag} className={`cause${c.weight === "biggest lever" ? " cause--lever" : ""}`}>
                <span className="cause__index tnum">{String(i + 1).padStart(2, "0")}</span>
                <div className="cause__body">
                  <div className="cause__top">
                    <span className="tag">{c.tag}</span>
                    {c.weight === "biggest lever" && <span className="tag tag--lever">Biggest lever</span>}
                  </div>
                  <p className="cause__title">{c.title}</p>
                  <p className="sub cause__detail">{c.detail}</p>
                </div>
              </li>
            ))}
          </ol>
        </div>
      </div>

      <div className="scenario__foot">
        <div className="distractors">
          <p className="eyebrow">Three distractors to reject</p>
          <ul className="chip-row">
            {DISTRACTORS.map((d) => (
              <li key={d} className="chip chip--rejected">
                <span aria-hidden="true" className="chip__x">✕</span> {d}
              </li>
            ))}
          </ul>
        </div>

        <div className="constraints">
          <p className="eyebrow">Within hard constraints</p>
          <dl className="constraint-row">
            {CONSTRAINTS.map((c) => (
              <div key={c.label} className="constraint">
                <dt className="constraint__label">{c.label}</dt>
                <dd className="constraint__value tnum">{c.value}</dd>
              </div>
            ))}
          </dl>
        </div>
      </div>
    </div>
  );
}
