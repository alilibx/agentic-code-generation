"""
Policy-to-Code Pipeline
Convert plain text policies into executable Python functions.
"""

__version__ = "1.0.0"
__author__ = "Policy-to-Code Team"

from .pipeline import PolicyPipeline, quick_generate

__all__ = ['PolicyPipeline', 'quick_generate']
