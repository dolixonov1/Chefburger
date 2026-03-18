"""
Cart — per-user shopping cart stored in context.user_data
"""

import config


class Cart:
    def __init__(self):
        self.items: dict = {}  # item_id -> {id, name, price, qty, category}

    def add(self, item: dict, qty: int = 1):
        item_id = str(item["id"])
        if item_id in self.items:
            self.items[item_id]["qty"] += qty
        else:
            self.items[item_id] = {
                "id":       item["id"],
                "name":     item["name"],
                "price":    item["price"],
                "category": item["category"],
                "qty":      qty,
            }

    def remove(self, item_id: int):
        key = str(item_id)
        if key in self.items:
            del self.items[key]

    def decrement(self, item_id: int):
        key = str(item_id)
        if key in self.items:
            self.items[key]["qty"] -= 1
            if self.items[key]["qty"] <= 0:
                del self.items[key]

    def clear(self):
        self.items = {}

    def is_empty(self) -> bool:
        return len(self.items) == 0

    def count(self) -> int:
        return sum(e["qty"] for e in self.items.values())

    def subtotal(self) -> int:
        return sum(e["price"] * e["qty"] for e in self.items.values())

    def delivery_fee(self, order_type: str = "delivery") -> int:
        if order_type != "delivery":
            return 0
        if self.subtotal() >= config.FREE_DELIVERY_THRESHOLD:
            return 0
        return config.DELIVERY_FEE

    def total(self, order_type: str = "delivery") -> int:
        return self.subtotal() + self.delivery_fee(order_type)

    def summary_lines(self) -> list[str]:
        lines = []
        for entry in self.items.values():
            lines.append(
                f"• {entry['name']} x{entry['qty']} — {entry['price'] * entry['qty']:,} UZS"
            )
        return lines
