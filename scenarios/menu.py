import random

import tgalice
import yaml
from tgalice.cascade import Pr

from cascade import csc, Turn

with open('texts/lifehacks.yaml', 'r', encoding='utf-8') as f:
    HACKS = yaml.safe_load(f)


def is_first_turn(turn: Turn) -> bool:
    if turn.ctx.session_is_new():
        return True
    if turn.ctx.source == tgalice.SOURCES.TEXT and not turn.ctx.message_text:
        return True
    if turn.ctx.message_text == '/start':
        return True
    return False


@csc.add_handler(priority=Pr.BEFORE_FALLBACK, checker=is_first_turn)
def hello(turn: Turn):
    turn.response_text = 'Привет!' \
        '\nВ этом навыке уникальная техника и простые упражнения, '\
        'выполняя которые, ты уже через 30 день сможешь сесть на шпагат!'
    if turn.us.current_step:
        turn.response_text += f'\nПродолжим с дня {turn.us.current_step + 1}?'
        turn.suggests.append('да')
        turn.stage = 'suggest_start_training'
    else:
        turn.response_text += '\nСкажите "что ты умеешь", чтобы узнать больше, или "тренировка", чтобы начать растяжку.'
        turn.suggests.append('тренировка')
    turn.suggests.append('что ты умеешь')


@csc.add_handler(priority=Pr.STRONG_INTENT, intents=['help'])
def get_help(turn: Turn):
    # todo: rewrite the help to make it more informative
    turn.response_text = 'Чтобы начать заниматься, скажите "план тренировок".' \
        '\nЧтобы выбрать день занятий, скажите "день 1", "день 2", и так далее.'


@csc.add_handler(priority=Pr.STRONG_INTENT, intents=['what_can_you_do'])
def abilities(turn: Turn):
    turn.response_text = 'Вы можете выбрать любой день тренировки просто сказав или нажав на нужный Вам от 1 до 30.' \
        '\nТакже вы можете ознакомиться с рекомендациями по разминке, сказав "разминка".' \
        '\nВ разделе "лайфхаки" можно получить советы как выстроить свой план тренировок более эффективно.'


@csc.add_handler(priority=Pr.FALLBACK)
def fallback(turn: Turn):
    turn.response_text = 'Я вас не понимаю. Скажите "тренировка", чтобы начать заниматься.'


@csc.add_handler(priority=Pr.STRONG_INTENT, intents=['rules'])
def rules(turn: Turn):
    turn.response_text = 'Перед началом всегда разминаемся.\
    \nРастяжки с первой по пятую - это ваши ОСНОВНЫЕ РАСТЯЖКИ, вы должны делать их каждый день. \
    Первые 5 дней вы делаете первые 5 растяжек как ежедневное комбо! \
    Затем, начиная с 6-го дня, вы просто добавите одно упражнение.'


@csc.add_handler(priority=Pr.STRONG_INTENT, intents=['lifehacks'])
@csc.add_handler(priority=Pr.STRONG_INTENT, intents=['yes'], stages=['suggest_hack'])
def hacks(turn: Turn):
    hack = random.choice(HACKS)
    turn.response_text = f'{hack}\nРассказать ещё лайфхак?'
    turn.stage = 'suggest_hack'
    turn.suggests.append('да')


@csc.add_handler(priority=Pr.STRONG_INTENT, intents=['warmup'])
def warmup(turn: Turn):
    turn.response_text = 'Перед тем как начать, важно разогреть мышцы и суставы. ' \
                         'Побегайте,попрыгайте на месте, приседайте.' \
                         'Подумайте о своих мышцах, как о резиновых лентах, которые от природы эластичны. ' \
                         'Если вы растянете их слишком далеко, прежде чем они будут готовы, ' \
                         'они могут сломаться или получить травму. ' \
                         'Уделите разминке как минимум 10 минут, прежде чем начать выполнять упражнения.'


@csc.add_handler(priority=Pr.STRONG_INTENT, intents=['contra'])
def contra(turn: Turn):
    turn.response_text = 'Далеко не всем показано практиковать растяжку, различные асаны и садиться на шпагат. ' \
                         'Если в этом списке Вы нашли свой “диагноз”, ' \
                         'то это повод задуматься о целесообразности совершаемых действий. \
                            \nИтак, противопоказания: \
                            \n- артроз коленных суставов; \
                            \n- ювенальный ревматоидный артрит; \
                            \n- различные воспаления суставов; \
                            \n- гинекологические проблемы у девушек; \
                            \n- смещение коленной чашечки; \
                            \n- операция на крестообразной подколенной связке; \
                            \n- вес, отличный от нормы (значение выше 10 кг); \
                            \n- высокое давление.'


@csc.add_handler(priority=Pr.STRONG_INTENT, intents=['result'])
def result(turn: Turn):
    turn.response_text = 'Всегда нужно сравнивать результаты ДО и ПОСЛЕ, ' \
                         'иначе как ты  поймёшь, что твой прогресс становиться с каждым днём лучше. ' \
                         'Сделай вот что: после того как мы провели первую тренировку, ' \
                         'сделай фото своего продольного шпагата, ' \
                         'и после прохождения наших занятий я тебе напомню о нём. ' \
                         'Мы сравним результаты, и даю тебе слово, ты удивишься своему прогрессу!'
