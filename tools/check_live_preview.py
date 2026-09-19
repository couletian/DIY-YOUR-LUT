#!/usr/bin/env python3
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Exercise emitted preview smali's branches with deterministic platform stubs.

This small, fail-closed interpreter tests the emitted state transitions rather
than a Python reimplementation of the preview logic. APK assembly separately
checks smali syntax. Camera rendering/performance still need a real device.
"""
import argparse
import json
from pathlib import Path
import re


class PreviewVM:
    def __init__(self, source):
        self.source = source
        self.methods = {}
        for declaration, body in re.findall(r'^\.method ([^\n]+)\n([\s\S]*?)^\.end method', source, re.M):
            self.methods[declaration.split()[-1]] = body
        self.fields = {'mController': 'controller', 'mGuideTextView': 'guide'}
        self.preferences = 'a'
        self.recording = False
        self.pending = False
        self.applies = []
        self.fail_apply = set()
        self.fail_save = False
        self.saved = []
        self.closed = False
        self.messages = []
        self.run_count = 0

    def call(self, signature, args=()):
        self.run_count += 1
        if self.run_count > 500:
            raise AssertionError('Unexpected recursion or transition loop')
        body = self.methods[signature]
        registers = {'p0': self}
        registers.update({'p' + str(i + 1): value for i, value in enumerate(args)})
        lines = [line.strip() for line in body.splitlines()]
        labels = {line: i for i, line in enumerate(lines) if line.startswith(':')}
        pc, result = 0, None
        while pc < len(lines):
            line = lines[pc]
            pc += 1
            if not line or line.startswith(('.', '#', ':')):
                continue
            op, _, values = line.partition(' ')
            operands = [s.strip() for s in values.split(',')]
            if op.startswith('const-string'):
                registers[operands[0]] = json.loads(values.split(',', 1)[1].strip())
            elif op.startswith('const'):
                registers[operands[0]] = int(operands[1], 0)
                if 'wide' in op:
                    registers['v' + str(int(operands[0][1:]) + 1)] = 0
            elif op.startswith('iget'):
                field = operands[2].split('->')[1].split(':')[0]
                registers[operands[0]] = self.fields.get(field)
            elif op.startswith('iput'):
                field = operands[2].split('->')[1].split(':')[0]
                self.fields[field] = registers[operands[0]]
            elif op == 'new-instance':
                registers[operands[0]] = operands[1]
            elif op.startswith('invoke'):
                match = re.fullmatch(r'\{([^}]*)\}, (.+)->(.+)', values)
                assert match, line
                names = [v.strip() for v in match[1].split(',') if v.strip()]
                actual = [registers.get(v) for v in names]
                owner, target = match[2], match[3]
                result = self.invoke(op, owner, target, actual)
            elif op.startswith('move-result'):
                registers[operands[0]] = result
            elif op == 'if-eqz':
                if not registers.get(operands[0]):
                    pc = labels[operands[1]]
            elif op == 'if-nez':
                if registers.get(operands[0]):
                    pc = labels[operands[1]]
            elif op == 'goto':
                pc = labels[operands[0]]
            elif op == 'return-void':
                return None
            elif op == 'return':
                return registers[operands[0]]
            else:
                raise AssertionError('Unsupported executed smali: ' + line)
        raise AssertionError('Fell off method: ' + signature)

    def invoke(self, op, owner, signature, args):
        if 'invoke-super' in op:
            if signature == 'closeMenuLayout(Landroid/os/Bundle;)V':
                self.closed = True
                return None
            raise AssertionError('Unexpected superclass call: ' + signature)
        if owner.endswith('PictureEffectPlusOptionMenuLayout;'):
            return self.call(signature, args[1:])
        if owner == 'Landroid/os/Looper;' and signature.startswith('getMainLooper'):
            return 'main-looper'
        if owner == 'Landroid/os/Handler;':
            if signature.startswith('<init>'):
                return None
            if signature.startswith('removeCallbacks'):
                self.pending = False
                return None
            if signature.startswith('postDelayed'):
                assert args[2] == 120, args
                self.pending = True
                return True
        if owner.endswith('MovieShootingExecutor;') and signature == 'isMovieRecording()Z':
            return self.recording
        if owner.endswith('PictureEffectPlusController;') and signature.startswith('getBackupEffectValue'):
            return self.preferences
        if owner.endswith('RicohHook;'):
            if signature.startswith('isRicohPreset'):
                return args[0] in ('a', 'b', 'c')
            if signature.startswith('applyHook'):
                assert not self.recording, 'Parameter write occurred during recording'
                self.applies.append(args[2])
                return args[2] not in self.fail_apply
        if owner == 'Ljava/lang/String;' and signature.startswith('equals'):
            return args[0] == args[1]
        if owner.endswith('BackUpUtil;'):
            if signature.startswith('getInstance'):
                return 'backup'
            if signature.startswith('setPreference'):
                assert args[1] == 'ID_PICTUREEFFECTPLUS_CURRENT_EFFECT'
                if self.fail_save:
                    return False
                self.preferences = args[2]
                self.saved.append(args[2])
                return True
        if owner == 'Landroid/widget/TextView;' and signature.startswith('setText'):
            self.messages.append(args[1])
            return None
        if owner == 'Landroid/util/Log;' and signature.startswith('e('):
            self.messages.append(args[1])
            return None
        raise AssertionError('Unexpected platform call: ' + owner + '->' + signature)

    def begin(self):
        self.call('beginFilmPreview()V')

    def highlight(self, value):
        self.fields['mSelectedItemId'] = value
        self.call('queueFilmPreview()V')

    def tick(self):
        if self.pending:
            self.pending = False
            self.call('run()V')


def check(decoded):
    matches = list((decoded / 'smali').glob('com/*/imaging/app/pictureeffectplus/shooting/layout/PictureEffectPlusOptionMenuLayout.smali'))
    assert len(matches) == 1, matches
    source = matches[0].read_text()
    results = []

    def done(name):
        results.append(name)

    vm = PreviewVM(source)
    vm.begin()
    vm.highlight('a')
    vm.highlight('b')
    vm.highlight('c')
    assert vm.applies == [] and vm.pending
    vm.tick()
    assert vm.applies == ['c'] and vm.preferences == 'a' and vm.saved == []
    done('rapid-scroll-latest-only-no-preference-write')
    vm.highlight('c')
    vm.tick()
    assert vm.applies == ['c']
    done('repeated-highlight-skips-hardware-write')
    vm.highlight('b')
    vm.call('pushedCenterKey()I')
    assert vm.applies == ['c', 'b'] and vm.saved == ['b'] and vm.closed and not vm.pending
    vm.call('run()V')
    assert vm.applies == ['c', 'b']
    done('center-flushes-newest-before-save-and-close')

    vm = PreviewVM(source)
    vm.begin()
    vm.highlight('b')
    vm.tick()
    vm.call('closeMenuLayout(Landroid/os/Bundle;)V', (None,))
    assert vm.applies == ['b', 'a'] and vm.preferences == 'a' and not vm.pending and vm.closed
    vm.call('run()V')
    assert vm.applies == ['b', 'a']
    done('cancel-restores-before-original-close-no-stale-callback')

    vm = PreviewVM(source)
    vm.begin()
    vm.highlight('b')
    vm.call('endFilmPreview()V')
    vm.tick()
    assert vm.applies == [] and vm.saved == []
    done('cancel-within-debounce-does-not-write')

    vm = PreviewVM(source)
    vm.begin()
    vm.highlight('b')
    vm.recording = True
    vm.tick()
    vm.call('pushedCenterKey()I')
    vm.call('endFilmPreview()V')
    assert vm.applies == [] and vm.saved == []
    done('recording-blocks-queued-preview-confirm-and-restore-writes')

    vm = PreviewVM(source)
    vm.begin()
    vm.fail_apply.add('b')
    vm.highlight('b')
    vm.tick()
    assert vm.applies == ['b', 'a'] and vm.fields['mFilmApplied'] == 'a' and vm.messages
    vm.call('pushedCenterKey()I')
    assert vm.applies == ['b', 'a', 'b', 'a'] and vm.saved == [] and not vm.closed
    done('partial-apply-failure-restores-original-never-commits')

    vm = PreviewVM(source)
    vm.begin()
    vm.highlight('b')
    vm.tick()
    vm.fail_save = True
    vm.call('pushedCenterKey()I')
    assert vm.applies == ['b', 'a'] and vm.saved == [] and not vm.closed
    done('save-failure-restores-original-keeps-browser-open')

    vm = PreviewVM(source)
    vm.begin()
    vm.highlight('not-a-filter')
    vm.tick()
    vm.call('pushedCenterKey()I')
    assert vm.applies == [] and vm.saved == []
    done('unknown-filter-is-rejected')

    for signature in ('pushedEnter5WayFuncKey()I', 'pushedEnterJoyStickFuncKey()I',
                      'doItemClickProcessing(Ljava/lang/String;)V'):
        vm = PreviewVM(source)
        vm.begin()
        vm.highlight('b')
        args = ('c',) if signature.startswith('doItemClick') else ()
        vm.call(signature, args)
        target = 'c' if args else 'b'
        assert vm.applies == [target] and vm.saved == [target] and vm.closed
    done('converted-enter-and-item-click-use-same-immediate-commit')

    methods = PreviewVM(source).methods
    selected = next(body for sig, body in methods.items() if sig.startswith('onItemSelected('))
    assert 'invoke-super' not in selected and 'execCurrentMenuItem' not in selected
    assert 'queueFilmPreview()V' in selected
    for sig in ('onPause()V', 'closeLayout()V', 'closeMenuLayout(Landroid/os/Bundle;)V', 'pushedMenuKey()I'):
        assert 'endFilmPreview()V' in methods[sig], sig
    assert 'getBackgroundDrawable' not in methods['onResume()V']
    view = methods['prepareFilmPreviewView()V']
    assert 'setBackgroundResource(I)V' in view and 'setVisibility(I)V' in view
    done('all-exit-hooks-present-and-opaque-sample-removed')
    return dict(checks=results, passed=len(results), camera_rendering_verified=False,
                note='Emitted-smali control-flow harness; actual camera UI and latency require a device.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('decoded', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = check(args.decoded)
    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(output + '\n')
    print(output)
