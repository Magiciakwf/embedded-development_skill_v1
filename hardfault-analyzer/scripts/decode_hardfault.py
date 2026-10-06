#!/usr/bin/env python3
"""Decode captured Armv7-M fault evidence; no target access or inferred root cause.

Stdlib only. M0/M0+ and Armv8-M security/frame additions are outside this
decoder's scope. Use the exact core manual before applying these results.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess

CFSR = {
    0: 'IACCVIOL', 1: 'DACCVIOL', 3: 'MUNSTKERR', 4: 'MSTKERR',
    5: 'MLSPERR', 7: 'MMARVALID', 8: 'IBUSERR', 9: 'PRECISERR',
    10: 'IMPRECISERR', 11: 'UNSTKERR', 12: 'STKERR', 13: 'LSPERR',
    15: 'BFARVALID', 16: 'UNDEFINSTR', 17: 'INVSTATE', 18: 'INVPC',
    19: 'NOCP', 24: 'UNALIGNED', 25: 'DIVBYZERO',
}
HFSR = {1: 'VECTTBL', 30: 'FORCED', 31: 'DEBUGEVT'}
SHCSR = {
    0: 'MEMFAULTACT', 1: 'BUSFAULTACT', 3: 'USGFAULTACT',
    7: 'SVCALLACT', 8: 'MONITORACT', 10: 'PENDSVACT', 11: 'SYSTICKACT',
    12: 'USGFAULTPENDED', 13: 'MEMFAULTPENDED', 14: 'BUSFAULTPENDED',
    15: 'SVCALLPENDED', 16: 'MEMFAULTENA', 17: 'BUSFAULTENA', 18: 'USGFAULTENA',
}
EXC_RETURNS = {
    0xFFFFFFF1: ('handler', 'MSP', 'basic'),
    0xFFFFFFF9: ('thread', 'MSP', 'basic'),
    0xFFFFFFFD: ('thread', 'PSP', 'basic'),
    0xFFFFFFE1: ('handler', 'MSP', 'extended'),
    0xFFFFFFE9: ('thread', 'MSP', 'extended'),
    0xFFFFFFED: ('thread', 'PSP', 'extended'),
}
FRAME_ERRORS = {'MSTKERR', 'MUNSTKERR', 'MLSPERR', 'STKERR', 'UNSTKERR', 'LSPERR'}


def uint32(value):
    try:
        result = int(value, 0)
    except ValueError as exc:
        raise argparse.ArgumentTypeError('expected decimal or prefixed hexadecimal integer') from exc
    if not 0 <= result <= 0xFFFFFFFF:
        raise argparse.ArgumentTypeError('value must be an unsigned 32-bit integer')
    return result


def register(value, table):
    if value is None:
        return None
    mask = sum(1 << bit for bit in table)
    return {'raw': value, 'hex': f'0x{value:08x}',
            'flags': [name for bit, name in table.items() if value & (1 << bit)],
            'unknown_set_bits': value & (~mask & 0xFFFFFFFF)}


def decode(*, cfsr=None, hfsr=None, shcsr=None, mmfar=None, bfar=None,
           exc_return=None, pc=None, xpsr=None):
    raw = dict(cfsr=cfsr, hfsr=hfsr, shcsr=shcsr, mmfar=mmfar, bfar=bfar,
               exc_return=exc_return, pc=pc, xpsr=xpsr)
    for name, value in raw.items():
        if value is not None and (type(value) is not int or not 0 <= value <= 0xFFFFFFFF):
            raise ValueError(f'{name} must be an unsigned 32-bit integer or None')
    result = {
        'model': 'Armv7-M (FPU fields only where implemented)',
        'raw': raw,
        'registers': {'CFSR': register(cfsr, CFSR), 'HFSR': register(hfsr, HFSR),
                      'SHCSR': register(shcsr, SHCSR)},
        'addresses': {}, 'frame': None, 'pc': None, 'cautions': [],
    }
    cautions = result['cautions']
    for name, reg in result['registers'].items():
        if reg and reg['unknown_set_bits']:
            cautions.append({'code': 'unknown_bits', 'message':
                             f"{name} has unrecognized set bits {reg['unknown_set_bits']:#010x}; check core/model."})
    flags = set(result['registers']['CFSR']['flags']) if cfsr is not None else set()
    for name, value, valid_bit in [('MMFAR', mmfar, 7), ('BFAR', bfar, 15)]:
        valid = None if cfsr is None else bool(cfsr & (1 << valid_bit))
        result['addresses'][name] = {'raw': value, 'valid': valid,
                                    'usable': value is not None and valid is True}
        if value is not None and valid is not True:
            cautions.append({'code': 'address_not_valid', 'message':
                             f'{name} cannot be attributed to this fault: validity is '
                             + ('unknown without CFSR.' if valid is None else 'not set.')})
        if value is None and valid is True:
            cautions.append({'code': 'address_missing', 'message': f'{name} valid bit is set but value was not captured.'})
    if hfsr is not None and hfsr & (1 << 30) and (cfsr is None or cfsr == 0):
        cautions.append({'code': 'escalation_unresolved', 'message':
                         'FORCED is set without a captured CFSR cause; escalation mechanism remains unresolved.'})
    frame_errors = sorted(flags & FRAME_ERRORS)
    if frame_errors:
        cautions.append({'code': 'frame_unreliable', 'message':
                         'Stack/unstack/lazy-state errors require validation before trusting frame words: '
                         + ', '.join(frame_errors)})
    if exc_return is not None:
        frame = {'raw': exc_return, 'encoding_valid': exc_return in EXC_RETURNS,
                 'memory_validated': False, 'status_errors': frame_errors}
        if frame['encoding_valid']:
            mode, stack, kind = EXC_RETURNS[exc_return]
            frame.update(mode=mode, stack=stack, kind=kind,
                         core_offset=0, pc_offset=0x18, xpsr_offset=0x1C,
                         frame_bytes=0x20 if kind == 'basic' else 0x68)
            if kind == 'extended':
                frame.update(fp_offset=0x20, fpscr_offset=0x60)
                cautions.append({'code': 'fp_frame_condition', 'message':
                                 'Extended offsets require applicable FPU state; verify lazy preservation and FPCCR.'})
        else:
            cautions.append({'code': 'invalid_exc_return', 'message':
                             'LR is not a conventional Armv7-M EXC_RETURN; no stack/frame offsets inferred.'})
        result['frame'] = frame
    if xpsr is not None:
        result['xpsr'] = {'raw': xpsr, 'thumb_state': bool(xpsr & (1 << 24)),
                          'alignment_pad': bool(xpsr & (1 << 9)), 'ipsr': xpsr & 0x1FF}
        if not xpsr & (1 << 24):
            cautions.append({'code': 'thumb_state_clear', 'message':
                             'Stacked xPSR.T is clear: check invalid execution state or frame integrity.'})
    if pc is not None:
        result['pc'] = {'raw': pc, 'symbol_address': pc, 'automatic_subtraction': 0,
                        'fault_instruction_established': False}
        if pc & 1:
            cautions.append({'code': 'odd_stacked_pc', 'message':
                             'Captured PC is odd; confirm this is an instruction PC rather than a marked function pointer.'})
        if xpsr is None:
            cautions.append({'code': 'thumb_state_unknown', 'message':
                             'Thumb state is in stacked xPSR.T, not PC bit 0; xPSR was not supplied.'})
        if 'IMPRECISERR' in flags:
            cautions.append({'code': 'imprecise_pc', 'message':
                             'IMPRECISERR does not identify the responsible access at this PC; inspect preceding CPU writes.'})
        elif 'PRECISERR' in flags:
            cautions.append({'code': 'precise_pc_candidate', 'message':
                             'With a valid frame, PRECISERR identifies the faulting instruction at the captured PC; do not subtract 2/4.'})
    return result


def resolve(elf, pc, tool, timeout=10):
    """Return explicit status, never mistake an unknown symbol for resolution."""
    if not Path(elf).is_file():
        return {'status': 'elf_missing', 'tool': tool}
    executable = shutil.which(tool)
    if not executable:
        return {'status': 'tool_missing', 'tool': tool}
    try:
        proc = subprocess.run([executable, '-e', str(elf), '-f', '-C', '-i', hex(pc)],
                              capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {'status': 'timeout', 'tool': tool}
    except (OSError, UnicodeError) as exc:
        return {'status': 'tool_error', 'tool': tool, 'error': str(exc)}
    if proc.returncode:
        return {'status': 'tool_error', 'tool': tool, 'error': proc.stderr.strip()}
    lines = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    has_symbol = any(line not in ('??', '?') for line in lines[0::2])
    has_location = any(not line.startswith(('??:', '?:')) for line in lines[1::2])
    return {'status': 'resolved' if has_symbol or has_location else 'unresolved',
            'tool': tool, 'output': lines}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--architecture', choices=['armv7-m'], default='armv7-m',
                        help='supported model; M0 and Armv8-M frames are outside scope')
    for name in ('cfsr', 'hfsr', 'shcsr', 'bfar', 'pc', 'xpsr'):
        parser.add_argument('--' + name, type=uint32)
    parser.add_argument('--mmfar', '--mmar', dest='mmfar', type=uint32)
    parser.add_argument('--exc-return', '--lr', dest='exc_return', type=uint32,
                        help='LR captured at exception entry, not a normal function LR')
    parser.add_argument('--elf', help='matching ELF for optional addr2line lookup')
    parser.add_argument('--tool', default='arm-none-eabi-addr2line')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args(argv)
    if args.cfsr is None and args.hfsr is None:
        parser.error('provide at least --cfsr or --hfsr (zero is a valid captured value)')
    if args.elf and args.pc is None:
        parser.error('--elf requires --pc')
    result = decode(**{name: getattr(args, name) for name in
                       ('cfsr', 'hfsr', 'shcsr', 'mmfar', 'bfar', 'exc_return', 'pc', 'xpsr')})
    if args.elf:
        result['symbols'] = resolve(args.elf, args.pc, args.tool)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(result['model'])
        for name, reg in result['registers'].items():
            if reg is not None:
                print(f"{name} = {reg['hex']}: {', '.join(reg['flags']) or 'no recognized bits set'}")
        for name, address in result['addresses'].items():
            if address['raw'] is not None:
                print(f"{name} = {address['raw']:#010x}; valid={address['valid']}")
        if result['frame']:
            print('Frame:', json.dumps(result['frame']))
        if result['pc']:
            print(f"Captured PC = {args.pc:#010x}; no automatic subtraction")
        if 'symbols' in result:
            print('Symbols:', json.dumps(result['symbols']))
        for caution in result['cautions']:
            print(f"[{caution['code']}] {caution['message']}")
        print('Frame memory/map not validated; decoded bits do not confirm root cause.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
