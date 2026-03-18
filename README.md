# Chef Burger

Chef Burger is a simple restaurant web app and Telegram bot project. It includes:

- `index.html`, `min.html` - frontend landing page(s)
- `script.js`, `styles.css` - UI behavior and styling
- `bot/` - Telegram bot implementation in Python for ordering and admin workflow

## Bot features

- Customer menu interaction (add to cart, checkout)
- Order storage (`bot/data/orders.json`)
- Admin order buttons: Approve, Reject, Preparing, Delivered
- Configured with token and admin id in `bot/config.py`

## Setup (Bot)

1. Enter `bot/` and create/verify `config.py` (token, admin id).
2. Create a virtual environment and activate it (recommended):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r bot/requirements.txt
   ```
4. Run the bot:
   ```bash
   cd bot
   python bot.py
   ```

## Setup (Web UI)

Open `index.html` or `min.html` in a browser. No backend required for static demo pages.

## Project structure

```
chef burger/
├── index.html
├── min.html
├── script.js
├── styles.css
└── bot/
    ├── bot.py
    ├── cart.py
    ├── config.py
    ├── menu.py
    ├── orders.py
    ├── requirements.txt
    └── data/orders.json
```

## Existing Bot README

- More Telegram bot docs and deployment instructions: `bot/README.md`.
