import random
from typing import Dict, List

import tgalice
import attr
import yaml

from tgalice.cascade import Pr
from tgalice.utils.serialization import Serializeable

from cascade import csc, Turn


@attr.s
class Exercise(Serializeable):
    text: str = attr.ib()
    full_text: str = attr.ib(default=None)
    out: str = attr.ib(default=None)
    one_sided: bool = attr.ib(default=False)
    image: str = attr.ib(default=None)


with open('texts/exercises.yaml', 'r', encoding='utf-8') as f:
    EXERCISES: Dict[int, Exercise] = {k: Exercise.from_dict(v) for k, v in yaml.safe_load(f).items()}

with open('texts/hints.yaml', 'r', encoding='utf-8') as f:
    HINTS: List[str] = yaml.safe_load(f)


COUNTERS = [
    'dialogs-upload/468b181f-b155-4fb1-abe7-9605e61d40cb/96f0b001-c9df-4470-9e02-20ff499970be.opus',
    'dialogs-upload/468b181f-b155-4fb1-abe7-9605e61d40cb/6f04bb5f-dacb-4079-aac0-f9463f6ae1c2.opus',
    'dialogs-upload/468b181f-b155-4fb1-abe7-9605e61d40cb/a78a543d-fbbb-47fb-b8e6-10661d316fce.opus',
    'dialogs-upload/468b181f-b155-4fb1-abe7-9605e61d40cb/476d2c14-004b-4d02-8393-df0e9b203c49.opus',
    'dialogs-upload/468b181f-b155-4fb1-abe7-9605e61d40cb/decebca8-51d6-408c-8308-173681cf377f.opus',
]


@csc.add_handler(intents=['start_training', 'choose_day'], priority=Pr.STRONG_INTENT)
@csc.add_handler(intents=['yes'], priority=Pr.WEAK_STAGE, stages=['suggest_start_training'])
def exercise(turn: Turn):
    day_id = turn.us.last_day or 1
    if 'choose_day' in turn.forms:
        day_id = int(turn.forms['choose_day']['day'])
        turn.us.day_is_complete = False
        turn.us.current_step = 0
    if turn.us.day_is_complete:
        turn.us.day_is_complete = False
        day_id += 1
        turn.us.current_step = 0
    do_exercise(turn=turn, day_id=day_id)


@csc.add_handler(intents=['next'], priority=Pr.WEAK_STAGE, stages=['exercise'])
def next_exercise(turn: Turn):
    do_exercise(turn=turn, day_id=turn.us.last_day)


@csc.add_handler(intents=['yes'], priority=Pr.WEAK_STAGE, stages=['suggest_restart'])
def next_exercise(turn: Turn):
    turn.us.day_is_complete = False
    turn.us.current_step = 0
    turn.us.last_day = 1
    do_exercise(turn=turn, day_id=1)


def do_exercise(turn: Turn, day_id: int, step_id: int = None):
    step_id = step_id or turn.us.current_step or 0

    if day_id == 31:
        turn.response_text = 'Вы закончили всю программу! Хотите начать заново с первого дня?'
        turn.stage = 'suggest_restart'
        turn.suggests.append('да')
        return
    if day_id not in EXERCISES:
        turn.response_text = 'Такого дня в программе тренировок нет! Назовите день от 1 до 30.'
        return
    last_ex: Exercise = EXERCISES[day_id]

    if step_id >= 7 or step_id >= 6 and day_id < 5:
        out = last_ex.out or random.choice(HINTS)
        turn.response_text = out
        turn.commands.append(tgalice.COMMANDS.EXIT)
        turn.us.day_is_complete = True
        return

    if step_id == 0:
        turn.response_text = f'Начинаем день {day_id}. ' \
                             f'\nДля начала разомнитесь: побегайте, попрыгайте, поприседайте. ' \
                             f'\nКогда будете готовы к растяжке, скажите "дальше".'
        turn.suggests.append('дальше')
    else:
        if step_id == 6:
            ex = last_ex
        else:
            ex = EXERCISES[step_id]

        if ex.full_text:
            turn.response_text = f'<text>{ex.text}</text><voice>{ex.full_text}</voice>'
        else:
            turn.response_text = ex.text

        turn.response_text += f'<speaker audio="{random.choice(COUNTERS)}">'
        if not ex.one_sided:
            turn.response_text += '<voice>Теперь другая сторона.</voice>'
            turn.response_text += f'<speaker audio="{random.choice(COUNTERS)}">'
        turn.image_id = ex.image

    step_id += 1
    turn.us.current_step = step_id
    turn.us.last_day = day_id
    turn.stage = 'exercise'
    turn.suggests.append('дальше')
