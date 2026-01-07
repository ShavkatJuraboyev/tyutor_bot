from aiogram.filters import Command
from aiogram import Router, F, Bot, Dispatcher
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from utils.membership import chek_membership
from database import db

router = Router()
class MurojaatStates(StatesGroup):
    waiting_full_name = State()
    waiting_contact = State()
    waiting_subject = State()

# ==========================
# /start
# ==========================
@router.message(Command("start"))
async def start(msg: Message, bot: Bot):
    user_id = msg.from_user.id
    user_name = msg.from_user.full_name
    username = msg.from_user.username if msg.from_user.username else "NoUsername"
    await db.add_user(user_id=user_id, username=username, full_name=user_name)
    await msg.answer(
        f"👋 Assalomu alaykum, <a href='tg://user?id={user_id}'><b>{user_name}</b></a>!",
        parse_mode="HTML"
    )
    start_page = await db.get_start_page()
    if start_page:
        photo_id, caption = start_page[1], start_page[2]
        if photo_id:
            await msg.answer_photo(photo_id, caption=caption)
        else:
            await tyutor_section(msg)
    else:
        await tyutor_section(msg)

    # Kanal tekshirish
    channels = await db.get_all_channels()
    if channels:
        all_membership = []
        for ch in channels:
            ch_id, name, link = ch
            is_member = await chek_membership(bot, link, user_id)
            all_membership.append(is_member)

        if all(all_membership):
            await tyutor_section(msg)
        else:
            buttons = [[InlineKeyboardButton(text=ch[1], url=ch[2])] for ch in channels]
            buttons.append([InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_membership")])
            await msg.answer(
                "Murojaat qilishdan oldin quyidagi kanallarga a’zo bo‘ling va tekshirish tugmasini bosing 👇",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
            )

# ==========================
# Tekshirish tugmasi
# ==========================
@router.callback_query(F.data == "check_membership")
async def check_cb(cb: CallbackQuery, bot: Bot):
    user_id = cb.from_user.id
    channels = await db.get_all_channels()
    if not channels:
        await cb.message.answer("⚠️ Kanallar mavjud emas.")
        await tyutor_section(cb.message)
        return

    all_membership = []
    for ch in channels:
        ch_id, name, link = ch
        is_member = await chek_membership(bot, link, user_id)
        all_membership.append(is_member)
    if all(all_membership):
        await cb.message.answer("✅ Siz barcha kanallarga a'zo bo'lgansiz!")
        await tyutor_section(cb.message)
    else:
        buttons = [[InlineKeyboardButton(text=ch[1], url=ch[2])] for ch in channels]
        buttons.append([InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_membership")])
        await cb.message.answer("⚠️ Siz hali ham barcha kanallarga a'zo emassiz.", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

# ==========================
# Tyutorlar bo'limi
# ==========================
async def tyutor_section(msg: Message):
    tutors = await db.get_all_tutors()

    if tutors:
        kb_buttons = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=tutor[2], callback_data=f"tutor_{tutor[0]}")] for tutor in tutors
            ]
        )
        await msg.answer("Murojaat qilish uchun tyutorlardan birini tanlang:", reply_markup=kb_buttons)
    else:
        await msg.answer("Hozircha tyutorlar mavjud emas.")

@router.callback_query(F.data == "tutors")
async def tyutors(cb: CallbackQuery):
    tutors = await db.get_all_tutors()

    if tutors:
        kb_buttons = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=tutor[2], callback_data=f"tutor_{tutor[0]}")] for tutor in tutors
            ]
        )
        await cb.message.answer("Murojaat qilish uchun tyutorlardan birini tanlang:", reply_markup=kb_buttons)
    else:
        await cb.message.answer("Hozircha tyutorlar mavjud emas.")
    await cb.message.delete()

@router.callback_query(F.data.startswith("tutor_"))
async def tutor_detail_cb(cb: CallbackQuery, state: FSMContext):
    tutor_id = int(cb.data.split("_")[1])
    tutor = await db.get_tutor_one(tutor_id)
    if tutor:
        id, user_id, name, subject, contact_info = tutor
        await state.update_data(user_id=user_id)
        button = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="📝 Murojaat qilish", callback_data="murojaat")],
                [InlineKeyboardButton(text="🔙 Orqaga", callback_data="tutors")]
            ]
        )
        await cb.message.answer(
            f"👤 <b>Tyutor:</b> {name}\n"
            f"📚 <b>Ma'lumoti:</b> {subject}\n"
            f"📞 <b>Aloqa:</b> {contact_info}",
            parse_mode="HTML",
            reply_markup=button
        )
    else:
        await cb.message.answer("Tyutor topilmadi.")

    await cb.message.delete()


@router.callback_query(F.data == "murojaat")
async def murojaat_cb(cb: CallbackQuery, state: FSMContext):
    await cb.message.answer("To'liq ismingizni kiriting:")
    await state.set_state(MurojaatStates.waiting_full_name)
    await cb.message.delete()

@router.message(MurojaatStates.waiting_full_name)
async def process_full_name(msg: Message, state: FSMContext):
    await state.update_data(full_name=msg.text)
    await msg.answer("Aloqa ma'lumotlaringizni kiriting (telefon raqam yoki email):")
    await state.set_state(MurojaatStates.waiting_contact)

@router.message(MurojaatStates.waiting_contact)
async def process_contact(msg: Message, state: FSMContext):
    await state.update_data(contact=msg.text)
    await msg.answer("Murojaat mazmunini kiriting:")
    await state.set_state(MurojaatStates.waiting_subject)

@router.message(MurojaatStates.waiting_subject)
async def process_subject(msg: Message, state: FSMContext):
    user_data = await state.get_data()
    full_name = user_data.get("full_name")
    user_id = user_data.get("user_id")
    contact = user_data.get("contact")
    subject = msg.text
    text = f"""Yangi murojaat:
    👤 Ism: {full_name}
    📞 Aloqa: {contact}
    📝 Murojaat mazmuni:
    {subject}
    """

    # Murojaatni saqlash
    await msg.bot.send_message(chat_id=user_id, text=text, parse_mode="HTML")
    button = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Orqaga", callback_data="tutors")]
            ]
        )
    await msg.answer("✅ Murojaatingiz qabul qilindi! Tez orada siz bilan bog'lanamiz.", reply_markup=button)
    await state.clear()

def register_user_handlers(dp: Dispatcher, bot: Bot):
    dp.include_router(router)