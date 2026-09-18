"""
plantilla_common.py — helpers every task app imports.

Copy this file into a new project as `<project>_common.py` and keep the
pieces you use. Everything here came out of the 2026 classroom build
(otree_beca_mty); see README.md for the rules behind each helper.
"""
import hashlib
import random

# ── Clickable scales (choices for IntegerField; rendered as dots/chips) ──
LIKERT_1_10 = [[i, str(i)] for i in range(1, 11)]
LIKERT_0_10 = [[i, str(i)] for i in range(0, 11)]
PCT_0_100 = [[i, str(i)] for i in range(0, 101, 10)]          # probabilities / percentiles
STEP_0_20 = [[i, str(i)] for i in range(0, 21, 2)]            # amounts out of a 20-token endowment
# Categorical brackets: the STORED value is the bracket midpoint, so the
# field stays numeric; the label is what the participant sees.
INGRESO_CHOICES = [
    [7500, 'Menos de $10 mil'], [12500, '$10 – 15 mil'], [17500, '$15 – 20 mil'],
    [22500, '$20 – 25 mil'], [27500, '$25 – 30 mil'], [35000, 'Más de $30 mil'],
]


def dots(choices):
    """Template-friendly list for the dots/chips partials: [{v, l}, ...]."""
    return [dict(v=v, l=l) for v, l in choices]


# ── Deterministic randomness ──────────────────────────────────────────────
def stable_seed(code: str, salt: str = '') -> int:
    """Process-independent seed from a participant code (Python's hash() is
    salted per process, so it differs across server workers)."""
    return int(hashlib.md5((salt + '|' + code).encode()).hexdigest()[:8], 16)


def seeded_choice(code: str, salt: str, options):
    return random.Random(stable_seed(code, salt)).choice(list(options))


# ── Tokens = raffle tickets (no cash, no 1-of-N selection) ────────────────
def add_tokens(player, source: str, n: float):
    """Record tokens earned from one task. Idempotent per (participant, source)."""
    tokens = player.participant.vars.get('tokens') or {}
    tokens[source] = float(n)
    player.participant.vars['tokens'] = tokens


def total_tokens(participant) -> int:
    return int(round(sum((participant.vars.get('tokens') or {}).values())))


# ── Proper scoring rules (paid in tokens) ─────────────────────────────────
def quadratic_tokens(estimate, realized, max_tokens=10, scale=100.0) -> int:
    """Point estimate of a quantity on [0, scale]: max*(1-((e-r)/scale)^2).
    Proper for the mean; with raffle-ticket payment it is also the
    binarized scoring rule, so risk attitudes do not distort it."""
    if estimate is None or realized is None:
        return max_tokens // 2
    d = (float(estimate) - float(realized)) / scale
    return int(round(max_tokens * max(0.0, 1.0 - d * d)))


def brier_tokens(prob_pct, outcome, max_tokens=5) -> int:
    """Stated probability (0-100) of a binary event: max*(1-(p/100-1[event])^2)."""
    if prob_pct is None or outcome is None:
        return max_tokens // 2
    d = float(prob_pct) / 100.0 - (1.0 if outcome else 0.0)
    return int(round(max_tokens * max(0.0, 1.0 - d * d)))


# ── Adaptive staircase (GPS-style; binary heap of amounts, index 1..2^L-1) ─
def staircase_node(answers, level: int, up_on: int = 1) -> int:
    """Heap node shown at `level` given the answers to levels 1..level-1.
    answers: list of 0/1 (None = 0). If an answer equals `up_on` the next
    node is the left child (2i), else the right child (2i+1)."""
    node = 1
    for i in range(level - 1):
        a = answers[i] if i < len(answers) and answers[i] is not None else 0
        node = 2 * node + (0 if int(a) == up_on else 1)
    return node


def staircase_value(answers) -> int:
    """1..2^n coding of a completed staircase (as in the GPS 1-32 scale)."""
    v = 0
    for a in answers:
        v = 2 * v + (int(a) if a is not None else 0)
    return v + 1
