"""Finite-state-machine state groups used across the bot."""
from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


class CheckoutSG(StatesGroup):
    """Order checkout flow."""

    contact = State()
    comment = State()
    confirm = State()


class AddProductSG(StatesGroup):
    """Admin: add a new product."""

    name = State()
    price = State()
    description = State()
    category = State()
    stock = State()


class EditProductSG(StatesGroup):
    """Admin: edit an existing product."""

    field = State()
    value = State()


class BroadcastSG(StatesGroup):
    """Admin: broadcast a message to all users."""

    message = State()
    confirm = State()


class PromocodeSG(StatesGroup):
    """Admin: create a promocode."""

    code = State()
    discount = State()
    max_uses = State()


class SearchSG(StatesGroup):
    """User: search products by name."""

    query = State()


__all__ = [
    "CheckoutSG",
    "AddProductSG",
    "EditProductSG",
    "BroadcastSG",
    "PromocodeSG",
    "SearchSG",
]
