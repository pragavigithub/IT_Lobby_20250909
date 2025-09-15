"""
Models for GRPO Module - Re-exports from main models.py to avoid table redefinition
"""
# Re-export GRPO models from main models.py to avoid duplicate table definitions
from models import GRPODocument, GRPOItem

# All GRPO models are now imported from the main models.py file
# This prevents SQLAlchemy table redefinition errors
__all__ = ['GRPODocument', 'GRPOItem']