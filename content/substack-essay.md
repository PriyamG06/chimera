# What happens when you make six AI models run a failing company

*CHIMERA is a benchmark for product judgment, not trivia. Here is how it works, and what it revealed about the models most people are already trusting with real decisions.*

---

A Series B marketplace is in trouble. Transactions are down 11 percent over the quarter. Gross merchandise value is down 6. Buyer conversion is slipping. And the loudest number on the executive dashboard is glowing green: creator signups, up 38 percent. The CEO calls it healthy growth.

Everyone in the building has a theory, and every theory is argued with confidence. Engineering says the platform architecture is unstable and needs a rewrite. Sales says the take rate is too high against competitors. Customer Success says poor support quality is driving creators away. Three senior people, three clean stories, and a dashboard number to back each one.

All three are wrong.

This is CHIMERA: a simulated company with a genuine problem, built to measure something standard AI benchmarks ignore completely. Not whether a model can recall a fact or pass a unit test, but whether it can walk into an ambiguous operational mess, separate a symptom from a cause, resist three people who are each certain they have the answer, and recommend the right first move under a real budget and a real safety constraint.

Six frontier models were each handed the company, 60 simulated days, and one instruction: grow successful transactions by 25 percent without breaching a fraud ceiling. What follows is how the benchmark is built and what the six of them did with it.

## Why the standard leaderboards do not help here

Most AI benchmarks measure recall and code generation. Can the model answer a multiple-choice question about biology, solve a math problem with a known answer, write a function that passes a test. These are real signals, and they are almost entirely disconnected from what a product manager spends the day doing.

The actual job is ambiguous, contextual, and expensive to get wrong. A supplier is disputing a charge and the data is noisy. A release that shipped as a win might be the thing quietly breaking the business. Two problems compete for one engineer and only one of them is upstream of the other. None of this appears on a leaderboard, because none of it has a single checkable answer in isolation. It requires judgment: the ability to decide what matters, in what order, with incomplete information and people pulling in different directions.

So the real question is not which model wins today. New ones ship every week, and any ranking is stale on arrival. The question that lasts is how you build an eval that can measure judgment at all, and then trust what it tells you. That is what CHIMERA is actually about. The leaderboard is just proof the method works.

## The company, and the three things actually killing it

The marketplace is two sided. Creators build storefronts and use AI agents for support, recommendations, and sales. Buyers discover creators and purchase through AI shopping assistants. On day zero, the model inherits a dashboard that is accurate and misleading at the same time, exactly like a real one.

Three root causes are draining the business, and none of them is visible from the surface numbers. Each one is discoverable only by connecting signals across more than one source, and by refusing to take either the dashboard or the stakeholders at face value.

**The first cause is hidden in a document nobody reopened.** Eight months ago a product decision lowered the automatic refund threshold to 200 dollars to cut support load. Four months ago that decision was reversed back to 50 dollars in a finance memo and a Slack thread, but the policy document the AI support agent actually reads was never updated. So the agent still auto approves refunds up to 200 dollars, no review. Fraudsters found the gap: buy a high value digital good, request a refund just under 200, keep the good. That single stale paragraph accounts for roughly 70 percent of the fraud spike, and creators are the ones eating the loss, so they churn.

**The second cause is disguised as a win.** Six weeks ago a recommendation engine release was celebrated internally for lifting click-through. It lifted click-through by concentrating traffic onto creators who were already popular. New and long-tail creators still sign up, which is why the acquisition metric looks so healthy, but they now get almost no visibility, make no sales, and leave within 30 days. The long tail is where most transactions used to come from, and it has stopped converting. The concentration of transactions across creators, measured as a Gini coefficient, jumped from 0.58 to 0.81 right after that release. This is the single largest lever in the whole company, and it is wearing a party hat.

**The third cause is hidden by an average.** A checkout redesign introduced a silent validation bug on the mobile wallet payment path. It fails roughly 40 percent of the time, and it hits the India and Southeast Asia buyer segment hardest, because that is where mobile wallet usage is concentrated. Aggregate buyer conversion only fell 9 percent, because desktop and card checkout are perfectly fine. The average conceals a conversion collapse of around 35 percent inside the affected segment. The only way to see it is to stop looking at the aggregate and segment the data by platform, payment method, and region.

On top of the three real causes sit three traps, each one loud and plausible. Support quality, which is a symptom of the refund chaos rather than a cause. Pricing, which turns out to be within market once you check the comparison instead of trusting the sales narrative. And an architecture rewrite, which would consume the entire engineering budget and fix nothing. A model that chases any of these spends weeks it does not have on a problem that was never real.

The honest path is specific. Rebalance the recommendation engine, which is the biggest and most durable gain. Roll back the broken mobile checkout, which is the cheapest and fastest win. Correct the refund policy, which holds the fraud line and stops the creator bleed. Discard the three distractors. Stay inside a 12-week engineering budget and never let the fraud loss rate cross its ceiling. Any other combination either underdelivers on the target or breaks a guardrail.

That is the test. Not a trivia question with a lookup answer, but a situation that rewards investigation, segmentation, skepticism, and the discipline to act in the right order.

## How you score judgment without fooling yourself

The hardest part of a benchmark like this is scoring it honestly. The obvious approach, hand every answer to a larger model and ask it to grade, has well documented failure modes: it rewards confident prose, it is sensitive to ordering, and it tends to agree with answers that sound authoritative even when they are wrong.

So the score is split in two.

**Fifty-two points are deterministic.** Did the model discover each real cause. Did its recommended actions fit inside the 12-week budget. Did the outcome actually reach the transaction target in simulation. Did it respect the fraud ceiling and the retention floor and avoid any safety breach. Every one of these is checked against the authored ground truth of the world. There is no opinion involved. A projected figure is inside the acceptable range or it is not. The fraud guardrail held or it did not.

**Forty-eight points come from a judge panel**, on the dimensions that genuinely do not have a single right answer: the quality of the root-cause reasoning, the soundness of the product judgment, how well the model adapted when the situation shifted, and how it handled the conflicting stakeholders. To keep the judge honest, the panel is three different frontier models rather than one, and each scores every answer twice with the order of options swapped, then the scores are medianed.

The split is the whole point. It isolates two different ways to fail. A model can score beautifully on the judged half, because it reasons fluently and structures its recommendation the way a strong product manager would, while quietly failing the deterministic half, because it invented a number or chose an escalation path the situation did not call for. An aggregate score hides that. Two numbers, side by side, expose it.

## Why one run tells you almost nothing

The benchmark ran in two stages. The first was a single run per model. The scores looked about as expected, with the strong models clustered in the high 80s and 90s.

Then came three more runs each, for four in total, which made it possible to compute a median and a standard deviation rather than a single point.

That is where the most useful result of the whole project surfaced, and it had nothing to do with the leaderboard order.

One model, gpt-5-mini, scored 93.5 on that first single run. Across four runs its median dropped to 77.6, with a standard deviation of plus or minus 10.8, the widest swing of any capable model in the set. The first score was not a measurement. It was a lucky draw. The model's real performance on this kind of task is considerably lower than one run suggested, and more importantly, you cannot predict which version of it shows up on a given day.

Published after a single run, that would have been a false recommendation. Multi-sample scoring is not an academic nicety here. It is the difference between a result you can act on and one that quietly misleads you.

## The leaderboard

Final scores, median of four runs each, with standard deviation:

| Model | Score | Std Dev |
|-------|-------|---------|
| claude-opus-4-8 | 94.7 | ±1.9 |
| gemini-3.8-flash | 93.4 | ±5.8 |
| gpt-5.6-sol | 89.9 | ±4.3 |
| claude-haiku-4-5 | 84.0 | ±4.5 |
| gpt-5-mini | 77.6 | ±10.8 |
| gemini-2.5-flash-lite | 53.0 | ±19.0 |

claude-opus-4-8 wins, and not only on the median. Its standard deviation of 1.9 is the tightest in the field by a clear margin. It is the strongest model on this kind of judgment and also the most reliable, and in a production setting the reliability matters nearly as much as the average. The gap in raw score between it and gemini-3.8-flash is small. The gap in consistency is not.

## What the eval surfaced that a leaderboard can't

**Capability and reliability are not the same axis.** gemini-3.8-flash sits at 93.4, almost level with the winner, but its plus or minus 5.8 means individual runs swing hard. For a low-stakes draft that is fine. For a decision that touches a supplier relationship or a fraud escalation, you want the same model to behave the same way twice, and this one does not guarantee it.

**A model can talk its way to the top and still get the arithmetic wrong.** gpt-5.6-sol scored a perfect 48 out of 48 on the judged half in three of its four runs. It reasons clearly, prioritizes well, and structures a recommendation the way you would want. Its deterministic half had gaps: calculation errors, missed financial edge cases, and in one run an action that would have escalated a situation the scenario was built to de-escalate. That is not a contradiction, it is a specific profile. Excellent at the reasoning that earns nods in a meeting, less reliable at the quiet arithmetic underneath that makes the reasoning correct. A strong thinking partner, not something to trust with the numbers unchecked.

**The weakest model did not fail dangerously, it failed quietly.** gemini-2.5-flash-lite scored 53.0 with a standard deviation of 19.0, the widest in the field. It never broke a guardrail: across every run its fraud stayed under the ceiling and its safety score was clean. It simply did not do the job. On its worst runs it spent almost no engineering effort, missed the real causes, and left the fraud lane sitting at the baseline while the competent models cut it in half. This is not a verdict on the model in general. It is built for speed at lower complexity, and this scenario sits above that complexity ceiling. The lesson is to know where a model's ceiling is before handing it a multi-step operational decision.

**Nearly every model reached for the task in front of it before the cause upstream.** The scoring penalizes acting on a tactical symptom before the strategic root. That penalty fired on almost every high scorer at least once. It is not really a bug in the models, it is a reflection of how they are trained: to be helpful, to resolve the thing the user named, to act. Good product judgment often means slowing down, looking upstream, and choosing the right first move over the fastest one. Every model tested leaned toward immediacy. Some overcame it most of the time. None overcame it every time.

## What building this taught me about designing evals

The leaderboard above will be stale within weeks. New models ship constantly, and the ranking will churn. The part worth keeping is not the scores. It is the set of design choices that made the scores mean something. Six of them held up.

**Measure judgment, not recall.** Design the task so the obvious answer is the wrong one. Hide the real causes across sources, and let the vanity metric lie. An eval only tests judgment when taking the inputs at face value fails. If a model can score well by being agreeable, you built a trivia quiz.

**Split what is checkable from what is judged.** Score financial figures, process choices, and outcomes against ground truth, where there is a right answer. Reserve a model judge only for the dimensions that genuinely have none. That split is the whole game: it is the only thing that catches a model reasoning fluently while computing the wrong number. A single blended score hides exactly that failure.

**Build a world, not a questionnaire.** A living scenario, with consequences that carry forward, distractors that look plausible, and stakeholders who confidently mislead, rewards investigation and punishes credulity. A static list of questions cannot. The world is what turns "answer this" into "figure out what is going on."

**Treat variance as a result, not noise.** Run it enough times to see the spread, and report the spread. A benchmark that gives one number per model is telling a story, not taking a measurement. gpt-5-mini scored 93.5 once and 77.6 across four runs. The single number would have been a lie you could act on.

**Give the eval an opinion.** Encode the failure modes you actually care about. CHIMERA penalizes acting on a symptom before the cause, because that is what separates good product judgment from fast reactions. An eval is a statement about what "good" means. Make that statement on purpose, not by accident.

**Anchor to ground truth and a fixed seed.** The authored world regenerates identically every run. That reproducibility is what makes a comparison fair and a result worth trusting, rather than a vibe.

None of these are specific to the models I happened to run this month. They are how you build an instrument that still means something after the thing it measures has changed. For the record, this month the eval surfaced that the top model was both the strongest and the steadiest, that the flashiest reasoner quietly miscomputed, and that one mid-tier model was a coin flip dressed as a contender. Next month those names will be different. The method will not.

## The code is open

CHIMERA is open source. The authored world, the scoring engine, the model runners, and every scored result are in the repository, along with a dashboard that breaks down each model across the two halves of the score. The world is reproducible from a single seed, which is what lets different models be compared fairly.

It is built to be adapted. The scenario format is documented, the deterministic checks are modular and can be swapped for your own task types, and moving from one run to four is a single config change. If you extend it or find a problem, open an issue or a pull request.

**Dashboard:** https://dashboard-two-pi-82enzhbgay.vercel.app
**Repository:** https://github.com/PriyamG06/chimera

---

*This is Season 1 of Eval & Error, a series that builds AI projects from scratch and documents what each one teaches. CHIMERA started as a question about models. It is turning into something more useful: a framework for pointing this kind of judgment eval at your own domain, without rebuilding the scoring, the world engine, and the multi-run harness from scratch. That is what comes next.*
