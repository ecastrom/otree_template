# Building an experiment in oTree: a guide and a template

> **Deploying on the BEER Lab server?** Read [GUIDE_FOR_RESEARCHERS.md](GUIDE_FOR_RESEARCHERS.md)
> (how to structure the project, environment variables, the server Dockerfile
> for local testing, how to submit it).


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

How to get a project hosted on the BEER Lab server (what the zip must
contain, how to send it): https://experiments.beer-lab.org/guia/ (research)
and https://teaching.beer-lab.org/guia/ (classroom games).

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

### 3. Flow: pace, synchronization and the experimenter's hand

"Flow" is the sequence and pace at which participants move through the
screens, where they must wait for other people or for the experimenter,
and what happens when someone is slow, absent or gone. Three questions
settle most flow decisions:

1. **What does each task need from other people?** Nothing (a survey
   item, an individual choice); a reference distribution (a percentile, a
   tournament against the group); one counterpart's decision (a dictator
   transfer, a two-player game); or a full group state at every step (a
   market, a repeated game with feedback). Each level needs a different
   amount of synchronization, and it is worth listing the tasks by level
   before choosing a mechanism.
2. **What does time cost in this population and venue?** A fixed slot
   (a class period), a limited attention span, participants on their own
   phones with screens that lock, and real dropouts push toward speed and
   independence. A paid laboratory session with a captive group and
   desktop machines makes waiting cheap.
3. **What does slowing down buy?** With a complicated institution or an
   unfamiliar mechanism, practice rounds, quizzes and forced pauses make
   everyone reach the decisions with the same understanding, and reduce
   noise more than they cost. Speed is not a virtue in itself; the goal is
   answers that mean what the design assumes they mean.

The mechanisms, each with its price:

- **Group WaitPages** (oTree groups): everyone in the group reaches the
  same stage before anyone proceeds. Exact, simple to reason about, the
  right tool for interactive games. Costs: the fastest wait for the
  slowest, dropouts block their group, group sizes must be fixed.
- **Whole-session waits**: a single barrier for all participants. The
  same costs multiplied by the session size; usually only worth it before
  a stage the experimenter must run in person.
- **Lazy resolution**: whatever needs the group is computed, when the
  participant reaches it, from what has been submitted so far, with the
  pool size and the time stored. Nobody waits. Costs: early finishers face
  a different reference pool than late ones, thin pools at the start of a
  session, and the analysis must handle the stored pool sizes.
- **Bounded guard pages**: a short polling page that advances when the
  pool is ready or after a hard cap. A compromise for thin pools in
  self-paced settings.
- **Experimenter-controlled stages**: the session stops until the
  experimenter acts (delivers a treatment in person, reads instructions,
  runs a draw). This needs a mechanism designed in advance, because
  oTree's admin tools are blunt: the "advance slowest participants"
  button discards whatever form the participant had open, so it must only
  be used on pages with nothing to lose, and it acts on at most twenty
  participants at a time.

Principles that hold across settings:

- **Grade real-effort answers on the server as they arrive**
  (`live_method`), so nothing already earned is lost to a locked phone, a
  lost connection or an administrative advance. Cheap everywhere.
- **Comprehension checks where misunderstanding changes behaviour.**
  Four short parallel options; the error restates the rule, not the
  answer; a retry; count the attempts. Cutting quizzes for speed can go
  too far: the PI restored one after it was cut ("some are crucial").
- **Feedback and reveals are design decisions, not decoration.** A
  mid-session reveal creates wealth and emotion spillovers into later
  tasks and requires a computed result to wait for. Show outcomes where
  the display is the measurement, or where feedback is part of the design
  (learning, repeated games); otherwise resolve silently and show results
  at the end.
- **Keep every promise the screen makes.** If a participant paid not to
  see a result, it stays hidden on every later screen, in totals, and in
  anything the facilitator sees. If the screen says one decision is drawn
  at random, one is.
- **Plan for dropouts according to the setting.** In the field they
  happen; the design must survive them (data kept, nobody delayed,
  eligibility for payment tied to completion) and the app should not
  advertise the exit. Say what the ethics protocol requires, once. In the
  Role Models field implementation, stressing that participants could
  stop at any moment was, in the PI's judgment, a serious mistake: it
  nudged abandonment. In a paid laboratory session this matters less.
- **The person running the room needs a way to act inside the app.**
  Starting a stage, stopping the session for an in-person step, or
  triggering a draw should not depend on finding the admin panel on a
  laptop. Give the facilitator a defined role in the app and a control
  that works from wherever they are.

*What we did in the lab-in-the-field, and why.* One 50-minute period,
whole classrooms on their own phones, no second staff member. The pilot
had a single synchronization page; it produced waits with a median of 56
seconds and a maximum of 4 minutes, the facilitator force-advanced the
room at least five times, and 13 of 17 participants ended with a
real-effort score of zero because the advance button does not submit the
form. Waiting was the binding cost, so we removed every wait: tournament
comparisons and percentiles resolve lazily, a one-shot pairing uses a
seeded draw instead of groups, a guard page covers the rare thin pool,
and the real-effort task is graded as answers arrive. The price we
accepted, documented through the stored pool sizes, is that early
finishers were compared against a smaller pool. The one thing that had
to be synchronized was the payment: tokens were raffle tickets and the
prize was drawn in the room at the end of the session. The facilitator
joins the session as a participant with a fixed label (skipping every
task, excluded from every pool and from the draw, dropped in analysis),
and the waiting screen shows a small box where a PIN starts the draw.
Because the box is on every participant's waiting screen, the facilitator
can run the draw from any phone in the room; the PIN is what makes that
safe. A laboratory session with a fixed group would have used a WaitPage
after the real-effort task and paid at the desk, and none of this
machinery would have been needed.

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

Most of this section is about memory. An experiment is built over weeks,
by several people, increasingly with AI coding agents that keep no memory
between sessions; and the person who made a decision in March will not
remember its reason in September. Write things down as you go, in files
that live with the code and that a newcomer (human or agent) can read
cold. We keep three, and recommend the habit whatever you call them:

- **A notes file for whoever works on the app next** (ours is
  `SESSION_NOTES.md`): the current state of the app, the decisions taken
  and their reasons, the constraints the PI has set, what is pending, and
  how to resume. When working with an AI agent, this is the file it reads
  first, so it must also say which parts are stale; date-stamp sections
  rather than letting old text mislead.
- **A change log for the researchers** (ours is `CHANGELOG.md`): a dated,
  numbered record of what changed and why, in plain language, so a
  co-author can see what happened without reading code.
- **A task-logic note** (see §0): for each task, what the source document
  says, what the app does, the departure, the construct, the test and the
  field names. This is the bridge between the pre-analysis plan and the
  code, and the document a reviewer checks the app against. It carries no
  author list; authorship of the paper is decided elsewhere.

Rules for what goes into these files:

- **Record only what was established.** A remark in a conversation is not
  a fact for a design note. Do not characterize results that live in the
  analysis; point to them. Categorical shorthand ("null effects",
  "deception") written into a note will be read as truth by the next
  reader.
- **Deviations from a registered design get a dated amendment**, with the
  reason, before the first real session.
- **Secrets never go into notes**: passwords, keys and PINs live in
  environment variables; the notes say where to find them.

Process habits that paid for themselves:

- **Independent review before fielding.** Someone (or an agent) who did
  not build the app reads the code against the documents. In our case
  such reviews caught a treatment arm that was silently never assigned,
  fields that were never stored, random seeds that changed between
  processes, claims in the design note the app could not compute, edge
  cases where the screen promised more than the code delivered, and
  credentials in the notes.
- **Separate consents for separate purposes.** Anything optional (a
  mailing list, future contact) is asked after the debrief, and answering
  "No" changes nothing else.
- **A facilitator manual as a deliverable**: one page per screen the
  implementer must recognize in the monitor, the in-room procedure, and
  what each admin button does to the data.
- **Academic honesty is categorical.** We frame strategically for
  committees; we never fabricate or massage. When our own salary data
  showed that the careers we call "prioritized" do not uniformly out-earn
  the others, the note says: we do not massage this.

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
