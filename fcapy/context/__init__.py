"""
This subpackage provides a class FormalContext to work with Formal Context object from FCA theory.
Other modules are implemented to shorten FormalContext class.

Classes
-------
formal_context.FormalContext

Modules:
  formal_context:
    Implements Formal Context class
  converters:
    Contains function to read/write a FormalContext object from/to a file
"""

from .formal_context import FormalContext
from .converters import read_cxt, read_json, read_csv, from_pandas
