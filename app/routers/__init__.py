# This file makes the routers directory a Python package
# Export routers for easy importing

from . import auth, users, admin, posts, comments, search

__all__ = ["auth", "users", "admin", "posts", "comments", "search"]