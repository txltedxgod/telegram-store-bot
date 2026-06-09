"""Aggregate all routers into a single router for the dispatcher."""
from __future__ import annotations

from aiogram import Router

from bot.handlers import (
    admin,
    cart,
    catalog,
    checkout,
    favorites,
    orders,
    profile,
    search,
    start,
)


def get_main_router() -> Router:
    router = Router(name="main")
    router.include_router(start.router)
    router.include_router(catalog.router)
    router.include_router(cart.router)
    router.include_router(checkout.router)
    router.include_router(orders.router)
    router.include_router(profile.router)
    router.include_router(favorites.router)
    router.include_router(search.router)
    # Admin last so its IsAdmin-filtered handlers are evaluated explicitly.
    router.include_router(admin.router)
    return router
