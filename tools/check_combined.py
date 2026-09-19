#!/usr/bin/env python3
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Original verification logic only; third-party rights remain separate.
"""Check arrays and menu IDs after round-trip decompilation of the built APK."""
import argparse
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from film_profiles import read_array, ricoh_profiles
from filter_strength import STRENGTHS, blend_profile
from filter_icons import verify_icons

ROOT = Path(__file__).resolve().parents[1]
HOOK_PATH = 'smali/com/yuki/imaging/app/pictureeffectplus/shooting/camera/RicohHook.smali'


def fields(text):
    links = re.findall(
        r'fill-array-data v1, :(\w+)\s+sput-object v1, [^\n]+->(sFuji\w+):(\[[IB])', text)
    result = {}
    for label, name, kind in links:
        data = read_array(text, label, 1 if kind == '[B' else 4, 2048 if kind == '[B' else 9)
        result[name] = [v & 255 for v in data] if kind == '[B' else data
    if len(result) != len(links):
        raise ValueError('Duplicate initialized fields')
    return result


def compiled_profile_arrays(decoded, hook):
    """Verify the final DEX has isolated initializers and valid lookup targets."""
    initializer = re.search(r'^\.method [^\n]* <clinit>\(\)V\n(.*?)^\.end method',
                            hook, re.M | re.S)
    assert initializer, 'Missing hook initializer'
    assert not re.search(r'new-array|fill-array-data|sget-object|invoke-', initializer[1]), \
        'Hook still eagerly initializes preset data'
    assert not fields(hook), 'Preset arrays must live in lazy holders'
    predicate = re.search(r'^\.method [^\n]* isRicohPreset\(Ljava/lang/String;\)Z\n(.*?)^\.end method',
                          hook, re.M | re.S)
    assert predicate and not re.search(r'getRGBMatrix|getGammaBytes|sget-object', predicate[1]), \
        'Availability checks must not load profile arrays'
    references = re.findall(
        r'sget-object v0, (L[^;]+\$Profile\d+_\d+;)->(sFuji\w+):(\[[IB])', hook)
    assert len(references) == 120 and len(set(references)) == 120, \
        'Every matrix/gamma lookup must target its own holder field exactly once'
    expected = {}
    for owner, name, kind in references:
        assert name not in expected, 'Multiple owners for one profile field'
        expected[name] = (owner, kind)
    arrays = {}
    holder_paths = sorted((decoded/HOOK_PATH).parent.glob('RicohHook$Profile*.smali'))
    assert len(holder_paths) == 60, 'Expected one holder per preset/strength pair'
    for path in holder_paths:
        text = path.read_text()
        owner = re.search(r'^\.class [^\n]* (L[^;]+;)$', text, re.M)[1]
        assert owner == 'L' + path.relative_to(decoded/'smali').with_suffix('').as_posix() + ';'
        members = re.findall(r'^\.field public static final (sFuji\w+):(\[[IB])$', text, re.M)
        assert len(members) == 2 and {kind for name, kind in members} == {'[B', '[I'}
        assert len(re.findall(r'^\.method ', text, re.M)) == 1
        assert '<clinit>()V' in text and text.count('new-array ') == 2
        assert not re.search(r'\bsget-object\b|\binvoke-', text), \
            'A holder must not initialize other holders or execute app code'
        initialized = fields(text)
        assert set(initialized) == {name for name, kind in members}
        stores = re.findall(r'sput-object v1, (L[^;]+;)->(sFuji\w+):(\[[IB])', text)
        assert set(stores) == {(owner, name, kind) for name, kind in members}, \
            'A holder must initialize its own declared fields'
        for name, kind in members:
            assert expected[name] == (owner, kind), 'Lookup/holder mismatch: ' + name
            assert name not in arrays, 'Duplicate profile field: ' + name
            arrays[name] = initialized[name]
    assert set(arrays) == set(expected)
    return arrays


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--decoded', type=Path, required=True,
                    help='Fresh apktool d -r output from the final signed APK')
    ap.add_argument('--upstream-hook', type=Path, required=True)
    ap.add_argument('--previous-decoded', type=Path,
                    help='Optional decoded 0.1.3 or later build, to compare existing arrays')
    args = ap.parse_args()
    profiles = json.loads((ROOT/'profiles/film_studio.json').read_text())['presets']
    hook = (args.decoded/HOOK_PATH).read_text()
    arrays = compiled_profile_arrays(args.decoded, hook)
    assert len(profiles) == 15 and len(arrays) == 120
    for i, p in enumerate(profiles):
        for strength in STRENGTHS:
            expected = blend_profile(p, strength)
            assert arrays[f'sFujimatrix{i}_{strength}'] == sum(expected['matrix'], [])
            raw = [b for v in expected['gamma'] for b in (v & 255, v >> 8)]
            assert arrays[f'sFujigamma{i}_{strength}'] == raw
    # Independent upstream input: verify both tinted and neutral presets retain
    # exact original values in the built DEX at the 100% endpoint.
    for i, p in enumerate(ricoh_profiles(args.upstream_hook), 10):
        assert profiles[i]['id'] == p['id']
        assert arrays[f'sFujimatrix{i}_100'] == sum(p['matrix'], [])
        assert arrays[f'sFujigamma{i}_100'] == [b for v in p['gamma'] for b in (v & 255, v >> 8)]
    menu = ET.parse(args.decoded/'assets/MenuData.xml')
    top = next(e for e in menu.iter() if e.get('ItemId') == 'ApplicationTop')
    ids = [p['id'] for p in profiles]
    assert [e.get('ItemId') for e in top] == ids
    assert [e.get('Value') for e in top] == ids
    assert verify_icons(args.decoded, profiles) == 15
    for method in ['getPresetIds', 'getRGBMatrix', 'getGammaBytes', 'getFilterName', 'getFilterGuide', 'isRicohPreset']:
        body = re.search(r'^\.method [^\n]* ' + method + r'\([^\n]*\n(.*?)^\.end method', hook, re.M | re.S)
        assert body, method
        for preset_id in ids:
            assert '"' + preset_id + '"' in body[1], (method, preset_id)
    movie = (args.decoded/'smali/com/sony/imaging/app/base/shooting/movie/trigger/MovieRecStandbyStateKeyHandler.smali').read_text()
    assert 'pushedCenterKey()I' in movie and '"ApplicationTop"' in movie
    assert '->isMovieRecording()Z' in movie
    assert '->isMovieRecording()Z' in hook
    resources = (args.decoded/'resources.arsc').read_bytes()
    assert '胶片工坊'.encode() in resources
    for old in ['理光相机', '富士风格']:
        assert old.encode() not in resources and old.encode('utf-16-le') not in resources
    previous_count = None
    if args.previous_decoded:
        previous_hook = (args.previous_decoded/HOOK_PATH).read_text()
        previous = fields(previous_hook)
        if not previous:
            previous = compiled_profile_arrays(args.previous_decoded, previous_hook)
        assert len(previous) in (80, 120)
        for field, values in previous.items():
            assert arrays[field] == values, field
        previous_count = len(previous)
    report = dict(
        profiles=15, strengths=list(STRENGTHS), compiled_arrays_checked=len(arrays),
        lazy_profile_holders=60, hook_eager_profile_arrays=0,
        first_selected_profile_array_bytes=2084, previous_eager_profile_array_bytes=125040,
        startup_timing_measured=False,
        upstream_ricoh_full_strength_exact=True,
        previous_compiled_arrays_unchanged=previous_count,
        previous_fuji_arrays_unchanged=min(previous_count, 80) if previous_count else None,
        menu_and_lookup_ids_match=True, renamed_resources=True,
        distinct_filter_badges_checked=15,
        movie_standby_shortcut_present=True, hardware_verified=False,
    )
    (ROOT/'validation/combined-static.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
