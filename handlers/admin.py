from aiogram import Bot, F, Router, Dispatcher
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
import database.db as db
from utils.auth import is_admin

router = Router()

class TutorsFSM(StatesGroup):
    user_id = State()
    full_name = State()
    subject = State()
    contact = State()

class StartPageFSM(StatesGroup):
    photo = State()
    caption = State()

class ChannelFSM(StatesGroup):
    title = State()
    link = State()



# ==========================
# /admin
# ==========================
@router.message(Command("admin"))
async def admin_panel(msg: Message):
    user_id = msg.from_user.id
    if not is_admin(user_id):
        await msg.answer("⚠️ Sizda admin huquqlari yo'q.")
        return

    buttons = [
        [InlineKeyboardButton(text="Tutors", callback_data="tutors_menu"),
         InlineKeyboardButton(text="📢 Kanallar", callback_data="channels_all")],
        [InlineKeyboardButton(text="🖼 Start page", callback_data="start_page"),
        InlineKeyboardButton(text="👥 Users", callback_data="list_users")]
    ]
    await msg.answer(
        "Admin paneliga xush kelibsiz! Quyidagi tugmalardan birini tanlang:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )

@router.callback_query(F.data == "back_to_admin")
async def admin_panel_cb(cb: CallbackQuery):
    user_id = cb.from_user.id
    if not is_admin(user_id):
        await cb.message.answer("⚠️ Sizda admin huquqlari yo'q.")
        return

    buttons = [
        [InlineKeyboardButton(text="Tutors", callback_data="tutors_menu"),
         InlineKeyboardButton(text="📢 Kanallar", callback_data="channels_all")],
        [InlineKeyboardButton(text="🖼 Start page", callback_data="start_page"),
        InlineKeyboardButton(text="👥 Users", callback_data="list_users")]
    ]
    await cb.message.answer(
        "Admin paneliga xush kelibsiz! Quyidagi tugmalardan birini tanlang:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )
    await cb.message.delete()

# ==========================
# tutors_menu Operations
# ==========================
@router.callback_query(F.data == "tutors_menu")
async def tutors_menu_cb(cb: CallbackQuery):
    user_id = cb.from_user.id
    if not is_admin(user_id):
        await cb.message.answer("⚠️ Sizda admin huquqlari yo'q.")
        return
    tutors = await db.get_all_tutors()
    if not tutors:
        button = [InlineKeyboardButton(text="➕ Tutor qo'shish", callback_data="add_tutor")]
        await cb.message.answer("Hozircha hech qanday tutor mavjud emas.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[button]))
        return
    
    buttons = []
    for tutor in tutors:
        tutor_id, _, name, subject, contact_info = tutor
        buttons.append([InlineKeyboardButton(text=f"{name}", callback_data=f"tutor:{tutor_id}")])
    buttons.append([InlineKeyboardButton(text="➕ Tutor qo'shish", callback_data="add_tutor")])
    buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_admin")])
    await cb.message.answer("Mavjud tutorlar ro'yxati:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await cb.message.delete()

@router.callback_query(F.data == "add_tutor")
async def add_tutor_cb(cb: CallbackQuery, state: FSMContext):
    user_id = cb.from_user.id
    if not is_admin(user_id):
        await cb.message.answer("⚠️ Sizda admin huquqlari yo'q.")
        return
    await state.set_state(TutorsFSM.full_name)
    await cb.message.answer("Tutor ismini kiriting:")
    await cb.message.delete()

@router.message(TutorsFSM.full_name)
async def tutor_full_name(msg: Message, state: FSMContext):
    await state.update_data(full_name=msg.text)
    await state.set_state(TutorsFSM.user_id)
    await msg.answer("Tutor telegram ID:")
    await msg.delete()

@router.message(TutorsFSM.user_id)
async def tutor_user_id(msg: Message, state: FSMContext):
    await state.update_data(user_id=int(msg.text))
    await state.set_state(TutorsFSM.subject)
    await msg.answer("Tutor malumotini kiriting:")
    await msg.delete()

@router.message(TutorsFSM.subject)
async def tutor_subject(msg: Message, state: FSMContext):
    await state.update_data(subject=msg.text)
    await state.set_state(TutorsFSM.contact)
    await msg.answer("Tutor kontaktini kiriting:")
    await msg.delete()

@router.message(TutorsFSM.contact)
async def tutor_contact(msg: Message, state: FSMContext):
    await state.update_data(contact=msg.text)
    data = await state.get_data()
    user_id = data.get("user_id")
    full_name = data.get("full_name")
    subject = data.get("subject")
    contact = data.get("contact")
    await db.add_tutor(user_id, full_name, subject, contact)
    button = [InlineKeyboardButton(text="🔙 Orqaga", callback_data="tutors_menu")]
    await msg.answer("✅ Tutor muvaffaqiyatli qo'shildi.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[button]))
    await state.clear()
    await msg.delete()

@router.callback_query(F.data.startswith("tutor:"))
async def tutor_detail_cb(cb: CallbackQuery):
    user_id = cb.from_user.id
    if not is_admin(user_id):
        await cb.message.answer("⚠️ Sizda admin huquqlari yo'q.")
        return
    _, tutor_id = cb.data.split(":")
    tutor = await db.get_tutor_one(int(tutor_id))
    if not tutor:
        await cb.message.answer("⚠️ Tutor topilmadi.")
        return
    tutor_id, telegram_id, name, subject, contact_info = tutor
    text = f"👤 Tutor ma'lumotlari:\n\n" \
           f"ID: {tutor_id}\n" \
           f"Telegram ID: {telegram_id}\n" \
           f"Ismi: {name}\n" \
           f"Fan: {subject}\n" \
           f"Kontakt: {contact_info}"
    button = [
        [
            InlineKeyboardButton(text="✍️ Tahrirlash", callback_data=f"edit_tutor:{tutor_id}"),
            InlineKeyboardButton(text="❌ O'chirish", callback_data=f"delete_tutor:{tutor_id}")
        ]
    ]
    button.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="tutors_menu")])
    await cb.message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=button), parse_mode="HTML")
    await cb.message.delete()

@router.callback_query(F.data.startswith("delete_tutor:"))
async def delete_tutor_cb(cb: CallbackQuery):
    user_id = cb.from_user.id
    if not is_admin(user_id):
        await cb.message.answer("⚠️ Sizda admin huquqlari yo'q.")
        return
    _, tutor_id = cb.data.split(":")
    await db.delete_tutor(int(tutor_id))
    button = [InlineKeyboardButton(text="🔙 Orqaga", callback_data="tutors_menu")]
    await cb.message.answer("✅ Tutor muvaffaqiyatli o'chirildi.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[button]))
    await cb.message.delete()

@router.callback_query(F.data.startswith("edit_tutor:"))
async def edit_tutor_cb(cb: CallbackQuery):
    user_id = cb.from_user.id
    if not is_admin(user_id):
        await cb.message.answer("⚠️ Sizda admin huquqlari yo'q.")
        return
    button = [InlineKeyboardButton(text="🔙 Orqaga", callback_data="tutors_menu")]
    await cb.message.answer("⚠️ Tutor tahrirlash funksiyasi hozircha mavjud emas.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[button]))
    await cb.message.delete()


#===========================
# Kanal qo'shish Operations
#===========================
@router.callback_query(F.data == "channels_all")
async def channels_all_cb(cb: CallbackQuery):
    user_id = cb.from_user.id
    if not is_admin(user_id):
        await cb.message.answer("⚠️ Sizda admin huquqlari yo'q.")
        return
    channels = await db.get_all_channels()
    if not channels:
        button = [
            [InlineKeyboardButton(text="➕ Kanal qo'shish", callback_data="add_channel")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_admin")]
        ]
        await cb.message.answer("Hozircha hech qanday kanal mavjud emas.", reply_markup=InlineKeyboardMarkup(inline_keyboard=button))
        await cb.message.delete()
        return
    
    buttons = []
    for channel in channels:
        channel_id, title, invite_link = channel
        buttons.append([InlineKeyboardButton(text=f"{title}", callback_data=f"channel:{channel_id}")])
    buttons.append([InlineKeyboardButton(text="➕ Kanal qo'shish", callback_data="add_channel")])
    buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_admin")])
    await cb.message.answer("Mavjud kanallar ro'yxati:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await cb.message.delete()

@router.callback_query(F.data == "add_channel")
async def add_channel_cb(cb: CallbackQuery, state: FSMContext):
    user_id = cb.from_user.id
    if not is_admin(user_id):
        await cb.message.answer("⚠️ Sizda admin huquqlari yo'q.")
        return
    await state.set_state(ChannelFSM.title)
    await cb.message.answer("Kanal nomini kiriting:")
    await cb.message.delete()

@router.message(ChannelFSM.title)
async def channel_title(msg: Message, state: FSMContext):
    await state.update_data(title=msg.text)
    await state.set_state(ChannelFSM.link)
    await msg.answer("Kanal taklif havolasini kiriting:") 
    await msg.delete()

@router.message(ChannelFSM.link)
async def channel_link(msg: Message, state: FSMContext):
    await state.update_data(link=msg.text)
    data = await state.get_data()
    title = data.get("title")
    link = data.get("link")
    await db.add_channel(title, link)
    button = [InlineKeyboardButton(text="🔙 Orqaga", callback_data="channels_all")]
    await msg.answer("✅ Kanal muvaffaqiyatli qo'shildi.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[button]))
    await state.clear()
    await msg.delete()

@router.callback_query(F.data.startswith("channel:"))
async def channel_detail_cb(cb: CallbackQuery):
    user_id = cb.from_user.id
    if not is_admin(user_id):
        await cb.message.answer("⚠️ Sizda admin huquqlari yo'q.")
        return
    _, channel_id = cb.data.split(":")
    channel = await db.get_channel_one(int(channel_id))
    if not channel:
        await cb.message.answer("⚠️ Kanal topilmadi.")
        return
    channel_id, title, invite_link = channel
    text = f"📢 Kanal ma'lumotlari:\n\n"   
    text += f"Nomi: {title}\n"    
    text += f"Taklif havolasi: {invite_link}"
    button = [
        [InlineKeyboardButton(text="❌ O'chirish", callback_data=f"delete_channel:{channel_id}")]
    ]   
    button.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="channels_all")])
    await cb.message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=button)) 
    await cb.message.delete()

@router.callback_query(F.data.startswith("delete_channel:"))
async def delete_channel_cb(cb: CallbackQuery):
    user_id = cb.from_user.id
    if not is_admin(user_id):
        await cb.message.answer("⚠️ Sizda admin huquqlari yo'q.")
        return
    _, channel_id = cb.data.split(":")
    await db.delete_channel(int(channel_id))
    button = [InlineKeyboardButton(text="🔙 Orqaga", callback_data="channels_all")]
    await cb.message.answer("✅ Kanal muvaffaqiyatli o'chirildi.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[button]))
    await cb.message.delete()


#===========================
# Start Page Operations
#===========================
@router.callback_query(F.data == "start_page")
async def start_page_cb(cb: CallbackQuery):
    user_id = cb.from_user.id
    if not is_admin(user_id):
        await cb.message.answer("⚠️ Sizda admin huquqlari yo'q.")
        return
    start_page = await db.get_start_page()
    if start_page:
        photo_id, caption = start_page[1], start_page[2]
        text = "Hozirgi start page:"
        button = [
            [InlineKeyboardButton(text="✍️ Tahrirlash", callback_data="edit_start_page"),
             InlineKeyboardButton(text="❌ O'chirish", callback_data="delete_start_page")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_admin")]
        ]
        if photo_id:
            await cb.message.answer_photo(photo_id, caption=caption or text, reply_markup=InlineKeyboardMarkup(inline_keyboard=button))
        else:
            await cb.message.answer(caption or text, reply_markup=InlineKeyboardMarkup(inline_keyboard=button))
    else:
        button = [
            [InlineKeyboardButton(text="➕ Start page qo'shish", callback_data="add_start_page")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_admin")]
        ]
        await cb.message.answer("Hozircha start page mavjud emas.", reply_markup=InlineKeyboardMarkup(inline_keyboard=button))

    await cb.message.delete()


@router.callback_query(F.data == "add_start_page")
async def add_start_page_cb(cb: CallbackQuery, state: FSMContext):
    user_id = cb.from_user.id
    if not is_admin(user_id):
        await cb.message.answer("⚠️ Sizda admin huquqlari yo'q.")
        return
    await state.set_state(StartPageFSM.photo)
    await cb.message.answer("Start page uchun rasm yuboring:")
    await cb.message.delete()

@router.message(StartPageFSM.photo)
async def start_page_photo(msg: Message, state: FSMContext):
    photo_id = msg.photo[-1].file_id
    await state.update_data(photo_id=photo_id)
    await state.set_state(StartPageFSM.caption)
    await msg.answer("Start page uchun caption (matn) kiriting:")
    await msg.delete()

@router.message(StartPageFSM.caption)
async def start_page_caption(msg: Message, state: FSMContext):
    await state.update_data(caption=msg.text)
    data = await state.get_data()
    photo_id = data.get("photo_id")
    caption = data.get("caption")
    await db.set_start_page(photo_id, caption)
    button = [InlineKeyboardButton(text="🔙 Orqaga", callback_data="start_page")]
    await msg.answer("✅ Start page muvaffaqiyatli qo'shildi.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[button]))
    await state.clear()
    await msg.delete()

@router.callback_query(F.data == "edit_start_page")
async def edit_start_page_cb(cb: CallbackQuery, state: FSMContext):
    user_id = cb.from_user.id
    if not is_admin(user_id):
        await cb.message.answer("⚠️ Sizda admin huquqlari yo'q.")
        return
    await state.set_state(StartPageFSM.photo)
    await cb.message.answer("Yangi start page uchun rasm yuboring:")
    await cb.message.delete()

@router.message(StartPageFSM.photo)
async def edit_start_page_photo(msg: Message, state: FSMContext):
    photo_id = msg.photo[-1].file_id
    await state.update_data(photo_id=photo_id)
    await state.set_state(StartPageFSM.caption)
    await msg.answer("Yangi start page uchun caption (matn) kiriting:") 
    await msg.delete()

@router.message(StartPageFSM.caption)
async def edit_start_page_caption(msg: Message, state: FSMContext):
    await state.update_data(caption=msg.text)
    data = await state.get_data()
    photo_id = data.get("photo_id")
    caption = data.get("caption")
    await db.update_start_page(photo_id, caption)
    button = [InlineKeyboardButton(text="🔙 Orqaga", callback_data="start_page")]
    await msg.answer("✅ Start page muvaffaqiyatli yangilandi.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[button]))
    await state.clear()
    await msg.delete()

@router.callback_query(F.data == "delete_start_page")
async def delete_start_page_cb(cb: CallbackQuery):
    user_id = cb.from_user.id
    if not is_admin(user_id):
        await cb.message.answer("⚠️ Sizda admin huquqlari yo'q.")
        return
    await db.delete_start_page()
    button = [InlineKeyboardButton(text="🔙 Orqaga", callback_data="start_page")]
    await cb.message.answer("✅ Start page muvaffaqiyatli o'chirildi.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[button]))
    await cb.message.delete()


#===========================
# Foydalanuvchilar ro'yxati
#===========================
@router.callback_query(F.data == "list_users")
async def list_users_cb(cb: CallbackQuery):
    user_id = cb.from_user.id
    if not is_admin(user_id):
        await cb.message.answer("⚠️ Sizda admin huquqlari yo'q.")
        return
    users = await db.get_all_users()
    if not users:
        button = [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_admin")]
        await cb.message.answer("Hozircha hech qanday foydalanuvchi mavjud emas.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[button]))
        return
    
    button = []
    for user in users:
        id, user_id, username, full_name = user
        button.append(InlineKeyboardButton(text=f"{full_name} (@{username})", callback_data=f"user:{user_id}"))
    button = [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_admin")]
    await cb.message.answer("👥 Foydalanuvchilar ro'yxati:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[button]))
    await cb.message.delete()

@router.callback_query(F.data.startswith("user:"))
async def user_detail_cb(cb: CallbackQuery):
    user_id = cb.from_user.id
    if not is_admin(user_id):
        await cb.message.answer("⚠️ Sizda admin huquqlari yo'q.")
        return
    _, target_user_id = cb.data.split(":")
    user = await db.get_user_one(int(target_user_id))
    if not user:
        await cb.message.answer("⚠️ Foydalanuvchi topilmadi.")
        return
    user_id, username, full_name = user
    text = f"👤 Foydalanuvchi ma'lumotlari:\n\n"
    text += f"ID: {user_id}\n"
    text += f"Ism: {full_name}\n"
    text += f"Username: @{username}\n"
    button = [
        [InlineKeyboardButton(text="❌ Foydalanuvchini o'chirish", callback_data=f"delete_user:{user_id}")]
    ]   
    button.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="list_users")])
    await cb.message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=button))
    await cb.message.delete()

@router.callback_query(F.data.startswith("delete_user:"))
async def delete_user_cb(cb: CallbackQuery):
    user_id = cb.from_user.id
    if not is_admin(user_id):
        await cb.message.answer("⚠️ Sizda admin huquqlari yo'q.")
        return
    _, target_user_id = cb.data.split(":")
    await db.delete_user(int(target_user_id))
    button = [InlineKeyboardButton(text="🔙 Orqaga", callback_data="list_users")]
    await cb.message.answer("✅ Foydalanuvchi muvaffaqiyatli o'chirildi.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[button]))
    await cb.message.delete()

# ==========================
# Routerga qo'shish
# ==========================
def register_admin_handlers(dp: Dispatcher, bot: Bot):
    dp.include_router(router)