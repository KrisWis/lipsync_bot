from Config import CRYPTO_BOT_TOKEN
# Aiocryptopay - это библиотека Python, обычно используемая в веб-сервисах, REST, биткойн-приложениях.
from aiocryptopay import AioCryptoPay


async def get_crypto_bot_sum(summa: float, currency: str):
    # Инициализируем инстанс AioCryptoPay
    cryptopay = AioCryptoPay(CRYPTO_BOT_TOKEN)

    # get_exchange_rates() нужен для получения обменных курсов поддерживаемых валют.
    courses = await cryptopay.get_exchange_rates()

    # Закрываем соединение к cryptopay, т.к больше она в этой функции не используется.
    await cryptopay.close()

    # Проходимся по всем курсам и сверяем данные
    for course in courses:
        if course.source == currency and course.target == 'USD':
            return round(float(summa / course.rate), 2)
        

# Функция для проверки оплаты
async def check_crypto_bot_invoice(invoice_id: int):
    cryptopay = AioCryptoPay(CRYPTO_BOT_TOKEN)

    # get_invoices используется для получения счетов-фактур вашего приложения.
    invoice = await cryptopay.get_invoices(invoice_ids=invoice_id)
    await cryptopay.close()

    if invoice.status == 'paid':
        return True

    return False


tariffs = {
    1: {
        'name': '🐣 Новичок',
        'count': 10,
        'amount': 250
    },
    2: {
        'name': '🥉 Базовый',
        'count': 20,
        'amount': 450
    },
    3: {
        'name': '🥈 Продвинутый',
        'count': 30,
        'amount': 650
    },
    4: {
        'name': '🥇 Тариф-Mega',
        'count': 50,
        'amount': 900
    },
    5: {
        'name': '🎖 Тариф-Ultra',
        'count': 100,
        'amount': 1500
    }
}
