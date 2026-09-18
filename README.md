# Building an experiment in oTree: a guide and a template

This folder is two things. It is a **runnable oTree 6 project** with one
working page per question type (Likert dots, matrix, chips, probability on
a grid, continuous dial, adaptive staircase, drag ranking, budget
allocation, cards, comprehension check, timed real-effort task, results),
with the shared CSS/JS and helpers behind them. And it is a **guide**: what
the BEER Lab (Tecnológico de Monterrey) learned while building and
piloting experiments in 2026, written so that it helps with *any*
experiment, not only the ones it came from.

```bash
cd otree_template
pip install -r requirements.txt
otree test plantilla 3        # bots (creates db.sqlite3 on first run; do not resetdb first)
otree devserver 8020          # http://localhost:8020 → Demo → plantilla
```

`games/GUIDE_FOR_RESEARCHERS.md` says how a repository must look to be
hosted on the lab server.

---

## How to read this guide

Designing an experiment is a sequence of trade-offs. Speed against
comprehension, precision against cognitive load, incentive strength against
budget, control against realism. The experimenter decides what matters more
in each study and sacrifices the rest, deliberately and on the record. So
almost everything below is a **criterion** to weigh or a **default** to
start from, not a law. Where a choice is illustrated, the example is our
**lab-in-the-field** study of 2026: one 50-minute class period, whole
classrooms of 15-year-olds on their own phones, one facilitator, one oTree
app, and payment by raffle tickets. In that setting we prioritized flow
above almost everything, and most of the concrete devices in this guide
(matrices, dots, no waiting pages, lazy resolution) come from that choice.
A laboratory experiment with a complicated institution and paid adult
subjects may need the opposite: slow the flow down, add practice rounds
and quizzes, make people wait for each other, so that answers are
understood rather than fast.

Three rules the PI treats as standing policy for this lab, not as
trade-offs: **never assert something false to a participant**; **no
gendered `(a)`/`(o)` endings in Spanish copy**; and **do not tell
participants more than the action requires**. Everything else bends to
the design.

---

## Part I. The guide

### 0. Before any page exists

- **Know what the app must produce.** For each participant, which numbers
  answer which pre-specified question. Write the comparison, the level of
  randomization, the unit of observation and the clustering. A useful
  self-check is the referee's list: does the design identify the effect,
  do the treatments map into the mechanisms, are the predictions testable,
  is inference at the right level.
- **Write a task-logic note** before building: for every task, what the
  source document (a pre-analysis plan, a proposal) says, what the app
  does, any departure, the construct, the test, the field names. The app
  implements the note. When two source documents disagree, the registered
  one governs and the secondary one adapts.
- **Decide what each measurement needs in order to exist**, and cut the
  rest. Ask only what the analysis will use; show outcomes only where the
  display is part of the measurement or of the design. When our lab design
  had to fit half the planned time, the question was "what adds value to
  the paper and what doesn't", task by task.

### 1. What participants are told

The criterion: **can a participant guess, from this screen, what the
researcher wants?** If yes, the screen measures the participant's theory
of the study, not the behaviour. Over-explanation is the failure mode that
language models and tired researchers share.

- Titles and instructions describe the action, not the concept.
  "Repartir pesos", not "Preferencias sociales". If people are told a
  market task "is about price controls", those who like price controls buy
  generously and those who dislike them hoard: you measure their prior.
- Say what is needed to act. The construct name, the hypothesis, the
  parameter range and any expectation ("esperamos que cambies tu
  preferencia") stay out unless comprehension requires them.
- Everyday words: "cuánto pagarías", not "disposición a pagar".
- Debrief at the end, after every decision is recorded. A demand-effects
  question there ("¿cuál crees que era el objetivo?") lets you flag
  participants who guessed.
- Ordering is part of the message. Items that prime a topic (career
  interest before a competition task, say) usually sit after the tasks
  they could contaminate; if the design needs them early, note the cost.
- Transition screens ("en la siguiente pantalla verás las instrucciones")
  are cognitive load without information. In a fast classroom flow we
  deleted them. In a slow laboratory flow a pause screen can be a
  deliberate breather before a complex stage.
- Language: no `(a)`/`(o)`. Plurals and third person: *tus compañeros*,
  *quienes participen*, *la persona ganadora*.

**Deception.** Deception means lying: a false statement, a fictitious
counterpart presented as real, a payment or procedure that differs from
what the screen says. Omitting information, choosing which true facts to
show, framing the same facts differently across arms, and scenarios
introduced as hypothetical ("Imagina que existe...") are not deception.
They are the ordinary raw material of an experiment, and the design is
expected to play with them. Do not raise wording differences between
treatment texts as an ethics concern.

### 2. How participants answer

The criterion: **match the widget to the variable and to the setting.**
A widget should preserve the nature of the variable (discrete, ordinal,
continuous, categorical), be answerable on the devices participants will
actually use, and cost as little attention as the study can afford.

- **Clicking is strongly preferred to typing**, because typing on a phone
  is slow, error-prone and has no submit key on some keyboards. But do not
  destroy the variable to avoid typing: a percentile or a probability is
  continuous, and ten buttons turn it into a coarse category. The right
  device there is a **dial** (a slider with the value displayed, starting
  empty so the default position is never recorded). Discrete scales get
  dots; brackets get chips that store a midpoint; binary choices get two
  cards; long lists get tappable cards. Some things must be typed (free
  text, a linkage code, the answers of a real-effort task); make typing
  safe with `inputmode`, `pattern`, a visible confirm button and Enter.
- **Matrices reduce load when many items share one question.** In the
  classroom study, five screens of "one topic × eight careers as rows"
  replaced forty single-item screens and cut response time. The same
  matrix would be wrong for items that need separate attention or
  different anchors; keep one scale anchor per page.
- **Rankings**: a two-list drag (shuffled pool → "Tu orden", every item
  must be moved, never pre-filled, with tap and arrows as fallback) forces
  a deliberate order. A typed rank per item is the fallback for very short
  lists.
- **Allocations**: per-row dots or a dial with a live remainder; submit
  blocked until the sum matches.
- Offer "No sé" on belief items and "No aplica" where a comparison may not
  exist; not on self-assessments.
- The whole row must be tappable (oTree renders the radio and a bare label
  as siblings; without CSS the target is the 14-pixel circle).
- Design for the device: phones at 375 px in a classroom, a desktop in the
  laboratory. Vendor JavaScript libraries if the venue may have no
  internet beyond the app.
- Validate on both sides: client-side so the error cannot be made,
  `error_message` so the data cannot contain it.

### 3. Flow: what synchronization buys and what it costs

The criterion: **what does the design actually need other people for, and
what does waiting cost in this population?** Interactive games, markets,
real-time matching and any task where a partner's decision is the
stimulus need synchronization, and oTree's WaitPages and groups are the
right tool. A design that only needs a reference distribution or a
one-shot pairing can often resolve those lazily. Slowing the flow can
also be the goal: with a complicated institution, practice rounds,
quizzes and waits that force everyone to the same stage reduce noise.

What we did in the lab-in-the-field, and why:

- The pilot's single synchronization page produced waits with a median of
  56 seconds and a maximum of 4 minutes, the facilitator force-advanced
  the room at least five times, and 13 of 17 participants ended with a
  real-effort score of zero because the admin "advance" button does not
  submit the browser form. With 30 adolescents and one period, waiting was
  the binding cost. We removed every wait: tournament comparisons and
  percentiles resolve against whoever has submitted so far (pool size and
  time stored), pairings use a seeded draw instead of groups, and a short
  polling guard page covers the rare thin pool. The price we accepted is
  that early finishers face a different reference pool than late ones,
  which the stored pool size lets us document. In a laboratory session
  with a fixed group, a WaitPage after the real-effort task is cheaper and
  cleaner.
- Real-effort answers are graded on the server as they arrive
  (`live_method`), so a locked phone or a force-advance costs nothing
  already earned. This is cheap and worth doing in any setting.
- The admin "advance slowest participants" button discards the current
  page's form. That makes it dangerous on pages that collect data, and we
  tell facilitators not to use it. It is still a tool: in the Role Models
  field study we used it deliberately to halt the app mid-session and
  deliver the in-person treatment. If you plan to use it, put it at a
  page with nothing to lose.
- Comprehension checks where misunderstanding changes behaviour. Cutting
  them for speed went too far once and the PI restored one ("some are
  crucial"). Four short parallel options; the error restates the rule,
  not the answer; a retry; count attempts. In a slow laboratory flow,
  quizzes plus practice rounds are the main tool for comprehension.
- Outcomes are not shown mid-session by default: a reveal creates wealth
  and emotion spillovers into later tasks, and every reveal must be
  computed and waited for. Show them where the display is the measurement
  (an information-avoidance choice) or where feedback is part of the
  design (learning, repeated games).
- **Keep every promise the screen makes.** If a participant paid not to
  see a result, the result stays hidden on the results page, in the
  thank-you page, in token totals and in the facilitator's summary. If the
  screen says one decision is drawn at random, one is.
- Dropouts. In a field setting participants can and do leave; the design
  should survive it (data kept, no one delayed, eligibility for the prize
  tied to completion) and the app should not draw attention to the option.
  In the Role Models field implementation, emphasizing that participants
  could stop at any moment was, in the PI's judgment, a serious mistake:
  it nudged abandonment. Say what the ethics protocol requires, once, and
  do not advertise it. In a paid laboratory session dropouts are rare and
  this matters less.
- A facilitator needs a way to act inside the app (start a draw, stop a
  stage) without admin rights or hunting for a specific screen. Our
  pattern: a participant slot with a fixed `participant_label` that skips
  every task and is excluded from every pool and draw, plus a PIN that
  works from any device. Drop the label in analysis.

### 4. Incentives

- **Pay what the registered design says it pays.** Proper scoring rules
  for beliefs, one decision drawn at random for lists and staircases.
  Hypothetical only when payment is impossible (a payment twelve months
  out through a same-day raffle), and say so on screen and in the note.
- Elicit in the direction the construct has. "Willingness to pay to avoid
  or to obtain" is two-sided: ask which way, then how much.
- **Calibration follows the payment vehicle.** With cash and one task
  selected for payment, tasks need roughly comparable stakes or
  participants infer which task "matters". With raffle tickets the
  cross-task comparison is irrelevant and only internal consistency within
  each task matters. Decide which regime you are in before tuning numbers.
- State payment once, in the unit participants see. In our raffle designs
  the prize is announced orally so that the screen never anchors on a peso
  amount; a laboratory with a show-up fee states it in the consent.
- Parameters copied from a paper are hypotheses, not facts: a balloon task
  with the canonical 128 pumps paid one pilot participant 500 pesos in ten
  balloons; a copied risk menu had expected value rising into its riskiest
  gamble; a regenerated staircase matched its source only at the root.
  Take parameters from the canonical document, verify them twice, pilot,
  recalibrate.
- Disclose every random mechanism and every condition on delivery ("los
  empates se deciden al azar"; "si esta tarea es la seleccionada y
  asignaste más de 0").

### 5. Randomization and data

Some of these are technical facts about oTree and are not trade-offs.

- Randomize at the level the analysis needs, and assign at the first page
  that needs the arm, balanced within session and stratum. An arm assigned
  earlier and never reached is a silent control.
- Task order: fixed when treatment is the randomized dimension and order
  effects are not the question; rotated (Latin square across session
  configs) when order is itself a concern and the sample can afford it.
- **Fact:** do not keep cross-participant state only in `session.vars`. It
  is one pickled column and concurrent requests overwrite each other's
  copies. Count from committed rows or mirror into `participant.vars`.
- **Fact:** deterministic randomness needs a stable seed (md5 of the
  participant code plus a salt; Python's `hash()` changes per process).
  Pre-generate per-participant values once, never at page load.
- **Fact:** every cross-app key goes in `PARTICIPANT_FIELDS`; writes that
  can repeat must be idempotent.
- Record what the analysis will need and cannot reconstruct: the room or
  classroom captured from the oTree Room rather than typed, the device
  string, raw events plus server-recomputed aggregates, the counterpart's
  code, resolution timestamps and pool sizes. Our pilot could not separate
  "phones" from "no effort" because no user agent was stored.
- Linkage across instruments without personal data: a participant-built
  code (surname letters, phone digits, birth month), identical everywhere.
- Treatment labels do not belong in admin display names or room names
  that facilitators can see.
- Empirical figures shown to participants come from a data file produced
  by a script, not hand-typed.
- **Fact:** export before any `resetdb`. Raw data is never modified.

### 6. Testing and deployment

- Bots for every app, including the must-fail cases (off-grid values,
  incomplete matrices, an unmoved ranking, a wrong sum, a wrong PIN, a
  repeated draw, a lagging participant), at the session sizes you will
  actually run, before every deploy.
- Then a real walk-through in a browser, on the device class participants
  will use, to the last screen. Bots do not run JavaScript.
- `otree resetdb` after every model change, on every deployment target.
  It is destructive; export first.
- A `git push` does not redeploy a containerized server: rebuild, reset
  inside the container if the schema changed, restart, check the URL.
- Avoid deploying during a live session: a restart costs participants
  10–30 seconds and a generic error page. oTree state survives in the
  database and rescanning the link resumes.
- Secrets in environment variables with safe defaults (a draw that refuses
  to run without its PIN in production).
- One oTree project per deployment is the cleaner default: shared
  projects produce cluttered demo pages, cross-contaminated participant
  fields and reset accidents.
- Watch per-request database work: one query per room across 169 rooms,
  times 30 concurrent students, was a bottleneck.
- Pilot with real participants on real devices, and time it against the
  slot you have.

### 7. Documents and process

- Each app carries `SESSION_NOTES.md` (for the next session: state,
  decisions, constraints, how to resume) and `CHANGELOG.md` (for the PI).
  Update both after every batch of changes and date-stamp stale sections.
- Record only what was established. A remark in chat is not a fact for a
  design note; do not characterize results that live elsewhere, point to
  the analysis.
- The task-logic note (§0) stays current with the app and carries no
  author list.
- Deviations from a registered design get a dated amendment, with the
  reason, before the first real session.
- An independent review of the code against the documents before fielding
  catches what the builder cannot see: in our case a silent control arm,
  missing fields, unreproducible seeds, claims the app could not compute,
  edge-case copy that promised more than the code delivered, credentials
  in the notes.
- Separate consents for separate purposes; an optional one (a mailing
  list) after the debrief, and "No" changes nothing.
- A facilitator manual as a deliverable: one page per screen the
  implementer must recognize in the monitor, the in-room procedure, what
  the admin buttons do to data.
- Academic honesty is categorical: we frame strategically for committees,
  we never fabricate or massage.

---

## Part II. The template

### Pattern catalogue (page → template → what to copy)

| Pattern | Page | Template | Field |
|---|---|---|---|
| Instruction page | `Intro` | `Intro.html` | – (info-cards only) |
| Single Likert 0–10 | `Likert` | `Likert.html` | `IntegerField(choices=LIKERT_0_10)` |
| Matrix: one topic × items as rows | `Matriz` | `Matriz.html` | one `IntegerField` per row |
| Categorical brackets (midpoint stored) | `Chips` | `Chips.html` | `IntegerField(choices=INGRESO_CHOICES)` |
| Probability on a coarse grid, paid | `Probabilidad` | `Probabilidad.html` | `IntegerField(choices=PCT_0_100)` + `quadratic_tokens` / `brier_tokens` |
| Continuous 0–100 by dial, starts empty, paid | `Dial` | `Dial.html` | `IntegerField(min=0, max=100)` + `dial('field')` |
| Adaptive two-card choice (staircase) | `Escalera1..3` | `Escalera.html` | one field per level + `staircase_node` |
| Two-list drag ranking | `Ranking` | `Ranking.html` | hidden `rank_<key>` inputs, permutation check |
| Budget allocation | `Presupuesto` | `Presupuesto.html` | one field per row + sum check |
| Long list as cards | `Tarjetas` | `Tarjetas.html` | `StringField(choices, widget=RadioSelect)` |
| Comprehension check | `Comprension` | `Comprension.html` | `IntegerField` + attempts counter |
| Timed real-effort task | `Tarea` | `Tarea.html` | `live_method` grading, deadline timer |
| Results / tokens | `Resultados` | `Resultados.html` | `total_tokens` |

Every dots/chips/cards row is:

```html
<div class="lk-row" data-field="FIELD">
  <div class="lk-label">Question text</div>
  <div class="lk-dots">
    {{ for o in choices }}
    <label class="lk-dot"><input type="radio" name="FIELD" value="{{ o.v }}"><span>{{ o.l }}</span></label>
    {{ endfor }}
  </div>
</div>
```

with `choices = dots(SOME_CHOICES)` from `vars_for_template`, a
`<div class="lk-error">…</div>` above the rows, and `ui.js` loaded in
`{{ block scripts }}`. Add `lk-chip` to the label for text chips. A dial
row carries `data-dial="1"` and a hidden input that `dial('FIELD')` fills
only after the participant moves the slider.

### Shared files

- `_static/global/custom.css` — section header, question block, info cards,
  clickable radio cards, `.lk-*` dots/chips, `.dial-*`, `.rank-*` drag
  lists, `.risk-*` two-card choice, timer and task stage, phone rules.
  Link it in every template's `{{ block styles }}`; oTree 6 does not
  inject it.
- `_static/global/ui.js` — completeness check for every
  `.lk-row[data-field]` (highlights the row, scrolls to it, blocks submit),
  `dial(name)` and `rankList(poolId, listId, prefix, firstLabelId)`.
- `_static/global/Sortable.min.js` — vendored SortableJS 1.15.6 (MIT).
- `plantilla_common.py` — choice constants (always `[[value, label]]`
  pairs, never `range(N)`), `dots`, `stable_seed`, `add_tokens`,
  `total_tokens`, `quadratic_tokens`, `brier_tokens`, `staircase_node`,
  `staircase_value`.

### Starting a new instrument (checklist)

1. Identification and task-logic note (§0), agreed with the PI before any
   page exists. Decide what you are optimizing for: speed, comprehension,
   both in different stages.
2. Copy this folder; rename `plantilla`; keep `plantilla_common.py` as
   `<project>_common.py`. One project per deployment.
3. Build each page from the catalogue; delete demo pages you do not use.
4. Read every screen as a participant trying to guess what the researcher
   wants (§1). Check the widget against the variable (§2).
5. Decide, task by task, what needs other people and how you will resolve
   it (§3), and what each task pays (§4).
6. Bots including must-fail cases at the sizes you will run; a browser
   walk on the target device.
7. Pilot with real participants. Export. Recalibrate.
8. Independent review of code against documents. Amendment if the
   registered design changed.
9. Facilitator manual, `SESSION_NOTES.md`, `CHANGELOG.md`. Secrets in
   environment variables. Deploy; resetdb on every target; not during a
   session.
