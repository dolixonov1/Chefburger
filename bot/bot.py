"""
Chef Burger Telegram Bot — To'liq O'zbek tilidagi versiya
Admin: 7492618052
"""

import logging
from datetime import datetime
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ConversationHandler, ContextTypes, filters
)
from telegram.constants import ParseMode
import config
from menu import MENU, CATEGORIES
from cart import Cart
from orders import OrderManager

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

(
    CHOOSING_ACTION, BROWSING_MENU, VIEWING_ITEM, CART_VIEW,
    CHECKOUT_NAME, CHECKOUT_PHONE, CHECKOUT_TYPE, CHECKOUT_ADDRESS, CHECKOUT_TIME,
    RESERVATION_DATE, RESERVATION_TIME, RESERVATION_GUESTS, RESERVATION_NAME, RESERVATION_PHONE,
) = range(14)

order_manager = OrderManager()

HOLAT_EMOJI = {"pending":"⏳","confirmed":"✅","preparing":"👨‍🍳","delivered":"🎉","cancelled":"❌"}
HOLAT_UZ    = {"pending":"Kutilmoqda","confirmed":"Tasdiqlandi","preparing":"Tayyorlanmoqda","delivered":"Yetkazildi","cancelled":"Bekor qilindi"}


def get_cart(context) -> Cart:
    if "cart" not in context.user_data:
        context.user_data["cart"] = Cart()
    return context.user_data["cart"]


def asosiy_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🍔 Menyu",            callback_data="menu"),
         InlineKeyboardButton("🛒 Savatcha",         callback_data="cart")],
        [InlineKeyboardButton("📋 Buyurtmalarim",    callback_data="my_orders"),
         InlineKeyboardButton("🪑 Stol bron qilish", callback_data="reserve")],
        [InlineKeyboardButton("🔥 Chegirmalar",      callback_data="deals"),
         InlineKeyboardButton("📍 Manzil",           callback_data="location")],
        [InlineKeyboardButton("ℹ️ Biz haqimizda",    callback_data="about"),
         InlineKeyboardButton("📞 Bog'lanish",       callback_data="contact")],
    ])


def orqaga_bosh():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Bosh sahifa", callback_data="main_menu")]])


def kategoriyalar_kb():
    buttons, row = [], []
    for key, label in CATEGORIES.items():
        row.append(InlineKeyboardButton(label, callback_data=f"cat_{key}"))
        if len(row) == 2:
            buttons.append(row); row = []
    if row: buttons.append(row)
    buttons.append([InlineKeyboardButton("⬅️ Orqaga", callback_data="main_menu")])
    return InlineKeyboardMarkup(buttons)


def mahsulotlar_kb(category):
    items   = [i for i in MENU if i["category"] == category]
    buttons = [[InlineKeyboardButton(f"{i['name']} — {i['price']:,} so'm", callback_data=f"item_{i['id']}")] for i in items]
    buttons.append([
        InlineKeyboardButton("⬅️ Kategoriyalar", callback_data="menu"),
        InlineKeyboardButton("🛒 Savatcha",       callback_data="cart"),
    ])
    return InlineKeyboardMarkup(buttons)


def mahsulot_kb(item_id, category):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Savatchaga qo'shish", callback_data=f"add_{item_id}")],
        [InlineKeyboardButton("⬅️ Orqaga", callback_data=f"cat_{category}"),
         InlineKeyboardButton("🛒 Savatcha", callback_data="cart")],
    ])


def savatcha_kb(cart: Cart):
    buttons = []
    if not cart.is_empty():
        buttons += [
            [InlineKeyboardButton("✅ Buyurtma berish",    callback_data="checkout")],
            [InlineKeyboardButton("🗑 Savatchani tozalash", callback_data="clear_cart")],
        ]
    buttons.append([
        InlineKeyboardButton("🍔 Davom etish", callback_data="menu"),
        InlineKeyboardButton("🏠 Bosh sahifa", callback_data="main_menu"),
    ])
    return InlineKeyboardMarkup(buttons)


def yetkazish_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 Yetkazib berish",    callback_data="type_delivery")],
        [InlineKeyboardButton("🥡 Olib ketish",        callback_data="type_takeaway")],
        [InlineKeyboardButton("🪑 Restoranda yeyish",  callback_data="type_dinein")],
        [InlineKeyboardButton("❌ Bekor qilish",       callback_data="main_menu")],
    ])


# ── BUYRUQLAR ─────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    user = update.effective_user
    await update.message.reply_text(
        f"👋 *Xush kelibsiz, {user.first_name}!*\n\n"
        "🍔 *Chef Burger*ga xush kelibsiz!\n"
        "🥩 Yangi mahsulotlar. Haqiqiy oshpazlar. Hech qanday murosasizlik.\n\n"
        "📍 Toshkent · Har kuni 11:00 – 23:00\n\n"
        "Bugun nima buyurtma qilasiz? 👇",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=asosiy_menu()
    )
    return CHOOSING_ACTION


async def yordam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "*Chef Burger Bot — Yordam*\n\n"
        "*/start* — Bosh sahifa\n"
        "*/menu* — Menyuni ko'rish\n"
        "*/cart* — Savatcham\n"
        "*/orders* — Buyurtmalarim\n"
        "*/reserve* — Stol bron qilish\n"
        "*/deals* — Chegirmalar\n"
        "*/location* — Manzil\n"
        "*/cancel* — Amalni bekor qilish\n\n"
        "Yordam: @ChefBurgerSupport",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=orqaga_bosh()
    )
    return CHOOSING_ACTION


async def bekor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Bekor qilindi.", reply_markup=asosiy_menu())
    return CHOOSING_ACTION


# ── CALLBACK ROUTER ───────────────────────────

async def cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q    = update.callback_query
    await q.answer()
    data = q.data

    # ── navigation ──
    if data == "main_menu":
        await q.edit_message_text("🏠 *Bosh sahifa*", parse_mode=ParseMode.MARKDOWN, reply_markup=asosiy_menu())
        return CHOOSING_ACTION

    if data == "menu":
        await q.edit_message_text("🍔 *Bizning Menyu*\n\nKategoriyani tanlang:", parse_mode=ParseMode.MARKDOWN, reply_markup=kategoriyalar_kb())
        return BROWSING_MENU

    if data.startswith("cat_"):
        cat   = data[4:]
        label = CATEGORIES.get(cat, cat)
        await q.edit_message_text(f"*{label}*\n\nMahsulotni tanlang:", parse_mode=ParseMode.MARKDOWN, reply_markup=mahsulotlar_kb(cat))
        return BROWSING_MENU

    if data.startswith("item_"):
        item = next((i for i in MENU if i["id"] == int(data[5:])), None)
        if not item:
            await q.edit_message_text("Topilmadi.", reply_markup=orqaga_bosh()); return CHOOSING_ACTION
        belgi = " · ".join(item.get("badges", []))
        matn  = (
            f"{'🏷 ' + belgi + chr(10) + chr(10) if belgi else ''}"
            f"*{item['name']}*\n_{item['description']}_\n\n"
            f"💰 *{item['price']:,} so'm*\n"
            f"⏱ ~{item.get('prep_time',10)} daqiqa"
        )
        if item.get("calories"): matn += f"\n🔥 {item['calories']} kkal"
        if item.get("allergens"): matn += f"\n⚠️ {', '.join(item['allergens'])}"
        await q.edit_message_text(matn, parse_mode=ParseMode.MARKDOWN, reply_markup=mahsulot_kb(item["id"], item["category"]))
        return VIEWING_ITEM

    if data.startswith("add_"):
        item = next((i for i in MENU if i["id"] == int(data[4:])), None)
        if item:
            cart = get_cart(context)
            cart.add(item)
            await q.edit_message_text(
                f"✅ *{item['name']}* savatchaga qo'shildi!\n\n"
                f"🛒 Jami: *{cart.total():,} so'm* ({cart.count()} ta)",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🍔 Yana qo'shish",      callback_data=f"cat_{item['category']}")],
                    [InlineKeyboardButton("🛒 Savatchani ko'rish",  callback_data="cart")],
                    [InlineKeyboardButton("✅ Buyurtma berish",     callback_data="checkout")],
                ])
            )
        return BROWSING_MENU

    if data == "cart":               return await show_cart(update, context)
    if data == "deals":              await show_deals(update, context);    return CHOOSING_ACTION
    if data == "location":           await show_location(update, context); return CHOOSING_ACTION
    if data == "about":              await show_about(update, context);    return CHOOSING_ACTION
    if data == "contact":            await show_contact(update, context);  return CHOOSING_ACTION
    if data == "my_orders":          return await show_orders(update, context)
    if data.startswith("reorder_"):  return await reorder(update, context, data[8:])
    if data.startswith("res_g_"):    return await bron_mehmon_cb(update, context)

    if data == "clear_cart":
        get_cart(context).clear()
        await q.edit_message_text(
            "🗑 Savatcha tozalandi!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🍔 Menyuga o'tish", callback_data="menu")],
                [InlineKeyboardButton("🏠 Bosh sahifa",    callback_data="main_menu")],
            ])
        )
        return CHOOSING_ACTION

    if data == "checkout":
        cart = get_cart(context)
        if cart.is_empty():
            await q.edit_message_text("🛒 Savatcha bo'sh!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🍔 Menyu", callback_data="menu")]]))
            return BROWSING_MENU
        await q.edit_message_text("📦 *Buyurtma berish*\n\nQanday usulda?", parse_mode=ParseMode.MARKDOWN, reply_markup=yetkazish_kb())
        return CHECKOUT_TYPE

    if data.startswith("type_"):
        tur = data[5:]
        labels = {"delivery":"🏠 Yetkazib berish","takeaway":"🥡 Olib ketish","dinein":"🪑 Restoranda yeyish"}
        context.user_data["order_type"]       = tur
        context.user_data["order_type_label"] = labels[tur]
        await q.edit_message_text(f"*{labels[tur]}* tanlandi!\n\n*To'liq ismingizni* kiriting:", parse_mode=ParseMode.MARKDOWN)
        return CHECKOUT_NAME

    if data == "reserve":
        await q.edit_message_text("🪑 *Stol bron qilish*\n\nQaysi *sanaga*?\nMisol: *25 mart*", parse_mode=ParseMode.MARKDOWN)
        return RESERVATION_DATE

    return CHOOSING_ACTION


# ── SAVATCHA ──────────────────────────────────

async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q    = update.callback_query
    cart = get_cart(context)
    if cart.is_empty():
        matn = "🛒 *Savatcha bo'sh*\n\nBurger qo'shing!"
    else:
        qat = ["🛒 *Savatcham*\n"]
        for e in cart.items.values():
            qat.append(f"• *{e['name']}* x{e['qty']} — {e['price']*e['qty']:,} so'm")
        if cart.delivery_fee() > 0:
            qat.append(f"\n🚚 Yetkazish: {cart.delivery_fee():,} so'm")
        qat.append(f"\n💰 *Jami: {cart.total():,} so'm*")
        matn = "\n".join(qat)
    fn = q.edit_message_text if q else update.message.reply_text
    await fn(matn, parse_mode=ParseMode.MARKDOWN, reply_markup=savatcha_kb(cart))
    return CART_VIEW


async def show_deals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    matn = (
        "🔥 *Bu haftaning chegirmalari*\n\n"
        "1️⃣ *2 ta burger → Kartoshka bepul*\n"
        "   Istalgan 2 ta burger — katta kartoshka sovg'a!\n\n"
        "2️⃣ *Combo to'plam — 20% chegirma*\n"
        "   Burger + ichimlik + garnir = 20% arzon.\n\n"
        "3️⃣ *Talabalar — 15% off*\n"
        "   Talaba guvohnomangizni ko'rsating. Har kuni.\n\n"
        "4️⃣ *Telegram orqali — Bepul sous*\n"
        "   Shu bot orqali buyurtma → imzoli sous sovg'a!\n\n"
        "⏰ Chegirmalar faqat shu hafta."
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🍔 Hozir buyurtma bering", callback_data="menu")],
        [InlineKeyboardButton("🏠 Bosh sahifa",            callback_data="main_menu")],
    ])
    fn = update.callback_query.edit_message_text if update.callback_query else update.message.reply_text
    await fn(matn, parse_mode=ParseMode.MARKDOWN, reply_markup=kb)


async def show_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    matn = (
        "📍 *Chef Burger manzili*\n\n"
        "🏠 Amir Temur ko'chasi 123, Yunusobod, Toshkent\n\n"
        "🕐 *Ish vaqti:*\n"
        "Du – Ju: 11:00 – 23:00\n"
        "Sha – Ya: 10:00 – 00:00\n\n"
        "📞 +998 71 234 5678\n"
        "🚇 Yunusobod metrosidan 5 daqiqa\n"
        "🚗 Bepul avtoturargoh\n"
        "🛵 Yetkazish hududi: 10 km"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🗺 Xaritada ochish",   url="https://maps.google.com/?q=Tashkent+Yunusabad")],
        [InlineKeyboardButton("📞 Qo'ng'iroq qilish", url="tel:+998712345678")],
        [InlineKeyboardButton("🏠 Bosh sahifa",       callback_data="main_menu")],
    ])
    fn = update.callback_query.edit_message_text if update.callback_query else update.message.reply_text
    await fn(matn, parse_mode=ParseMode.MARKDOWN, reply_markup=kb)


async def show_about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    matn = (
        "👨‍🍳 *Chef Burger haqida*\n\n"
        "2019-yildan beri Toshkentga eng mazali burgerni taqdim etib kelmoqdamiz.\n\n"
        "🥩 *100% yangi go'sht* — mahalliy ta'minot, har kuni yangi\n"
        "🍞 *Yangi non* — har ertalab yetkaziladi\n"
        "🥬 *Mahalliy sabzavotlar* — viloyat fermerlaridan\n"
        "👨‍🍳 *Ochiq oshxona* — ko'rishingiz mumkin\n\n"
        "⭐ 4.8 reyting · 2,000+ mamnun mijoz"
    )
    fn = update.callback_query.edit_message_text if update.callback_query else update.message.reply_text
    await fn(matn, parse_mode=ParseMode.MARKDOWN, reply_markup=orqaga_bosh())


async def show_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    matn = (
        "📞 *Bog'lanish*\n\n"
        "📱 +998 71 234 5678\n"
        "💬 Telegram: @ChefBurgerSupport\n"
        "📸 Instagram: @ChefBurgerUZ\n"
        "🎵 TikTok: @ChefBurgerUZ\n\n"
        "Korporativ buyurtma va tadbirlar uchun yozing."
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 Support", url="https://t.me/ChefBurgerSupport")],
        [InlineKeyboardButton("📸 Instagram", url="https://instagram.com/ChefBurgerUZ")],
        [InlineKeyboardButton("🏠 Bosh sahifa", callback_data="main_menu")],
    ])
    fn = update.callback_query.edit_message_text if update.callback_query else update.message.reply_text
    await fn(matn, parse_mode=ParseMode.MARKDOWN, reply_markup=kb)


async def show_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q      = update.callback_query
    orders = order_manager.get_user_orders(update.effective_user.id)
    if not orders:
        await q.edit_message_text(
            "📋 Hali buyurtma yo'q!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🍔 Menyuga o'tish", callback_data="menu")],
                [InlineKeyboardButton("🏠 Bosh sahifa",    callback_data="main_menu")],
            ])
        )
    else:
        qat  = ["📋 *So'nggi buyurtmalarim*\n"]
        btns = []
        for o in orders[-5:]:
            emoji = HOLAT_EMOJI.get(o["status"], "📦")
            holat = HOLAT_UZ.get(o["status"], o["status"])
            qat.append(f"{emoji} *#{o['id']}* — {o['total']:,} so'm\n   {o['date']} · {holat}\n")
            btns.append([InlineKeyboardButton(f"🔁 Qayta buyurtma #{o['id']}", callback_data=f"reorder_{o['id']}")])
        btns.append([InlineKeyboardButton("🏠 Bosh sahifa", callback_data="main_menu")])
        await q.edit_message_text("\n".join(qat), parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(btns))
    return CHOOSING_ACTION


async def reorder(update: Update, context: ContextTypes.DEFAULT_TYPE, order_id: str):
    q     = update.callback_query
    order = order_manager.get_order(order_id)
    if not order or order.get("user_id") != update.effective_user.id:
        await q.edit_message_text("Topilmadi.", reply_markup=orqaga_bosh()); return CHOOSING_ACTION
    cart = get_cart(context)
    cart.clear()
    for item in order["items"]: cart.add(item)
    await q.edit_message_text(
        f"🔁 *#{order_id} yuklandi!*\n\n🛒 {cart.count()} ta · *{cart.total():,} so'm*",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Buyurtma berish",     callback_data="checkout")],
            [InlineKeyboardButton("✏️ Savatchani ko'rish",  callback_data="cart")],
            [InlineKeyboardButton("🏠 Bosh sahifa",         callback_data="main_menu")],
        ])
    )
    return CART_VIEW


# ── CHECKOUT FLOW ─────────────────────────────

async def checkout_ism(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ism = update.message.text.strip()
    if len(ism) < 2:
        await update.message.reply_text("Iltimos, to'liq ismingizni kiriting:")
        return CHECKOUT_NAME
    context.user_data["checkout_name"] = ism
    await update.message.reply_text(
        f"👍 *{ism}*!\n\n*Telefon raqamingizni* kiriting:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("📱 Raqamimni ulashish", request_contact=True)]], one_time_keyboard=True, resize_keyboard=True)
    )
    return CHECKOUT_PHONE


async def checkout_telefon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telefon = update.message.contact.phone_number if update.message.contact else update.message.text.strip()
    context.user_data["checkout_phone"] = telefon
    if context.user_data.get("order_type") == "delivery":
        await update.message.reply_text("📍 *Yetkazish manzilingizni* kiriting:", parse_mode=ParseMode.MARKDOWN, reply_markup=ReplyKeyboardRemove())
        return CHECKOUT_ADDRESS
    await update.message.reply_text("⏰ Qachon tayyor bo'lsin?\n*Tezroq* yoki vaqt kiriting (masalan: *14:30*):", parse_mode=ParseMode.MARKDOWN, reply_markup=ReplyKeyboardRemove())
    return CHECKOUT_TIME


async def checkout_manzil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["checkout_address"] = update.message.text.strip()
    await update.message.reply_text("⏰ Qachon yetkazib beraylik?\n*Tezroq* yoki vaqt kiriting:", parse_mode=ParseMode.MARKDOWN)
    return CHECKOUT_TIME


async def checkout_vaqt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["checkout_time"] = update.message.text.strip()
    return await buyurtmani_joylash(update, context)


async def buyurtmani_joylash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cart  = get_cart(context)
    user  = update.effective_user
    ud    = context.user_data
    order = order_manager.create_order(
        user_id          = user.id,
        user_name        = ud.get("checkout_name", user.first_name),
        phone            = ud.get("checkout_phone", "N/A"),
        order_type       = ud.get("order_type", "delivery"),
        order_type_label = ud.get("order_type_label", "Yetkazib berish"),
        address          = ud.get("checkout_address", "N/A"),
        time             = ud.get("checkout_time", "Tezroq"),
        cart             = cart,
    )
    mahsulotlar = "\n".join([f"  • {e['name']} x{e['qty']} — {e['price']*e['qty']:,} so'm" for e in cart.items.values()])
    await update.message.reply_text(
        f"✅ *Buyurtma qabul qilindi! #{order['id']}*\n\n"
        f"👤 {order['name']}\n📞 {order['phone']}\n📦 {order['order_type_label']}\n"
        f"{('📍 ' + order['address'] + chr(10)) if order['address'] != 'N/A' else ''}"
        f"⏰ {order['time']}\n\n*Buyurtmangiz:*\n{mahsulotlar}\n\n"
        f"💰 *Jami: {order['total']:,} so'm*\n\n"
        f"⏱ Taxminiy vaqt: *{order.get('eta','30')} daqiqa*\n\nRahmat! 🙏",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 Buyurtmalarim", callback_data="my_orders")],
            [InlineKeyboardButton("🍔 Yana buyurtma", callback_data="menu")],
            [InlineKeyboardButton("🏠 Bosh sahifa",   callback_data="main_menu")],
        ])
    )
    await admin_xabar(context, order, mahsulotlar)
    cart.clear()
    return CHOOSING_ACTION


async def admin_xabar(context, order, mahsulotlar):
    if not config.ADMIN_CHAT_ID: return
    try:
        await context.bot.send_message(
            config.ADMIN_CHAT_ID,
            f"🔔 *YANGI BUYURTMA #{order['id']}*\n\n"
            f"👤 {order['name']}\n📞 {order['phone']}\n📦 {order['order_type_label']}\n"
            f"{('📍 ' + order['address'] + chr(10)) if order['address'] != 'N/A' else ''}"
            f"⏰ {order['time']}\n\n*Mahsulotlar:*\n{mahsulotlar}\n\n"
            f"💰 *Jami: {order['total']:,} so'm*\n🕐 {order['date']}",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Tasdiqlash",    callback_data=f"admin_confirm_{order['id']}"),
                 InlineKeyboardButton("❌ Bekor qilish", callback_data=f"admin_cancel_{order['id']}")],
                [InlineKeyboardButton("👨‍🍳 Tayyorlanmoqda", callback_data=f"admin_prep_{order['id']}")],
                [InlineKeyboardButton("🎉 Yetkazildi",   callback_data=f"admin_done_{order['id']}")],
            ])
        )
    except Exception as e:
        logger.warning(f"Admin xabar: {e}")


# ── BRON FLOW ─────────────────────────────────

async def bron_sana(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["res_date"] = update.message.text.strip()
    await update.message.reply_text(f"📅 *{context.user_data['res_date']}* — qabul!\n\nQaysi *vaqtda*? (masalan: 19:00):", parse_mode=ParseMode.MARKDOWN)
    return RESERVATION_TIME


async def bron_vaqt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["res_time"] = update.message.text.strip()
    await update.message.reply_text(
        "👥 Necha *mehmon*?", parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(str(n), callback_data=f"res_g_{n}") for n in range(1, 5)],
            [InlineKeyboardButton(str(n), callback_data=f"res_g_{n}") for n in range(5, 8)],
            [InlineKeyboardButton("8+", callback_data="res_g_8")],
        ])
    )
    return RESERVATION_GUESTS


async def bron_mehmon_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q      = update.callback_query
    await q.answer()
    mehmon = q.data.replace("res_g_", "")
    context.user_data["res_guests"] = mehmon
    await q.edit_message_text(f"👥 *{mehmon} ta mehmon*!\n\nBron uchun *to'liq ismingizni* kiriting:", parse_mode=ParseMode.MARKDOWN)
    return RESERVATION_NAME


async def bron_ism(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["res_name"] = update.message.text.strip()
    await update.message.reply_text(
        "📞 *Telefon raqamingiz*:", parse_mode=ParseMode.MARKDOWN,
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("📱 Raqamimni ulashish", request_contact=True)]], one_time_keyboard=True, resize_keyboard=True)
    )
    return RESERVATION_PHONE


async def bron_telefon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telefon = update.message.contact.phone_number if update.message.contact else update.message.text.strip()
    ud      = context.user_data
    res_id  = order_manager.create_reservation(
        user_id = update.effective_user.id,
        name    = ud["res_name"], phone = telefon,
        date    = ud["res_date"], time  = ud["res_time"], guests = ud["res_guests"],
    )
    await update.message.reply_text(
        f"🪑 *Stol bron qilindi! #{res_id}*\n\n"
        f"👤 {ud['res_name']}\n📅 {ud['res_date']} soat {ud['res_time']}\n"
        f"👥 {ud['res_guests']} ta mehmon\n📞 {telefon}\n\n"
        "1 soat oldin eslatma yuboramiz. Ko'rishguncha! 🍔",
        parse_mode=ParseMode.MARKDOWN, reply_markup=ReplyKeyboardRemove()
    )
    await update.message.reply_text("Yana nima qilmoqchisiz?", reply_markup=asosiy_menu())
    if config.ADMIN_CHAT_ID:
        try:
            await context.bot.send_message(
                config.ADMIN_CHAT_ID,
                f"🪑 *YANGI BRON #{res_id}*\n\n👤 {ud['res_name']} · {telefon}\n📅 {ud['res_date']} soat {ud['res_time']}\n👥 {ud['res_guests']} ta mehmon",
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            logger.warning(f"Admin bron xabar: {e}")
    return CHOOSING_ACTION


# ── ADMIN CALLBACK ────────────────────────────

async def admin_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if update.effective_user.id != config.ADMIN_CHAT_ID:
        await q.answer("Ruxsat yo'q.", show_alert=True); return
    parts    = q.data.split("_")
    action   = parts[1]
    order_id = parts[2]
    holat_map = {
        "confirm": ("confirmed", "✅ Tasdiqlandi!"),
        "cancel":  ("cancelled", "❌ Bekor qilindi."),
        "prep":    ("preparing", "👨‍🍳 Tayyorlanmoqda!"),
        "done":    ("delivered", "🎉 Yetkazildi!"),
    }
    if action in holat_map:
        yangi_holat, eslatma = holat_map[action]
        order = order_manager.update_status(order_id, yangi_holat)
        if order:
            mijoz_xabar = {
                "confirmed": "✅ Buyurtmangiz tasdiqlandi!",
                "cancelled": "❌ Buyurtmangiz bekor qilindi.",
                "preparing": "👨‍🍳 Buyurtmangiz tayyorlanmoqda!",
                "delivered": "🎉 Buyurtmangiz tayyor / yo'lda! Yoqimli ishtaha!",
            }
            try:
                await context.bot.send_message(
                    order["user_id"],
                    f"{mijoz_xabar.get(yangi_holat,'')}\n\nBuyurtma *#{order_id}* — {order['total']:,} so'm",
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception as e:
                logger.warning(f"Mijozga xabar: {e}")
            await q.edit_message_text(
                q.message.text + f"\n\n{eslatma} [{datetime.now().strftime('%H:%M')}]",
                parse_mode=ParseMode.MARKDOWN
            )


# ── COMMAND SHORTCUTS ─────────────────────────

async def menu_cmd(u, c):
    await u.message.reply_text("🍔 *Bizning Menyu*\n\nKategoriyani tanlang:", parse_mode=ParseMode.MARKDOWN, reply_markup=kategoriyalar_kb())
    return BROWSING_MENU

async def cart_cmd(u, c):   return await show_cart(u, c)

async def orders_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    orders = order_manager.get_user_orders(update.effective_user.id)
    if not orders:
        await update.message.reply_text("📋 Hali buyurtma yo'q!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🍔 Menyu", callback_data="menu")]]))
    else:
        qat = ["📋 *So'nggi buyurtmalarim*\n"]
        for o in orders[-5:]:
            qat.append(f"{HOLAT_EMOJI.get(o['status'],'📦')} *#{o['id']}* — {o['total']:,} so'm · {HOLAT_UZ.get(o['status'],o['status'])}")
        await update.message.reply_text("\n".join(qat), parse_mode=ParseMode.MARKDOWN, reply_markup=orqaga_bosh())
    return CHOOSING_ACTION

async def reserve_cmd(u, c):
    await u.message.reply_text("🪑 *Stol bron qilish*\n\nQaysi *sanaga*?\nMisol: *25 mart*", parse_mode=ParseMode.MARKDOWN)
    return RESERVATION_DATE

async def deals_cmd(u, c):    await show_deals(u, c);    return CHOOSING_ACTION
async def location_cmd(u, c): await show_location(u, c); return CHOOSING_ACTION


# ── MAIN ──────────────────────────────────────

def main():
    app = Application.builder().token(config.BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[
            CommandHandler("start",    start),
            CommandHandler("menu",     menu_cmd),
            CommandHandler("cart",     cart_cmd),
            CommandHandler("orders",   orders_cmd),
            CommandHandler("reserve",  reserve_cmd),
            CommandHandler("deals",    deals_cmd),
            CommandHandler("location", location_cmd),
        ],
        states={
            CHOOSING_ACTION:    [CallbackQueryHandler(cb)],
            BROWSING_MENU:      [CallbackQueryHandler(cb)],
            VIEWING_ITEM:       [CallbackQueryHandler(cb)],
            CART_VIEW:          [CallbackQueryHandler(cb)],
            CHECKOUT_TYPE:      [CallbackQueryHandler(cb)],
            CHECKOUT_NAME:      [MessageHandler(filters.TEXT & ~filters.COMMAND, checkout_ism)],
            CHECKOUT_PHONE:     [MessageHandler(filters.CONTACT | (filters.TEXT & ~filters.COMMAND), checkout_telefon)],
            CHECKOUT_ADDRESS:   [MessageHandler(filters.TEXT & ~filters.COMMAND, checkout_manzil)],
            CHECKOUT_TIME:      [MessageHandler(filters.TEXT & ~filters.COMMAND, checkout_vaqt)],
            RESERVATION_DATE:   [MessageHandler(filters.TEXT & ~filters.COMMAND, bron_sana), CallbackQueryHandler(cb)],
            RESERVATION_TIME:   [MessageHandler(filters.TEXT & ~filters.COMMAND, bron_vaqt)],
            RESERVATION_GUESTS: [CallbackQueryHandler(bron_mehmon_cb, pattern=r"^res_g_")],
            RESERVATION_NAME:   [MessageHandler(filters.TEXT & ~filters.COMMAND, bron_ism)],
            RESERVATION_PHONE:  [MessageHandler(filters.CONTACT | (filters.TEXT & ~filters.COMMAND), bron_telefon)],
        },
        fallbacks=[
            CommandHandler("cancel", bekor),
            CommandHandler("help",   yordam),
            CommandHandler("start",  start),
        ],
        allow_reentry=True,
    )

    app.add_handler(conv)
    app.add_handler(CallbackQueryHandler(admin_cb, pattern=r"^admin_"))
    app.add_handler(CommandHandler("help", yordam))

    print(f"Chef Burger Bot ishga tushdi!")
    print(f"Token: {config.BOT_TOKEN[:20]}...")
    print(f"Admin ID: {config.ADMIN_CHAT_ID}")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
