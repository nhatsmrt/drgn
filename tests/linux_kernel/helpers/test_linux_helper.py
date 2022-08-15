# Copyright (c) Meta Platforms, Inc. and affiliates.
# SPDX-License-Identifier: GPL-3.0-or-later

from drgn.helpers.linux import identify_address
from drgn.helpers.linux.mm import pfn_to_virt
from tests.linux_kernel import (
    LinuxKernelTestCase,
    skip_unless_have_full_mm_support,
    skip_unless_have_test_kmod,
)


class TestLinuxHelpers(LinuxKernelTestCase):
    def test_identify_symbol(self):
        symbol = self.prog.symbol("__schedule")
        self.assertEqual(
            identify_address(self.prog, symbol.address + 1), "__schedule+1"
        )

    @skip_unless_have_full_mm_support
    @skip_unless_have_test_kmod
    def test_identify_slab_cache(self):
        objects = self.prog["drgn_test_slab_objects"]

        if not self.prog["drgn_test_slob"]:
            for obj in objects:
                value = hex(self.prog.read_word(obj))
                self.assertEqual(
                    identify_address(self.prog, obj),
                    f"[{value}:drgn_test]",
                )

    def test_identify_unrecognized(self):
        start_addr = (pfn_to_virt(self.prog["min_low_pfn"])).value_()
        end_addr = (pfn_to_virt(self.prog["max_pfn"]) + self.prog["PAGE_SIZE"]).value_()

        self.assertIsNone(identify_address(self.prog, start_addr - 1))
        self.assertIsNone(identify_address(self.prog, end_addr))
