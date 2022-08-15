# Copyright (c) Meta Platforms, Inc. and affiliates.
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Linux Kernel
------------

The ``drgn.helpers.linux`` package contains several modules for working with
data structures and subsystems in the Linux kernel. The helpers are available
from the individual modules in which they are defined and from this top-level
package. E.g., the following are both valid:

>>> from drgn.helpers.linux.list import list_for_each_entry
>>> from drgn.helpers.linux import list_for_each_entry

Iterator macros (``for_each_foo``) are a common idiom in the Linux kernel. The
equivalent drgn helpers are implemented as Python :ref:`generators
<python:tut-generators>`. For example, the following code in C:

.. code-block:: c

    list_for_each(pos, head)
            do_something_with(pos);

Translates to the following code in Python:

.. code-block:: python3

    for pos in list_for_each(head):
        do_something_with(pos)
"""

import importlib
import pkgutil
from typing import List, Optional

from drgn import IntegerLike, Object, Program
from drgn.helpers import escape_ascii_string
from drgn.helpers.linux.slab import slab_cache_containing

__all__: List[str] = []
for _module_info in pkgutil.iter_modules(
    __path__,  # type: ignore[name-defined]  # python/mypy#1422
    prefix=__name__ + ".",
):
    _submodule = importlib.import_module(_module_info.name)
    _submodule_all = getattr(_submodule, "__all__", ())
    __all__.extend(_submodule_all)
    for _name in _submodule_all:
        globals()[_name] = getattr(_submodule, _name)


def identify_address(prog: Program, addr: IntegerLike) -> Optional[str]:
    """
    Identify an address as a symbol or slab object.

    This will currently identify the following types of addresses as follows:

    * Symbols (e.g., addresses in functions or global variables): `"symbol_name+offset"`.
    * Slab objects: `"slab_name"`.

    This may learn to recognize other types of addresses in the future.

    :return: Identity as string or ``None` if the address is unrecognized.
    """

    try:
        if isinstance(addr, Object):
            addr_value = addr.value_()
        else:
            addr_value = addr

        symbol = prog.symbol(addr)
        offset = addr_value - symbol.address

        return '"{}"+{}'.format(symbol.name, offset)
    except LookupError:  # not a symbol
        slab_cache = slab_cache_containing(prog, addr)

        if slab_cache.value_():
            # address is slab allocated
            cache_name = escape_ascii_string(
                slab_cache.name.string_(), escape_backslash=True
            )
            return '"{}"'.format(cache_name)

        # Unrecognized address
        return None
