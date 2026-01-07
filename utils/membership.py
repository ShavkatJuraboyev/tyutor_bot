from aiogram import Bot
from aiogram.types import ChatMember

async def chek_membership(bot: Bot, channel_link: str, user_id: int):
    """
    Docstring for chek_membership
    
    :param bot: Description
    :type bot: Bot
    :param channel_link: Description
    :type channel_link: str
    :param user_id: Description
    :type user_id: int
    """
    try: 
        # username olish
        if channel_link.startswith("https://t.me/"):
            username = channel_link.split("https://t.me/")[-1].strip()
        else:
            username = channel_link.strip()

        # Telegram API orqali a'zo ekanligini tekshirish
        member: ChatMember = await bot.get_chat_member(chat_id=f"@{username}", user_id=user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except Exception as e:
        # Public kanalda bot kanalda bo'lmasa yoki private kanal bo'lsa, xatolik qaytadi
        print(f"Error checking membership for {channel_link}: {e}")
        return False