# Copyright (c) Meta Platforms, Inc. and affiliates.
# SPDX-License-Identifier: GPL-3.0-or-later

from drgn.helpers.linux import identify_address
from tests.linux_kernel import LinuxKernelTestCase


class TestSlab(LinuxKernelTestCase):
    def test_identify_symbol(self):
        symbol = self.prog.symbol("jiffies")
        self.assertEqual(identify_address(
            self.prog, symbol.address),
            '"jiffies_64+0"'
        )
