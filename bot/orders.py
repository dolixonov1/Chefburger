"""
OrderManager — stores orders and reservations in JSON files
Replace with a real database (PostgreSQL, SQLite) for production.
"""

import json
import os
import random
import string
from datetime import datetime
from cart import Cart


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
ORDERS_FILE = os.path.join(DATA_DIR, "orders.json")
RESERVATIONS_FILE = os.path.join(DATA_DIR, "reservations.json")


def _load(path: str) -> dict:
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(path: str, data: dict):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _gen_id(prefix: str = "") -> str:
    suffix = "".join(random.choices(string.digits, k=5))
    return f"{prefix}{suffix}"


class OrderManager:

    # ── ORDERS ──

    def create_order(
        self,
        user_id: int,
        user_name: str,
        phone: str,
        order_type: str,
        order_type_label: str,
        address: str,
        time: str,
        cart: Cart,
    ) -> dict:
        orders = _load(ORDERS_FILE)
        order_id = _gen_id("ORD")

        items_snapshot = [
            {
                "id":    entry["id"],
                "name":  entry["name"],
                "price": entry["price"],
                "category": entry["category"],
                "qty":   entry["qty"],
            }
            for entry in cart.items.values()
        ]

        order = {
            "id":               order_id,
            "user_id":          user_id,
            "name":             user_name,
            "phone":            phone,
            "order_type":       order_type,
            "order_type_label": order_type_label,
            "address":          address,
            "time":             time,
            "items":            items_snapshot,
            "subtotal":         cart.subtotal(),
            "delivery_fee":     cart.delivery_fee(order_type),
            "total":            cart.total(order_type),
            "status":           "pending",
            "date":             datetime.now().strftime("%d %b %Y, %H:%M"),
            "eta":              "30",
        }

        orders[order_id] = order
        _save(ORDERS_FILE, orders)
        return order

    def get_order(self, order_id: str) -> dict | None:
        return _load(ORDERS_FILE).get(order_id)

    def get_user_orders(self, user_id: int) -> list[dict]:
        orders = _load(ORDERS_FILE)
        user_orders = [o for o in orders.values() if o["user_id"] == user_id]
        return sorted(user_orders, key=lambda o: o["date"])

    def update_status(self, order_id: str, status: str) -> dict | None:
        orders = _load(ORDERS_FILE)
        if order_id not in orders:
            return None
        orders[order_id]["status"] = status
        _save(ORDERS_FILE, orders)
        return orders[order_id]

    def get_all_orders(self, status: str = None) -> list[dict]:
        orders = _load(ORDERS_FILE)
        result = list(orders.values())
        if status:
            result = [o for o in result if o["status"] == status]
        return sorted(result, key=lambda o: o["date"], reverse=True)

    # ── RESERVATIONS ──

    def create_reservation(
        self,
        user_id: int,
        name: str,
        phone: str,
        date: str,
        time: str,
        guests: str,
    ) -> str:
        reservations = _load(RESERVATIONS_FILE)
        res_id = _gen_id("RES")
        reservations[res_id] = {
            "id":      res_id,
            "user_id": user_id,
            "name":    name,
            "phone":   phone,
            "date":    date,
            "time":    time,
            "guests":  guests,
            "status":  "confirmed",
            "created": datetime.now().strftime("%d %b %Y, %H:%M"),
        }
        _save(RESERVATIONS_FILE, reservations)
        return res_id

    def get_user_reservations(self, user_id: int) -> list[dict]:
        reservations = _load(RESERVATIONS_FILE)
        return [r for r in reservations.values() if r["user_id"] == user_id]

    def get_all_reservations(self) -> list[dict]:
        return list(_load(RESERVATIONS_FILE).values())
