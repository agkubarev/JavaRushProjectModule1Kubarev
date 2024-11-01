from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, \
    CallbackQueryHandler, CommandHandler, ContextTypes

from credentials import ChatGPT_TOKEN
from util import load_message, send_image, send_text, show_main_menu, \
                 load_prompt, send_text_buttons
from gpt import ChatGptService


async def random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Функция для предоставления интересного факта из chat GPT"""
    prompt = load_prompt('random')
    await send_image(update, context, 'random')
    message = load_message('random')
    message = await send_text(update, context, message)
    answer = await chat_gpt.send_question(prompt, '')
    await message.edit_text(answer)


async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Функция, которая перехватывает событие 'gpt' """
    context.user_data['mode'] = 'gpt'
    prompt = load_prompt('gpt')
    message = load_message('gpt')
    chat_gpt.set_prompt(prompt)
    await send_image(update, context, 'gpt')
    await send_text(update, context, message)


async def gpt_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Функция, которая управляет взаимодействием с chat GPT"""
    if context.user_data['mode'] == 'recomend':
        text = f"recomend_type={context.user_data['recomend_type']}"
        text = f"{text} recomend_wishes={context.user_data['recomend_wishes']}"
    else:
        text = update.message.text

    message = await send_text(update, context, 'Думаю над вопросом...')
    answer_gpt = await chat_gpt.add_message(text)

    if context.user_data['mode'] == 'quiz':
        if answer_gpt == 'Правильно!':
            context.user_data['right_answers'] += 1
        answer_gpt = f"{answer_gpt}. Количество правильных ответов: {context.user_data['right_answers']}"
        await send_text_buttons(update, context, answer_gpt, {
            'quiz_more': 'Ещё вопрос'})
    else:
        await message.edit_text(answer_gpt)


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текста в боте"""
    if context.user_data['mode'] == 'gpt':
        await gpt_dialog(update, context)
    elif context.user_data['mode'] == 'echo':
        message = update.message.text
        await send_text(update, context, message)
    elif context.user_data['mode'] == 'talk':
        await gpt_dialog(update, context)
    elif context.user_data['mode'] == 'quiz':
        await gpt_dialog(update, context)
    elif context.user_data['mode'] == 'recomend':
        context.user_data['recomend_wishes'] = update.message.text
        await gpt_dialog(update, context)
    else:
        await start(update, context)


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Перехват события 'echo'"""
    context.user_data['mode'] = 'echo'


async def talk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Перехват события 'talk'"""
    context.user_data['mode'] = 'talk'
    message = load_message('talk')
    await send_text_buttons(update, context, message, {
        'talk_cobain': 'Курт Кобейн - Солист группы Nirvana',
        'talk_queen': 'Елизавета II - Королева Соединённого Королевства',
        'talk_tolkien': 'Джон Толкиен - Автор книги "Властелин Колец"',
        'talk_nietzsche': 'Философ',
        'talk_hawking': 'Физик'})


async def talk_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора персоны для диалога"""
    await update.callback_query.answer()
    query = update.callback_query.data
    prompt = load_prompt(query)
    chat_gpt.set_prompt(prompt)
    text = load_message(query)
    await send_image(update, context, query)
    await send_text(update, context, text)


async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Перехват события 'quiz'"""
    context.user_data['mode'] = 'quiz'
    message = load_message('quiz')
    await send_image(update, context, 'quiz')
    await send_text_buttons(update, context, message, {
        'quiz_prog': 'Программирование на языке python',
        'quiz_math': 'Математические теории, теории алгоритмов, теории множеств и матанализа',
        'quiz_biology': 'Биология'
    })


async def quiz_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Перехват выбора темы квиза"""
    await update.callback_query.answer()
    query = update.callback_query.data
    if query != 'quiz_more':
        context.user_data['right_answers'] = 0
        prompt = load_prompt('quiz')
        chat_gpt.set_prompt(prompt)
    message = await send_text(update, context, 'Думаю над вопросом...')
    question_gpt = await chat_gpt.add_message(query)
    await message.edit_text(question_gpt)


async def recomend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Перехват события 'recomend'"""
    context.user_data['recomend_type'] = None
    context.user_data['recomend_wishes'] = None
    context.user_data['mode'] = 'recomend'
    message = load_message('recomend')
    await send_image(update, context, 'recomend')
    await send_text_buttons(update, context, message, {
        'recomend_book': 'Книга',
        'recomend_film': 'Фильм',
    })


async def recomend_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Перехват нажатия кнопки в событии 'recomend'"""
    await update.callback_query.answer()
    query = update.callback_query.data
    buttons = {}
    context.user_data['recomend_type'] = None
    context.user_data['recomend_wishes'] = None
    if query == 'recomend_book':
        buttons = {'type_book_poetry': 'Поззия',
                   'type_book_drama': 'Драма',
                   'type_book_prose': 'Проза'}
    elif query == 'recomend_film':
        buttons = {'type_film_action': 'Боевик',
                   'type_film_comedy': 'Комедия',
                   'type_film_drama': 'Драма',
                   'type_film_thriller': 'Триллер',
                   'type_film_melodrama': 'Мелодрама'}
    message = load_message('recomend_type')
    await send_text_buttons(update, context, message, buttons)


async def recomend_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Перехват выбора жанра"""
    await update.callback_query.answer()
    query = update.callback_query.data
    context.user_data['recomend_type'] = query
    message = load_message('recomend_wishes')
    await send_text(update, context, message)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало работы бота"""
    context.user_data['mode'] = None
    text = load_message('main')
    await send_image(update, context, 'main')
    await send_text(update, context, text)
    await show_main_menu(update, context, {
        'start': 'Главное меню',
        'echo': 'Переписка с самим собой',
        'random': 'Узнать случайный интересный факт 🧠',
        'gpt': 'Задать вопрос чату GPT 🤖',
        'talk': 'Поговорить с известной личностью 👤',
        'quiz': 'Поучаствовать в квизе ❓',
        'recomend': 'Получить рекомендацию фильма или книги 🍿📚'

    })


app = ApplicationBuilder().token("7696227821:AAHwXQV3-jZoBKCNvafDbi3D8eMQZo4gCnY").build()
chat_gpt = ChatGptService(ChatGPT_TOKEN)
app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler('random', random))
app.add_handler(CommandHandler('gpt', gpt))
app.add_handler(CommandHandler('echo', echo))
app.add_handler(CommandHandler('talk', talk))
app.add_handler(CommandHandler('quiz', quiz))
app.add_handler(CommandHandler('recomend', recomend))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
app.add_handler(CallbackQueryHandler(talk_answer, pattern='^talk_.*'))
app.add_handler(CallbackQueryHandler(recomend_answer, pattern='^recomend_.*'))
app.add_handler(CallbackQueryHandler(recomend_type, pattern='^type_.*'))
app.add_handler(CallbackQueryHandler(quiz_answer, pattern='^quiz_.*'))
app.run_polling()