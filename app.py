import re
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from telethon.tl.types import KeyboardButtonCallback

# اطلاعات API و شماره تلفن (برای کاربر شخصی)
api_id = 22987403
api_hash = '0a0b2c4093ddee4dcdb84895c591365d'

# سشن ذخیره شده (رشته سشن که قبلاً تولید شده)
user_session_string = '1BJWap1sBuxqnj3jRJpzjOKuFsM1dHLYIIlYUt9RXDU0a7o-FHDnXP3bvFM866I6TDjyC7KMUx-dElTKcSyikXFWVL8aSYkQd8gNQSGfDXKuzfsplZ-EcfNLeCMJ-Qm5zefJDD1KsAF_2Rfi50vNW-NnDnpv3TH9jtJWzYCMFuWdRXwdJq5lMFfWsU0Gl2fh1XggI12wpDbPj6VjiZCV36uGq_7L5cB29ZRvZSt983dLdqufNnjbK0HxwnmQTqJAwrAAsnJXLm8ugHK4xPdppFoUUFuMgRAFgzWFCrZnSOdWT8XUhtpG6RLWn1AINIxMy19iQ9U8TUZGYuxTgEUbSTZ_8n5jacpQ='
bot_session_string = '1BJWap1sBu1AXaqRpv6RMwD84a45X4Or2gEq-WBDXeUjPB-iHlcjh0dmX2BctoPiR9G_W4ayUSrYNrxhTJS7vJ-v9ibrzElc1keLEht3YMXvA-CmMgeo3M2IfVf-imkm5bT2Z82040GH5wuzY7wMzCfjTv1fjitgTEfxbLxQlHRelBgpVTg8svja9q09AYGv8xcOF2tyjsyzuhx7Eyz2QWUykDbjr8Ct5cOp2Me30AZuAZdti4LuxNPsvsIfb0i_Jd-COlQagY8X9EymtSqSFeemHoJTyowxXTqzBgsEQ0N2Z3rhdbrVT8EhDE6OuqUtiS51KrXdYrHR8v3o4xxekvBZCR0AvIfs='

# توکن ربات (برای ارسال پیام)
bot_token = '7533266828:AAEERKEbeldNTaoqKV3QfCTrvPmsBtpop6Q'

# کانال‌ها
source_channels = {
    'آخرین قیمت انس جهانی': 't.me/XauusdPricenews',
    'آخرین نرخ درهم به تومان': 't.me/nerkharzazad',
    'آخرین نرخ تتر به تومن': 't.me/istanbul_tether'
}

# شناسه کانال مقصد
destination_channel = 't.me/Nerkh1dolari'

def contains_number(text):
    return bool(re.search(r'\d', text))

def process_message(channel_name, message_text):
    if channel_name == 'آخرین نرخ تتر به تومن':
        # حذف "آخرین نرخ تتر به تومن:" و "istanbulexchange.com" از پیام
        message_text = re.sub(r'آخرین نرخ تتر به تومن:\s*', '', message_text)
        message_text = re.sub(r'\s*istanbulexchange\.com\s*', '', message_text)
    return message_text.strip()

async def get_last_message_with_number(client, channel):
    async for message in client.iter_messages(channel):
        if message.text and contains_number(message.text):
            return message
    return None

async def main():
    # ساخت کلاینت‌های تلگرام با استفاده از سشن‌ها
    user_client = TelegramClient(StringSession(user_session_string), api_id, api_hash)
    bot_client = TelegramClient(StringSession(bot_session_string), api_id, api_hash)

    # شروع کلاینت‌ها
    await user_client.start()
    await bot_client.start(bot_token=bot_token)

    last_message_id = None

    # هندل کردن پیام /start
    @bot_client.on(events.NewMessage(pattern='/start'))
    async def handler(event):
        buttons = [
            [KeyboardButtonCallback(name, channel.encode()) for name, channel in source_channels.items()]
        ]
        await bot_client.send_message(destination_channel, "برای دیدن بروزترین قیمت‌ها، یکی از گزینه‌های زیر را انتخاب کنید:", buttons=buttons)

    # هندل کردن کلیدهای فراخوانی شده (CallbackQuery)
    @bot_client.on(events.CallbackQuery)
    async def callback(event):
        nonlocal last_message_id
        channel = event.data.decode()
        message = await get_last_message_with_number(user_client, channel)

        if message:
            # حذف پیام قبلی اگر وجود داشته باشد
            if last_message_id:
                await bot_client.delete_messages(destination_channel, last_message_id)

            # پردازش پیام
            channel_name = next((name for name, url in source_channels.items() if url == channel), "نامشخص")
            processed_message = process_message(channel_name, message.text)

            # ارسال پیام جدید و ذخیره شناسه آن
            new_message = await bot_client.send_message(destination_channel, f"{channel_name}:\n{processed_message}", buttons=[
                [Button.inline("بروزرسانی", channel.encode())]
            ])
            last_message_id = new_message.id
        else:
            await bot_client.send_message(destination_channel, "پستی با اعداد یافت نشد.")

    await bot_client.run_until_disconnected()
    await user_client.run_until_disconnected()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
