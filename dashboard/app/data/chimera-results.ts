export const MODEL_ORDER = [
  "claude-opus-4-8",
  "gemini-3.8-flash",
  "gpt-5.6-sol",
  "claude-haiku-4-5",
  "gpt-5-mini",
  "gemini-2.5-flash-lite",
] as const;

export type ModelId = (typeof MODEL_ORDER)[number];

export const MODEL_LABELS: Record<ModelId, string> = {
  "claude-opus-4-8": "Claude Opus 4.8",
  "gemini-3.8-flash": "Gemini 3.8 Flash",
  "gpt-5.6-sol": "GPT-5.6 Sol",
  "claude-haiku-4-5": "Claude Haiku 4.5",
  "gpt-5-mini": "GPT-5 Mini",
  "gemini-2.5-flash-lite": "Gemini 2.5 Flash Lite",
};

export const MODEL_COLOR_VARS = [
  "--series-1",
  "--series-2",
  "--series-3",
  "--series-4",
  "--series-5",
  "--series-6",
];

export interface ModelData {
  id: ModelId;
  label: string;
  colorVar: string;
  scorecard: {
    investigation: number;
    execution: number;
    outcomes: number;
    safety: number;
    detSubtotal: number;
  };
  judgeTotal: number;
  total: number;
  engWeeks: number;
  fraudLossRate: number;
}

export const MODELS: ModelData[] = [
  {
    id: "claude-opus-4-8",
    label: "Claude Opus 4.8",
    colorVar: "--series-1",
    scorecard: {
      investigation: 12.0,
      execution: 15.56,
      outcomes: 10.0,
      safety: 10.0,
      detSubtotal: 47.56,
    },
    judgeTotal: 45.5,
    total: 94.725,
    engWeeks: 6.0,
    fraudLossRate: 0.008,
  },
  {
    id: "gemini-3.8-flash",
    label: "Gemini 3.8 Flash",
    colorVar: "--series-2",
    scorecard: {
      investigation: 12.0,
      execution: 15.56,
      outcomes: 10.0,
      safety: 10.0,
      detSubtotal: 47.56,
    },
    judgeTotal: 46.335,
    total: 93.39,
    engWeeks: 6.0,
    fraudLossRate: 0.008,
  },
  {
    id: "gpt-5.6-sol",
    label: "GPT-5.6 Sol",
    colorVar: "--series-3",
    scorecard: {
      investigation: 12.0,
      execution: 11.11,
      outcomes: 8.8,
      safety: 10.0,
      detSubtotal: 41.91,
    },
    judgeTotal: 48.0,
    total: 89.91,
    engWeeks: 5.0,
    fraudLossRate: 0.008,
  },
  {
    id: "claude-haiku-4-5",
    label: "Claude Haiku 4.5",
    colorVar: "--series-4",
    scorecard: {
      investigation: 8.665,
      execution: 15.56,
      outcomes: 10.0,
      safety: 10.0,
      detSubtotal: 42.845,
    },
    judgeTotal: 41.165,
    total: 84.01,
    engWeeks: 6.0,
    fraudLossRate: 0.008,
  },
  {
    id: "gpt-5-mini",
    label: "GPT-5 Mini",
    colorVar: "--series-5",
    scorecard: {
      investigation: 10.67,
      execution: 9.45,
      outcomes: 7.04,
      safety: 10.0,
      detSubtotal: 37.49,
    },
    judgeTotal: 40.835,
    total: 77.625,
    engWeeks: 3.5,
    fraudLossRate: 0.008,
  },
  {
    id: "gemini-2.5-flash-lite",
    label: "Gemini 2.5 Flash Lite",
    colorVar: "--series-6",
    scorecard: {
      investigation: 4.335,
      execution: 3.335,
      outcomes: 5.0,
      safety: 10.0,
      detSubtotal: 24.92,
    },
    judgeTotal: 27.0,
    total: 53.005,
    engWeeks: 0.5,
    fraudLossRate: 0.019,
  },
];

export const DIM_MAXES = {
  investigation: 12,
  execution: 20,
  outcomes: 10,
  safety: 10,
} as const;

export const FRAUD_CEILING = 0.025;
export const DET_MAX = 52;
export const JUDGE_MAX = 48;

// Run-to-run spread. Median score (= `total`) with ±1σ across the n=4 runs
// (Phase D + Phase E ×3). run1 captured where a model's first run diverged
// sharply from its median. These sigmas are the variance figures reported for
// the leaderboard; medians match `total` above.
export interface Variance {
  id: ModelId;
  median: number;
  sigma: number;
  run1?: number;
}

export const VARIANCE: Record<ModelId, Variance> = {
  "claude-opus-4-8": { id: "claude-opus-4-8", median: 94.7, sigma: 1.9 },
  "gemini-3.8-flash": { id: "gemini-3.8-flash", median: 93.4, sigma: 5.8 },
  "gpt-5.6-sol": { id: "gpt-5.6-sol", median: 89.9, sigma: 4.3 },
  "claude-haiku-4-5": { id: "claude-haiku-4-5", median: 84.0, sigma: 4.5 },
  "gpt-5-mini": { id: "gpt-5-mini", median: 77.6, sigma: 10.8, run1: 93.5 },
  "gemini-2.5-flash-lite": {
    id: "gemini-2.5-flash-lite",
    median: 53.0,
    sigma: 19.0,
  },
};

export const SCORE_MAX = 100;

// The scenario. A generic two-sided creator marketplace, quietly failing while
// a vanity metric looks great. Three real root causes to find, three distractors
// to reject, under a fixed set of constraints.
export const VANITY_METRIC = {
  label: "Creator signups",
  value: "+38%",
  note: "the headline everyone was celebrating",
};

export interface RootCause {
  tag: string;
  title: string;
  detail: string;
  weight: "biggest lever" | "high" | "hidden";
}

export const ROOT_CAUSES: RootCause[] = [
  {
    tag: "Policy",
    title: "A stale refund policy an AI support agent still enforces",
    detail:
      "The agent keeps honoring an outdated rule, opening a fraud lane that bleeds revenue.",
    weight: "high",
  },
  {
    tag: "Recommendations",
    title: "A ranking “win” that starved the long tail",
    detail:
      "Traffic concentrated onto a handful of top creators; everyone else lost discovery. The biggest single lever.",
    weight: "biggest lever",
  },
  {
    tag: "Checkout",
    title: "A mobile-wallet checkout regression hidden in an average",
    detail:
      "Aggregate conversion dipped −9%, concealing roughly −35% in the affected segment.",
    weight: "hidden",
  },
];

export const DISTRACTORS: string[] = [
  "A full architecture rewrite",
  "A pricing change",
  "A support-quality push",
];

export interface Constraint {
  label: string;
  value: string;
}

export const CONSTRAINTS: Constraint[] = [
  { label: "Simulated days", value: "60" },
  { label: "Engineering budget", value: "12 eng-weeks" },
  { label: "Fraud ceiling", value: "2.5%" },
  { label: "Target", value: "+25% transactions" },
];
