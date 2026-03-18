# Chef Burger — Telegram Bot (O'zbek tili)

## Sozlash tugallandi
- Token: sozlangan
- Admin ID: 7492618052

## Ishga tushirish

```bash
# 1. Paketlarni o'rnating
pip install -r requirements.txt

# 2. Botni ishga tushiring
python bot.py
```

## Serverda 24/7 ishlatish

### systemd (Linux VPS)
```bash
# /etc/systemd/system/chefburger.service faylini yarating:

[Unit]
Description=Chef Burger Bot
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/ubuntu/chef_burger_bot_uz
ExecStart=/usr/bin/python3 bot.py
Restart=always

[Install]
WantedBy=multi-user.target

# Keyin:
sudo systemctl enable chefburger
sudo systemctl start chefburger
```

### Screen (tezkor usul)
```bash
screen -S chefburger
python bot.py
# Ctrl+A, D — orqaga chiqish
```

## Fayl tuzilmasi
```
chef_burger_bot_uz/
├── bot.py          — Asosiy bot (O'zbek tilida)
├── config.py       — Token va admin sozlamalari
├── menu.py         — Menyu ma'lumotlari
├── cart.py         — Savatcha klassi
├── orders.py       — Buyurtmalar boshqaruvi
├── requirements.txt
└── data/           — Buyurtmalar va bronlar (JSON)
```

## Admin boshqaruvi

Har yangi buyurtmada siz (admin) 4 ta tugma bilan xabar olasiz:
- ✅ Tasdiqlash
- ❌ Bekor qilish
- 👨‍🍳 Tayyorlanmoqda
- 🎉 Yetkazildi

Har bir tugma bosilganda mijozga avtomatik xabar ketadi.

## Menyuni yangilash

`menu.py` faylini oching va `MENU` ro'yxatini tahrirlang.
Botni qayta ishga tushiring.
