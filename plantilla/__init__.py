"""
plantilla — one page per widget pattern. Copy the page + template you
need into your own app; every pattern is click-only, mobile-first and
validated on both client (ui.js) and server.

Pages (in order):
  Intro         instruction page (info-cards; says only what is needed)
  Likert        one 0-10 dots question
  Matriz        one topic, several items as rows, dots (1-10)
  Chips         categorical brackets stored as numeric midpoints
  Probabilidad  0-100 by 10 dots, paid by a proper scoring rule (coarse grid)
  Dial          continuous 0-100 by moving a dial; starts empty; paid by the same rule
  Escalera1-3   adaptive two-card choice (staircase), 3 levels demo
  Ranking       two-list drag: pool -> "Tu orden", never pre-filled
  Presupuesto   100 fichas across areas, live remainder, sum enforced
  Tarjetas      long option list as clickable radio cards (formfield)
  Comprension   comprehension check: parallel options, forced retry
  Tarea         timed real-effort task, server-graded via live_method
  Resultados    tokens summary (tokens = raffle tickets)
"""
import random as _random

from otree.api import *
from plantilla_common import (
    LIKERT_0_10, LIKERT_1_10, PCT_0_100, STEP_0_20, INGRESO_CHOICES, dots,
    stable_seed, add_tokens, total_tokens, quadratic_tokens,
    staircase_node, staircase_value,
)


doc = """Plantilla: un ejemplo funcional de cada tipo de pregunta (dots, matriz, chips, probabilidad, dial continuo, escalera, ranking arrastrable, presupuesto, tarjetas, comprensión, tarea cronometrada)."""


ITEMS = [  # rows of the matrix demo (use your own list)
    ['a', 'Ingeniería'], ['b', 'Derecho'], ['c', 'Medicina'], ['d', 'Psicología'],
]
AREAS = [['econ', 'Economía'], ['salud', 'Salud'], ['ing', 'Ingeniería']]
STAIR_AMOUNTS = [0, 16, 24, 8, 28, 20, 12, 4]   # heap, 3 levels (index 1..7)


class C(BaseConstants):
    NAME_IN_URL = 'plantilla'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    LOTTERY = 30
    BUDGET = 100
    TAREA_SECONDS = 30
    ENDOWMENT = 20


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


def _matrix_fields():
    return {f'gusta_{k}': models.IntegerField(label=n, choices=LIKERT_1_10) for k, n in ITEMS}


def _rank_fields():
    return {f'rank_{k}': models.IntegerField(label=n, min=1, max=len(ITEMS)) for k, n in ITEMS}


class Player(BasePlayer):
    # Likert (single)
    riesgo_qual = models.IntegerField(label="¿Qué tan dispuesta estás, como persona, a tomar riesgos?", choices=LIKERT_0_10)
    # Matriz + Ranking (one field per row)
    locals().update(_matrix_fields())
    locals().update(_rank_fields())
    # Chips (bracket midpoints)
    ingreso = models.IntegerField(label="¿Cuánto crees que gana al mes, en su primer año, alguien que estudió Ingeniería?", choices=INGRESO_CHOICES)
    # Probabilidad (paid by a scoring rule)
    prob = models.IntegerField(label="¿Qué tan probable es que tu puntaje esté arriba de la mediana?", choices=PCT_0_100)
    # Dial (continuous 0-100, no typing, no coarse grid)
    pct_dial = models.IntegerField(min=0, max=100, label="De cada 100, ¿cuántas personas obtuvieron un puntaje menor que el tuyo?")
    # Escalera (adaptive two-card choice)
    esc_q1 = models.IntegerField(choices=[[1, 'Lotería'], [0, 'Seguro']])
    esc_q2 = models.IntegerField(choices=[[1, 'Lotería'], [0, 'Seguro']])
    esc_q3 = models.IntegerField(choices=[[1, 'Lotería'], [0, 'Seguro']])
    esc_value = models.IntegerField(blank=True)
    # Presupuesto
    fichas_econ = models.IntegerField(choices=PCT_0_100, label="Economía")
    fichas_salud = models.IntegerField(choices=PCT_0_100, label="Salud")
    fichas_ing = models.IntegerField(choices=PCT_0_100, label="Ingeniería")
    # Tarjetas (long list, formfield radio)
    carrera = models.StringField(
        label="¿Cuál es la carrera que MÁS te gustaría estudiar?",
        choices=[['economia', 'Economía'], ['ingenieria', 'Ingeniería'], ['salud', 'Ciencias de la Salud'],
                 ['derecho', 'Derecho'], ['otra', 'Otra'], ['indeciso', 'Aún no lo he decidido']],
        widget=widgets.RadioSelect)
    # Comprension (forced retry; count attempts)
    comp = models.IntegerField(
        label="Supón que tu monto fue 12 tokens y el precio sorteado 8. ¿Qué pasa?",
        choices=[[1, 'Pago 12 tokens y no veo el resultado.'], [2, 'Pago 8 tokens y no veo el resultado.'],
                 [3, 'Pago 8 tokens y veo el resultado.'], [4, 'No pago nada y veo el resultado.']],
        widget=widgets.RadioSelect)
    comp_intentos = models.IntegerField(initial=0)
    # Tarea (timed, server-graded)
    correctas = models.IntegerField(initial=0)
    intentos = models.IntegerField(initial=0)


# ── Pages ─────────────────────────────────────────────────────────────────
class Intro(Page):
    pass


class Likert(Page):
    form_model = 'player'
    form_fields = ['riesgo_qual']

    @staticmethod
    def vars_for_template(player):
        return dict(choices=dots(LIKERT_0_10))


class Matriz(Page):
    form_model = 'player'
    form_fields = [f'gusta_{k}' for k, _ in ITEMS]

    @staticmethod
    def vars_for_template(player):
        return dict(rows=[dict(field=f'gusta_{k}', nombre=n) for k, n in ITEMS],
                    choices=dots(LIKERT_1_10))


class Chips(Page):
    form_model = 'player'
    form_fields = ['ingreso']

    @staticmethod
    def vars_for_template(player):
        return dict(choices=dots(INGRESO_CHOICES))


class Probabilidad(Page):
    form_model = 'player'
    form_fields = ['prob']

    @staticmethod
    def vars_for_template(player):
        return dict(choices=dots(PCT_0_100))

    @staticmethod
    def before_next_page(player, timeout_happened):
        # Demo: pay against a seeded "realized" outcome; in a real app the
        # realized value comes from the data (e.g. the session median).
        realized = 100 if stable_seed(player.participant.code, 'demo') % 2 else 0
        add_tokens(player, 'prob', quadratic_tokens(player.prob, realized))


class Dial(Page):
    form_model = 'player'
    form_fields = ['pct_dial']

    @staticmethod
    def error_message(player, values):
        v = values.get('pct_dial')
        if v is None or not (0 <= int(v) <= 100):
            return "Mueve el dial para responder."

    @staticmethod
    def before_next_page(player, timeout_happened):
        # Demo: paid against a seeded realized percentile; a real app uses the data.
        realized = stable_seed(player.participant.code, 'dial') % 101
        add_tokens(player, 'dial', quadratic_tokens(player.pct_dial, realized))


class _Escalera(Page):
    form_model = 'player'
    template_name = 'plantilla/Escalera.html'
    level = 1

    @classmethod
    def get_form_fields(cls, player):
        return [f'esc_q{cls.level}']

    @classmethod
    def vars_for_template(cls, player):
        answers = [player.field_maybe_none(f'esc_q{i}') for i in range(1, cls.level)]
        return dict(level=cls.level, n=3, loteria=C.LOTTERY,
                    sure_amount=STAIR_AMOUNTS[staircase_node(answers, cls.level)],
                    field_name=f'esc_q{cls.level}')


class Escalera1(_Escalera):
    level = 1


class Escalera2(_Escalera):
    level = 2


class Escalera3(_Escalera):
    level = 3

    @staticmethod
    def before_next_page(player, timeout_happened):
        answers = [player.field_maybe_none(f'esc_q{i}') for i in range(1, 4)]
        player.esc_value = staircase_value(answers)


class Ranking(Page):
    form_model = 'player'
    form_fields = [f'rank_{k}' for k, _ in ITEMS]

    @staticmethod
    def vars_for_template(player):
        pv = player.participant.vars
        if not pv.get('rank_orden'):
            keys = [k for k, _ in ITEMS]
            _random.Random(stable_seed(player.participant.code, 'rank')).shuffle(keys)
            pv['rank_orden'] = ','.join(keys)
        by = dict(ITEMS)
        return dict(rows=[dict(key=k, nombre=by[k]) for k in pv['rank_orden'].split(',')])

    @staticmethod
    def error_message(player, values):
        ranks = [values.get(f'rank_{k}') for k, _ in ITEMS]
        if sorted(r for r in ranks if r is not None) != list(range(1, len(ITEMS) + 1)):
            return "Pasa todas las opciones a «Tu orden»."

    @staticmethod
    def before_next_page(player, timeout_happened):
        order = sorted((k for k, _ in ITEMS), key=lambda k: player.field_maybe_none(f'rank_{k}') or 99)
        player.participant.vars['rank_final'] = ','.join(order)


class Presupuesto(Page):
    form_model = 'player'
    form_fields = ['fichas_econ', 'fichas_salud', 'fichas_ing']

    @staticmethod
    def vars_for_template(player):
        return dict(budget=C.BUDGET, choices=dots(PCT_0_100),
                    rows=[dict(field=f'fichas_{k}', nombre=n) for k, n in AREAS])

    @staticmethod
    def error_message(player, values):
        total = sum(int(values.get(f'fichas_{k}') or 0) for k, _ in AREAS)
        if total != C.BUDGET:
            return f"Los puntos deben sumar exactamente {C.BUDGET} (ahora suman {total})."


class Tarjetas(Page):
    form_model = 'player'
    form_fields = ['carrera']


class Comprension(Page):
    form_model = 'player'
    form_fields = ['comp']

    @staticmethod
    def error_message(player, values):
        player.comp_intentos += 1
        if values['comp'] != 2:
            # Restate the RULE, never the answer.
            return ("Respuesta incorrecta. Recuerda: si tu monto es mayor o igual al "
                    "precio sorteado, pagas el precio (no tu monto) y no ves el "
                    "resultado. Inténtalo otra vez.")


class Tarea(Page):
    timeout_seconds = C.TAREA_SECONDS

    @staticmethod
    def js_vars(player):
        return {'duration_s': C.TAREA_SECONDS}

    @staticmethod
    def live_method(player, data):
        """Grade every confirmed answer server-side, as it arrives, so a
        dead tab or a force-advance never zeroes the score."""
        try:
            a, b, val = int(data.get('a')), int(data.get('b')), int(data.get('val'))
        except (TypeError, ValueError):
            return {player.id_in_group: dict(attempts=player.intentos)}
        if 10 <= a <= 99 and 10 <= b <= 99:
            player.intentos += 1
            if val == a + b:
                player.correctas += 1
        return {player.id_in_group: dict(attempts=player.intentos)}

    @staticmethod
    def before_next_page(player, timeout_happened):
        add_tokens(player, 'tarea', float(player.correctas))


class Resultados(Page):
    @staticmethod
    def vars_for_template(player):
        return dict(tokens=player.participant.vars.get('tokens') or {},
                    total=total_tokens(player.participant))


page_sequence = [Intro, Likert, Matriz, Chips, Probabilidad, Dial, Escalera1, Escalera2, Escalera3,
                 Ranking, Presupuesto, Tarjetas, Comprension, Tarea, Resultados]
