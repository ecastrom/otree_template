from os import environ

# otree_template — copy this project to start a new classroom/lab instrument.
# One session config, one demo app with one page per widget pattern.

SESSION_CONFIGS = [
    dict(
        name='plantilla',
        display_name='Plantilla — un ejemplo de cada tipo de pregunta',
        app_sequence=['plantilla'],
        num_demo_participants=3,
    ),
]

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=0.00,
    participation_fee=0.00,
    doc="",
)

# One oTree Room per classroom; launch every session from its Room so the
# room name identifies the classroom in the export.
ROOMS = [dict(name='testing', display_name='Sala de Pruebas')] + [
    dict(name=f'room{i}', display_name=f'Room {i}') for i in range(1, 6)
]

# Cross-app state lives here (exported with the data). Declare every key.
PARTICIPANT_FIELDS = [
    'tokens',            # dict source -> tokens (raffle tickets)
    'rank_orden',        # shuffled pool order shown on the ranking page
    'rank_final',        # final order, keys best -> worst
]
SESSION_FIELDS = []

LANGUAGE_CODE = 'es'
REAL_WORLD_CURRENCY_CODE = 'MXN'
USE_POINTS = False

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')
SECRET_KEY = environ.get('OTREE_SECRET_KEY', 'plantilla-dev-secret')
DEBUG = environ.get('OTREE_PRODUCTION') in (None, '', '0')
