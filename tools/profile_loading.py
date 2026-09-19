# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Original additions only; underlying third-party rights remain separate. See LICENSING.md and NOTICE.
"""Initialize one selected matrix/curve pair, not every preset at app startup.

Each preset/strength pair has a small class whose static initializer runs on its
first sget-object. Dalvik class initialization provides synchronization and keeps
the arrays for subsequent selections without a custom cache or background work.
Only dex 035 / Android API 10 instructions are used.
"""
from filter_strength import STRENGTHS, blend_profile


def holder_descriptor(hook, preset_index, strength):
    if not hook.startswith('L') or not hook.endswith(';'):
        raise ValueError('Expected a smali class descriptor')
    if preset_index < 0 or strength not in STRENGTHS:
        raise ValueError('Unknown preset or strength')
    return hook[:-1] + f'$Profile{preset_index}_{strength};'


def field_reference(hook, kind, preset_index, strength):
    descriptor = holder_descriptor(hook, preset_index, strength)
    data_type = {'matrix': '[I', 'gamma': '[B'}[kind]
    return f'{descriptor}->sFuji{kind}{preset_index}_{strength}:{data_type}'


def empty_init():
    """The hook itself needs no eagerly allocated profile arrays."""
    return '\n'.join(('.method static constructor <clinit>()V',
                      '    .locals 0', '    return-void', '.end method'))


def holder_smali(hook, preset_index, profile, strength):
    descriptor = holder_descriptor(hook, preset_index, strength)
    blend = blend_profile(profile, strength)
    arrays = (
        ('matrix', '[I', sum(blend['matrix'], []), 4),
        ('gamma', '[B', [b for v in blend['gamma'] for b in (v & 255, v >> 8)], 1),
    )
    lines = [f'.class public final {descriptor}', '.super Ljava/lang/Object;', '']
    for kind, data_type, values, width in arrays:
        lines.append(f'.field public static final sFuji{kind}{preset_index}_{strength}:{data_type}')
    lines += ['', '.method static constructor <clinit>()V', '    .locals 2']
    payloads = []
    for kind, data_type, values, width in arrays:
        field = field_reference(hook, kind, preset_index, strength)
        lines += [f'    const/16 v0, {hex(len(values))}',
                  f'    new-array v1, v0, {data_type}',
                  f'    fill-array-data v1, :data_{kind}',
                  f'    sput-object v1, {field}']
        payloads += [f'    :data_{kind}', f'    .array-data {width}']
        for value in values:
            number = '-0x%x' % -value if value < 0 else '0x%x' % value
            payloads.append('        ' + number + ('t' if width == 1 else ''))
        payloads.append('    .end array-data')
    return '\n'.join(lines + ['    return-void'] + payloads + ['.end method', ''])


def write_profile_holders(hook_path, profiles, hook):
    """Write sibling smali files before the build's normal package rename."""
    if hook_path.stem != hook.rsplit('/', 1)[-1][:-1]:
        raise ValueError('Hook path and descriptor differ')
    outputs = []
    for index, profile in enumerate(profiles):
        for strength in STRENGTHS:
            descriptor = holder_descriptor(hook, index, strength)
            filename = descriptor.rsplit('/', 1)[-1][:-1] + '.smali'
            target = hook_path.with_name(filename)
            # Build inputs are freshly decoded; fail rather than overwrite an
            # unexpected upstream class with the generated name.
            with target.open('x', encoding='utf-8') as stream:
                stream.write(holder_smali(hook, index, profile, strength))
            outputs.append(target)
    return outputs
