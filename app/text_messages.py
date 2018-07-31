from settings import CHANNEL_NAME, BOT_NAME

text_messages = {
    'help':
        (f"Это бот для удобной навигации по каталогу математических книг {CHANNEL_NAME}\n"
         "\n"
         "Для начала навигации вызовите любую команду: /lib /lit /catalog\n"
         "\n"
         "Для того, чтобы сбросить книгу в диалог, воспользуйтесь inline-режимом: "
         f"наберите в сообщении {BOT_NAME} и поисковый запрос\n"
         "\n"
         "Если вы хотите помочь с наполнением каталога, пишите @AChekhonte\n"
         "\n"
         "По поводу поддержки пишите @MikhailTikhonov"),

    'admin':
        'Используйте следующие команды:\n'
        '/addcatalog <название каталога> — для добавления нового каталога (все названия уникальны)\n'
        '/add — для добавления новой книги \n'
        '/edit — для редактирования \n',

    'links':
        'Список чатов в Телеграм:\n'
        '1. [НМУ 2017+]'
        '(https://t.me/ium2017)\n'
        '2. [НМУ Геометрия-1]'
        '(https://t.me/ium_geom)\n'
        '3. [НМУ Матан-1]'
        '(https://t.me/ium_analysis)\n'
        '4. [НМУ Алгебра-1]'
        '(https://t.me/ium_algebra)\n'
        '5. [НМУ Топология-1]'
        '(https://t.me/joinchat/A5wx2gxJoquD_1JuCLAr7w)\n'
        '6. [НМУ Задачи и только задачи]'
        '(https://t.me/ium_zadachi)\n'
        '7. [Discord Конференция по задачам]'
        '(https://discord.gg/kHSBukP)\n\n'
        '8. [Infernal Math]'
        '(https://t.me/joinchat/AAAAAEFHT_BkBsc_HgiTvg)\n'
        '9. [Канал МЦНМО]'
        '(https://t.me/cme_channel)\n'
        '10. [Геометрия-канал]'
        '(https://t.me/geometrykanal)\n'
        '11. [Геометрический чатик]'
        '(https://t.me/geometrychat)\n'
        '12. [Флудилка Мехмата]'
        '(https://t.me/mechmath)\n'
        '13. [МехМат МГУ 2017]'
        '(https://t.me/mechmath2017)\n'
        '14. [Канал Сосиска в тесте]'
        '(https://t.me/mathcatalog)\n',

    'inline_mode':
        '_Попробуйте набрать в поле для сообщения_ @sosiska\_v\_teste\_bot '
        '_и название/автора/раздел книги, чтобы быстро скинуть её в чат._'
}