"""
Utility functions for the routers module.
This module re-exports functions from other modules to maintain
better organization and avoid circular imports.
"""

from ..crud import store_image_reference

__all__ = ['store_image_reference']