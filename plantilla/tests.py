from otree.api import Bot, SubmissionMustFail, expect
from plantilla_common import quadratic_tokens
from . import (Intro, Likert, Matriz, Chips, Probabilidad, Dial, Escalera1, Escalera2, Escalera3,
               Ranking, Presupuesto, Tarjetas, Comprension, Tarea, Resultados, ITEMS, STAIR_AMOUNTS, C)


def call_live_method(method, group, page_class, **kwargs):
    """Drive the timed task's server-side grading directly (CLI bots do not run JS)."""
    if page_class is not Tarea:
        return
    for p in group.get_players():
        n = 2 + p.participant.id_in_session
        for k in range(n):
            Tarea.live_method(p, dict(a=10 + k, b=20, val=30 + k))
        Tarea.live_method(p, dict(a=11, b=11, val=99))       # wrong
        Tarea.live_method(p, dict(a=5, b=11, val=16))        # rejected: out of range


class PlayerBot(Bot):
    def play_round(self):
        pid = self.participant.id_in_session
        yield Intro
        yield SubmissionMustFail(Likert, dict(riesgo_qual=11))
        yield Likert, dict(riesgo_qual=pid % 11)
        incomplete = {f'gusta_{k}': 1 + (pid % 10) for k, _ in ITEMS[:-1]}
        yield SubmissionMustFail(Matriz, incomplete)
        yield Matriz, {f'gusta_{k}': 1 + ((pid + i) % 10) for i, (k, _) in enumerate(ITEMS)}
        yield SubmissionMustFail(Chips, dict(ingreso=15000))            # not a bracket
        yield Chips, dict(ingreso=17500)
        yield SubmissionMustFail(Probabilidad, dict(prob=55))           # off the grid
        yield Probabilidad, dict(prob=10 * (pid % 11))
        expect(self.participant.vars['tokens']['prob'] in [float(quadratic_tokens(10 * (pid % 11), r)) for r in (0, 100)], True)
        yield SubmissionMustFail(Dial, dict(pct_dial=101))               # out of range
        yield SubmissionMustFail(Dial, dict())                           # untouched dial
        yield Dial, dict(pct_dial=37)
        expect(self.player.pct_dial, 37)
        expect(0 <= self.participant.vars['tokens']['dial'] <= 10, True)
        qs = [(pid >> k) & 1 for k in range(3)]
        for i, page in enumerate([Escalera1, Escalera2, Escalera3]):
            node = 1
            for j in range(i):
                node = 2 * node + (0 if qs[j] == 1 else 1)
            expect(page.vars_for_template(self.player)['sure_amount'], STAIR_AMOUNTS[node])
            yield page, {f'esc_q{i + 1}': qs[i]}
        expect(1 <= self.player.esc_value <= 8, True)
        keys = [k for k, _ in ITEMS]
        bad = {f'rank_{k}': 1 for k in keys}                            # duplicates
        yield SubmissionMustFail(Ranking, bad)
        yield Ranking, {f'rank_{k}': i + 1 for i, k in enumerate(keys)}
        expect(self.participant.vars['rank_final'].split(',')[0], keys[0])
        yield SubmissionMustFail(Presupuesto, dict(fichas_econ=50, fichas_salud=50, fichas_ing=10))
        yield Presupuesto, dict(fichas_econ=50, fichas_salud=30, fichas_ing=20)
        yield Tarjetas, dict(carrera='economia')
        yield SubmissionMustFail(Comprension, dict(comp=1))
        yield Comprension, dict(comp=2)
        expect(self.player.comp_intentos, 2)
        yield Tarea
        expect(self.player.correctas, 2 + pid)
        expect(self.player.intentos, 3 + pid)
        expect(self.participant.vars['tokens']['tarea'], float(2 + pid))
        # Resultados is the terminal page (no button): nothing to submit.
