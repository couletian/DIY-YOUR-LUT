# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Original additions only; underlying third-party rights remain separate. See LICENSING.md and NOTICE.
"""Preview the flat Film Studio presets without committing every highlight.

The upstream chooser executes SET_VALUE from its superclass selection callback,
and covers the camera with an opaque background/sample picture. Replace only
this app's chooser callback, retain Sony's menu/capture lifecycle, and use the
main looper (the original camera-parameter thread) with a latest-only debounce.
No firmware files, recording profiles, or user's media are touched.
"""
import re
import xml.etree.ElementTree as ET

APP = 'Lcom/sony/imaging/app/pictureeffectplus/'
LAYOUT = APP + 'shooting/layout/PictureEffectPlusOptionMenuLayout;'
HOOK = APP + 'shooting/camera/RicohHook;'
CTRL = APP + 'shooting/camera/PictureEffectPlusController;'
SUPER = 'Lcom/sony/imaging/app/base/menu/layout/SpecialScreenMenuLayout;'
BACKUP = 'Lcom/sony/imaging/app/util/BackUpUtil;'
MOVIE = 'Lcom/sony/imaging/app/base/shooting/movie/MovieShootingExecutor;'
DEBOUNCE_MS = 120


def method(text, signature):
    matches = list(re.finditer(r'^\.method [^\n]* ' + re.escape(signature)
                              + r'\n[\s\S]*?^\.end method', text, re.M))
    if len(matches) != 1:
        raise ValueError('Expected exactly one method: ' + signature)
    return matches[0].group()


def replace(text, signature, body):
    return text.replace(method(text, signature), body, 1)


def prepend(text, signature, instruction):
    old = method(text, signature)
    new, count = re.subn(r'(    \.locals \d+\n)', r'\1' + instruction + '\n', old, count=1)
    if count != 1:
        raise ValueError('Missing locals: ' + signature)
    return text.replace(old, new, 1)


def preview_methods():
    """Smali uses only Android API 10 methods already available to the app."""
    return f'''
.method private beginFilmPreview()V
    .locals 2
    iget-object v0, p0, {LAYOUT}->mFilmHandler:Landroid/os/Handler;
    if-nez v0, :handler_ready
    new-instance v0, Landroid/os/Handler;
    invoke-static {{}}, Landroid/os/Looper;->getMainLooper()Landroid/os/Looper;
    move-result-object v1
    invoke-direct {{v0, v1}}, Landroid/os/Handler;-><init>(Landroid/os/Looper;)V
    iput-object v0, p0, {LAYOUT}->mFilmHandler:Landroid/os/Handler;
    :handler_ready
    invoke-virtual {{v0, p0}}, Landroid/os/Handler;->removeCallbacks(Ljava/lang/Runnable;)V
    iget-object v0, p0, {LAYOUT}->mController:{CTRL}
    invoke-virtual {{v0}}, {CTRL}->getBackupEffectValue()Ljava/lang/String;
    move-result-object v0
    iput-object v0, p0, {LAYOUT}->mFilmOriginal:Ljava/lang/String;
    iput-object v0, p0, {LAYOUT}->mFilmApplied:Ljava/lang/String;
    const/4 v0, 0x0
    iput-boolean v0, p0, {LAYOUT}->mFilmDirty:Z
    const/4 v0, 0x1
    iput-boolean v0, p0, {LAYOUT}->mFilmActive:Z
    return-void
.end method

.method private queueFilmPreview()V
    .locals 3
    iget-object v0, p0, {LAYOUT}->mFilmHandler:Landroid/os/Handler;
    if-eqz v0, :done
    invoke-virtual {{v0, p0}}, Landroid/os/Handler;->removeCallbacks(Ljava/lang/Runnable;)V
    iget-boolean v1, p0, {LAYOUT}->mFilmActive:Z
    if-eqz v1, :done
    invoke-static {{}}, {MOVIE}->isMovieRecording()Z
    move-result v1
    if-nez v1, :done
    const-wide/16 v1, {hex(DEBOUNCE_MS)}
    invoke-virtual {{v0, p0, v1, v2}}, Landroid/os/Handler;->postDelayed(Ljava/lang/Runnable;J)Z
    :done
    return-void
.end method

.method public run()V
    .locals 1
    iget-boolean v0, p0, {LAYOUT}->mFilmActive:Z
    if-eqz v0, :done
    invoke-direct {{p0}}, {LAYOUT}->applyFilmPreview()Z
    :done
    return-void
.end method

.method private applyFilmPreview()Z
    .locals 4
    iget-boolean v0, p0, {LAYOUT}->mFilmActive:Z
    if-eqz v0, :failed
    invoke-static {{}}, {MOVIE}->isMovieRecording()Z
    move-result v0
    if-nez v0, :failed
    iget-object v2, p0, {LAYOUT}->mSelectedItemId:Ljava/lang/String;
    if-eqz v2, :failed
    invoke-static {{v2}}, {HOOK}->isRicohPreset(Ljava/lang/String;)Z
    move-result v0
    if-eqz v0, :failed
    iget-object v0, p0, {LAYOUT}->mFilmApplied:Ljava/lang/String;
    invoke-virtual {{v2, v0}}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    if-nez v0, :success
    const/4 v0, 0x1
    iput-boolean v0, p0, {LAYOUT}->mFilmDirty:Z
    # Mark unknown before the call: a failed matrix/gamma write may be partial.
    const/4 v1, 0x0
    iput-object v1, p0, {LAYOUT}->mFilmApplied:Ljava/lang/String;
    iget-object v0, p0, {LAYOUT}->mController:{CTRL}
    invoke-static {{v0, v1, v2}}, {HOOK}->applyHook({CTRL}Landroid/util/Pair;Ljava/lang/String;)Z
    move-result v3
    if-eqz v3, :restore_failed_preview
    iput-object v2, p0, {LAYOUT}->mFilmApplied:Ljava/lang/String;
    :success
    const/4 v0, 0x1
    return v0
    :restore_failed_preview
    invoke-direct {{p0}}, {LAYOUT}->restoreFilmPreview()V
    invoke-direct {{p0}}, {LAYOUT}->showFilmPreviewError()V
    :failed
    const/4 v0, 0x0
    return v0
.end method

.method private restoreFilmPreview()V
    .locals 4
    invoke-static {{}}, {MOVIE}->isMovieRecording()Z
    move-result v0
    if-nez v0, :done
    iget-boolean v0, p0, {LAYOUT}->mFilmDirty:Z
    if-eqz v0, :done
    iget-object v2, p0, {LAYOUT}->mFilmOriginal:Ljava/lang/String;
    if-eqz v2, :done
    iget-object v0, p0, {LAYOUT}->mFilmApplied:Ljava/lang/String;
    invoke-virtual {{v2, v0}}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    if-nez v0, :done
    iget-object v0, p0, {LAYOUT}->mController:{CTRL}
    const/4 v1, 0x0
    invoke-static {{v0, v1, v2}}, {HOOK}->applyHook({CTRL}Landroid/util/Pair;Ljava/lang/String;)Z
    move-result v3
    if-eqz v3, :restore_failed
    iput-object v2, p0, {LAYOUT}->mFilmApplied:Ljava/lang/String;
    goto :done
    :restore_failed
    const-string v0, "FilmPreview"
    const-string v1, "Could not restore committed filter; it remains selected for next camera initialization"
    invoke-static {{v0, v1}}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;)I
    :done
    return-void
.end method

.method private endFilmPreview()V
    .locals 1
    const/4 v0, 0x0
    iput-boolean v0, p0, {LAYOUT}->mFilmActive:Z
    iget-object v0, p0, {LAYOUT}->mFilmHandler:Landroid/os/Handler;
    if-eqz v0, :restore
    invoke-virtual {{v0, p0}}, Landroid/os/Handler;->removeCallbacks(Ljava/lang/Runnable;)V
    :restore
    invoke-direct {{p0}}, {LAYOUT}->restoreFilmPreview()V
    return-void
.end method

.method private showFilmPreviewError()V
    .locals 2
    iget-object v0, p0, {LAYOUT}->mGuideTextView:Landroid/widget/TextView;
    if-eqz v0, :done
    const-string v1, "\u9884\u89c8\u672a\u751f\u6548\uff0c\u8bf7\u91cd\u8bd5\u6216 MENU \u8fd4\u56de"
    invoke-virtual {{v0, v1}}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V
    :done
    return-void
.end method

.method private prepareFilmPreviewView()V
    .locals 3
    iget-object v0, p0, {LAYOUT}->mCurrentView:Landroid/view/ViewGroup;
    const/4 v1, 0x0
    invoke-virtual {{v0, v1}}, Landroid/view/ViewGroup;->setBackgroundResource(I)V
    iget-object v0, p0, {LAYOUT}->mBackgroundImageView:Landroid/widget/ImageView;
    invoke-direct {{p0, v0}}, {LAYOUT}->releaseImageViewDrawable(Landroid/widget/ImageView;)V
    const/16 v1, 0x8
    invoke-virtual {{v0, v1}}, Landroid/widget/ImageView;->setVisibility(I)V
    # Leave the 122 px icon column and Sony footer intact, expose the live image.
    iget-object v0, p0, {LAYOUT}->mGuideTextView:Landroid/widget/TextView;
    invoke-virtual {{v0}}, Landroid/widget/TextView;->getLayoutParams()Landroid/view/ViewGroup$LayoutParams;
    move-result-object v1
    check-cast v1, Landroid/widget/RelativeLayout$LayoutParams;
    const/16 v2, 0x16d
    iput v2, v1, Landroid/widget/RelativeLayout$LayoutParams;->topMargin:I
    const/16 v2, 0x2d
    iput v2, v1, Landroid/widget/RelativeLayout$LayoutParams;->height:I
    invoke-virtual {{v0, v1}}, Landroid/widget/TextView;->setLayoutParams(Landroid/view/ViewGroup$LayoutParams;)V
    const/4 v1, 0x1
    invoke-virtual {{v0, v1}}, Landroid/widget/TextView;->setSingleLine(Z)V
    const v1, -0x78000000
    invoke-virtual {{v0, v1}}, Landroid/widget/TextView;->setBackgroundColor(I)V
    const-string v1, "\u5207\u6362\u9884\u89c8 \u00b7 \u4e2d\u5fc3\u786e\u8ba4 \u00b7 MENU \u8fd4\u56de"
    invoke-virtual {{v0, v1}}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V
    return-void
.end method
'''


def patch_live_preview(base, profiles):
    # This replacement deliberately supports the flat filter browser only.
    rows = next(e for e in ET.parse(base / 'assets/MenuData.xml').iter()
                if e.get('ItemId') == 'ApplicationTop')
    if [e.get('ItemId') for e in rows] != [p['id'] for p in profiles] or any(list(e) for e in rows):
        raise ValueError('Live preview requires the flat, ordered Film Studio filter menu')
    path = base / 'smali' / (LAYOUT[1:-1] + '.smali')
    text = path.read_text()
    if '.implements Ljava/lang/Runnable;' in text or 'beginFilmPreview()V' in text:
        raise ValueError('Live preview patch already present')
    text = text.replace('.source "PictureEffectPlusOptionMenuLayout.java"',
                        '.source "PictureEffectPlusOptionMenuLayout.java"\n.implements Ljava/lang/Runnable;')
    fields = '''.field private mFilmHandler:Landroid/os/Handler;
.field private mFilmActive:Z
.field private mFilmDirty:Z
.field private mFilmOriginal:Ljava/lang/String;
.field private mFilmApplied:Ljava/lang/String;
'''
    text = text.replace('# instance fields\n', '# instance fields\n' + fields, 1)

    # Avoid both loading a large sample bitmap and writing camera settings from
    # SpecialScreenMenuLayout.onItemSelected on every scroll event.
    signature = 'onItemSelected(Lcom/sony/imaging/app/base/menu/layout/SpecialScreenView;Landroid/view/View;IJ)V'
    text = replace(text, signature, f'''.method public {signature}
    .locals 3
    invoke-virtual {{p1, p3}}, Lcom/sony/imaging/app/base/menu/layout/SpecialScreenView;->getItemAtPosition(I)Ljava/lang/Object;
    move-result-object v0
    check-cast v0, Ljava/lang/String;
    iput-object v0, p0, {LAYOUT}->mSelectedItemId:Ljava/lang/String;
    iget-object v1, p0, {LAYOUT}->mService:Lcom/sony/imaging/app/base/menu/BaseMenuService;
    invoke-virtual {{v1, v0}}, Lcom/sony/imaging/app/base/menu/BaseMenuService;->getMenuItemText(Ljava/lang/String;)Ljava/lang/CharSequence;
    move-result-object v1
    iget-object v2, p0, {LAYOUT}->mItemNameView:Landroid/widget/TextView;
    invoke-virtual {{v2, v1}}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V
    iget-object v1, p0, {LAYOUT}->mGuideTextView:Landroid/widget/TextView;
    const-string v2, "\u5207\u6362\u9884\u89c8 \u00b7 \u4e2d\u5fc3\u786e\u8ba4 \u00b7 MENU \u8fd4\u56de"
    invoke-virtual {{v1, v2}}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V
    invoke-direct {{p0}}, {LAYOUT}->queueFilmPreview()V
    iget-object v0, p0, {LAYOUT}->mViewArea:Lcom/sony/imaging/app/base/menu/layout/SpecialScreenArea;
    invoke-virtual {{v0}}, Lcom/sony/imaging/app/base/menu/layout/SpecialScreenArea;->update()V
    return-void
.end method''')

    signature = 'onResume()V'
    resume = method(text, signature)
    needle = f'    invoke-super {{p0}}, {SUPER}->onResume()V'
    assert resume.count(needle) == 1
    resume = resume.replace(needle, f'    invoke-direct {{p0}}, {LAYOUT}->beginFilmPreview()V\n' + needle)
    # Remove the complete old sample draw sequence, not just setBackgroundResource.
    start = f'    iget-object v0, p0, {LAYOUT}->mBackgroundImageView:Landroid/widget/ImageView;'
    end = '    invoke-virtual {v0, v1}, Landroid/widget/ImageView;->setBackgroundResource(I)V'
    begin, finish = resume.index(start), resume.index(end) + len(end)
    resume = resume[:begin] + resume[finish:]
    resume = resume.replace('    return-void',
                            f'    invoke-direct {{p0}}, {LAYOUT}->prepareFilmPreviewView()V\n    return-void')
    text = replace(text, signature, resume)

    text = replace(text, 'pushedCenterKey()I', f'''.method public pushedCenterKey()I
    .locals 4
    iget-object v0, p0, {LAYOUT}->mFilmHandler:Landroid/os/Handler;
    if-eqz v0, :done
    invoke-virtual {{v0, p0}}, Landroid/os/Handler;->removeCallbacks(Ljava/lang/Runnable;)V
    # Flush the actual highlighted item even if ENTER arrives inside 120 ms.
    invoke-direct {{p0}}, {LAYOUT}->applyFilmPreview()Z
    move-result v0
    if-eqz v0, :done
    :try_start
    invoke-static {{}}, {BACKUP}->getInstance(){BACKUP}
    move-result-object v0
    const-string v1, "ID_PICTUREEFFECTPLUS_CURRENT_EFFECT"
    iget-object v2, p0, {LAYOUT}->mSelectedItemId:Ljava/lang/String;
    invoke-virtual {{v0, v1, v2}}, {BACKUP}->setPreference(Ljava/lang/String;Ljava/lang/Object;)Z
    move-result v3
    :try_end
    .catch Ljava/lang/Throwable; {{:try_start .. :try_end}} :save_exception
    if-eqz v3, :save_failed
    iput-object v2, p0, {LAYOUT}->mFilmOriginal:Ljava/lang/String;
    iput-object v2, p0, {LAYOUT}->mPreviousSelectedeffect:Ljava/lang/String;
    const/4 v0, 0x0
    invoke-virtual {{p0, v0}}, {LAYOUT}->closeMenuLayout(Landroid/os/Bundle;)V
    :done
    const/4 v0, 0x1
    return v0
    :save_exception
    move-exception v0
    :save_failed
    invoke-direct {{p0}}, {LAYOUT}->restoreFilmPreview()V
    invoke-direct {{p0}}, {LAYOUT}->showFilmPreviewError()V
    goto :done
.end method''')

    text = replace(text, 'pushedMenuKey()I', f'''.method public pushedMenuKey()I
    .locals 1
    invoke-direct {{p0}}, {LAYOUT}->endFilmPreview()V
    iget-object v0, p0, {LAYOUT}->mLastItemId:Lcom/sony/imaging/app/base/menu/HistoryItem;
    if-nez v0, :previous
    invoke-virtual {{p0}}, {LAYOUT}->closeLayout()V
    goto :done
    :previous
    invoke-virtual {{p0}}, {LAYOUT}->openPreviousMenu()V
    :done
    const/4 v0, 0x1
    return v0
.end method''')
    for sig in ('closeLayout()V', 'onPause()V'):
        text = prepend(text, sig, f'    invoke-direct {{p0}}, {LAYOUT}->endFilmPreview()V')
    # S1, MOVIE, playback, media removal and mode changes use this entry point;
    # restoring before the original close also precedes forwarding the key.
    assert ' closeMenuLayout(Landroid/os/Bundle;)V\n' not in text
    text += f'''
.method public closeMenuLayout(Landroid/os/Bundle;)V
    .locals 0
    invoke-direct {{p0}}, {LAYOUT}->endFilmPreview()V
    invoke-super {{p0, p1}}, {SUPER}->closeMenuLayout(Landroid/os/Bundle;)V
    return-void
.end method
'''
    text += preview_methods()
    # Converted ENTER keys otherwise inherit KeyReceiver's no-op. Route any
    # legacy/touch item-click callback through the same verified commit path.
    for name in ('pushedEnter5WayFuncKey', 'pushedEnterJoyStickFuncKey'):
        assert f' {name}()I\n' not in text
        text += f'''
.method public {name}()I
    .locals 1
    invoke-virtual {{p0}}, {LAYOUT}->pushedCenterKey()I
    move-result v0
    return v0
.end method
'''
    assert ' doItemClickProcessing(Ljava/lang/String;)V\n' not in text
    text += f'''
.method protected doItemClickProcessing(Ljava/lang/String;)V
    .locals 0
    iput-object p1, p0, {LAYOUT}->mSelectedItemId:Ljava/lang/String;
    invoke-virtual {{p0}}, {LAYOUT}->pushedCenterKey()I
    return-void
.end method
'''
    path.write_text(text)
    # The upstream adapter loads exactly the same drawable twice; the first
    # result is discarded. Keep the existing cached adapter and one lookup.
    adapter = path.with_name(path.stem + '$PictureEffectSpecialBaseMenuAdapter.smali')
    source = adapter.read_text()
    lookup = '    invoke-virtual {v2, v1}, Lcom/sony/imaging/app/base/menu/BaseMenuService;->getMenuItemDrawable(Ljava/lang/String;)Landroid/graphics/drawable/Drawable;'
    assert source.count(lookup) == 2
    source = source.replace(lookup, '', 1)
    adapter.write_text(source)
