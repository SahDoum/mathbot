from models import IUMCourse
from utils import bot, get_course_args


def cmd_add_course(message):
    text = 'Формат:\n' \
           'url\n' \
           'name\n' \
           'lecturers\n' \
           'place\n' \
           'program_url\n' \
           'timetable wday|hs|ms|he|me'

    bot.reply_to(message, text)
    bot.register_next_step_handler(message, add_course)


def add_course(message):
    lines = message.text.splitlines()
    course_args = get_course_args(lines)
    if course_args:
        IUMCourse.create(**course_args)
    else:
        bot.reply_to(message, 'Извините, неправильный формат данных')
