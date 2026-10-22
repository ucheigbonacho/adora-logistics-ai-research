"""Compatibility import for the canonical routing decision implementation.

The decision function is defined in src.engine; this module retains the
import path used by dataset generation, evaluation, validation and tests.
"""
from src.engine import execute_routing_decision

__all__ = ["execute_routing_decision"]
