"""Regression tests for fault evidence interpretation and CLI failure paths."""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import decode_hardfault as decoder


class DecodeTests(unittest.TestCase):
    def codes(self, result):
        return {item['code'] for item in result['cautions']}

    def test_even_pc_and_precise_fault_preserve_instruction_address(self):
        result = decoder.decode(cfsr=0x8200, hfsr=0x40000000, bfar=0,
                                exc_return=0xFFFFFFFD, pc=0x08001234, xpsr=0x01000000)
        self.assertEqual(result['registers']['CFSR']['flags'], ['PRECISERR', 'BFARVALID'])
        self.assertTrue(result['addresses']['BFAR']['usable'])
        self.assertEqual(result['pc']['symbol_address'], 0x08001234)
        self.assertEqual(result['pc']['automatic_subtraction'], 0)
        self.assertNotIn('odd_stacked_pc', self.codes(result))
        self.assertTrue(result['xpsr']['thumb_state'])

    def test_address_without_valid_bit_is_not_usable(self):
        result = decoder.decode(cfsr=0x200, bfar=0x20000000, mmfar=0x10000000)
        self.assertFalse(result['addresses']['BFAR']['usable'])
        self.assertFalse(result['addresses']['MMFAR']['usable'])

    def test_address_validity_unknown_without_cfsr(self):
        result = decoder.decode(hfsr=0x40000000, bfar=0x40000000)
        self.assertIsNone(result['addresses']['BFAR']['valid'])
        self.assertFalse(result['addresses']['BFAR']['usable'])

    def test_valid_address_bit_without_value(self):
        result = decoder.decode(cfsr=0x80)
        self.assertIn('address_missing', self.codes(result))

    def test_imprecise_pc_is_not_attributed(self):
        result = decoder.decode(cfsr=0x400, pc=0x08001234)
        self.assertIn('imprecise_pc', self.codes(result))
        self.assertFalse(result['pc']['fault_instruction_established'])

    def test_basic_and_extended_frame_offsets(self):
        for value, pc_offset, stack in [(0xFFFFFFF9, 0x18, 'MSP'),
                                        (0xFFFFFFFD, 0x18, 'PSP'),
                                        (0xFFFFFFED, 0x18, 'PSP')]:
            with self.subTest(value=value):
                frame = decoder.decode(cfsr=0, exc_return=value)['frame']
                self.assertEqual(frame['pc_offset'], pc_offset)
                self.assertEqual(frame['stack'], stack)
                self.assertFalse(frame['memory_validated'])

    def test_extended_frame_keeps_core_words_below_fp_context(self):
        # Raw layout from Arm DDI 0403E.e PushStack(): core 0..7, FP 8..25.
        words = [1, 2, 3, 4, 12, 0x08001001, 0x08001234, 0x01000000]
        words += [0x3f800000] * 16 + [0x12340000, 0]
        frame = decoder.decode(cfsr=0, exc_return=0xFFFFFFED)['frame']
        self.assertEqual(words[frame['pc_offset'] // 4], 0x08001234)
        self.assertEqual(words[frame['xpsr_offset'] // 4], 0x01000000)
        self.assertEqual(words[frame['fpscr_offset'] // 4], 0x12340000)
        self.assertEqual(frame['frame_bytes'], len(words) * 4)

    def test_normal_lr_does_not_select_stack(self):
        result = decoder.decode(cfsr=0, exc_return=0x08001235)
        self.assertFalse(result['frame']['encoding_valid'])
        self.assertNotIn('pc_offset', result['frame'])

    def test_stacking_error_marks_frame_unreliable(self):
        result = decoder.decode(cfsr=0x1000, exc_return=0xFFFFFFFD)
        self.assertIn('frame_unreliable', self.codes(result))

    def test_thumb_state_comes_from_xpsr(self):
        result = decoder.decode(cfsr=0x20000, pc=0x08001234, xpsr=0)
        self.assertIn('thumb_state_clear', self.codes(result))
        self.assertNotIn('odd_stacked_pc', self.codes(result))

    def test_alignment_pad_does_not_shift_pc_offset(self):
        result = decoder.decode(cfsr=0, exc_return=0xFFFFFFFD, xpsr=0x01000200)
        self.assertTrue(result['xpsr']['alignment_pad'])
        self.assertEqual(result['frame']['pc_offset'], 0x18)

    def test_unknown_bits_are_retained(self):
        result = decoder.decode(cfsr=0x00100000)
        self.assertEqual(result['registers']['CFSR']['unknown_set_bits'], 0x00100000)
        self.assertIn('unknown_bits', self.codes(result))

    def test_forced_without_cause_remains_unresolved(self):
        result = decoder.decode(cfsr=0, hfsr=0x40000000)
        self.assertIn('escalation_unresolved', self.codes(result))

    def test_mixed_faults_all_decode(self):
        result = decoder.decode(cfsr=0x02000002)
        self.assertEqual(result['registers']['CFSR']['flags'], ['DACCVIOL', 'DIVBYZERO'])

    def test_input_bounds_and_missing_input(self):
        for args in [[], ['--cfsr', '-1'], ['--cfsr', '0x100000000'],
                     ['--cfsr', 'banana'], ['--cfsr', '0', '--elf', 'a.elf'],
                     ['--architecture', 'armv8-m', '--cfsr', '0']]:
            with self.subTest(args=args), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as caught:
                    decoder.main(args)
                self.assertEqual(caught.exception.code, 2)

    def test_json_cli_aliases(self):
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            self.assertEqual(decoder.main(['--cfsr', '0x82', '--mmar', '0',
                                           '--lr', '0xFFFFFFFD', '--json']), 0)
        result = json.loads(stream.getvalue())
        self.assertTrue(result['addresses']['MMFAR']['usable'])
        self.assertEqual(result['frame']['stack'], 'PSP')

    def test_resolver_missing_elf(self):
        self.assertEqual(decoder.resolve('not-a-real-elf-file.elf', 0, 'tool')['status'], 'elf_missing')

    def test_resolver_timeout_and_unknown_symbol(self):
        with tempfile.TemporaryDirectory() as temp:
            elf = Path(temp) / 'matching.elf'
            elf.write_bytes(b'fixture')
            with patch.object(decoder.shutil, 'which', return_value='tool'), \
                 patch.object(decoder.subprocess, 'run', side_effect=subprocess.TimeoutExpired('tool', 10)):
                self.assertEqual(decoder.resolve(elf, 0x08001234, 'tool')['status'], 'timeout')
            proc = subprocess.CompletedProcess([], 0, '??\n??:0\n', '')
            with patch.object(decoder.shutil, 'which', return_value='tool'), \
                 patch.object(decoder.subprocess, 'run', return_value=proc) as run:
                self.assertEqual(decoder.resolve(elf, 0x08001234, 'tool')['status'], 'unresolved')
                self.assertEqual(run.call_args.args[0][-1], '0x8001234')


if __name__ == '__main__':
    unittest.main()
