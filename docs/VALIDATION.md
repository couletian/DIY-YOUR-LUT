# 验证范围 / Validation / 検証範囲

[中文](../README.md) · [English](../README.en.md) · [日本語](../README.ja.md)

## 实机记录 / Device evidence / 実機記録

Device: one Sony a5100 / ILCE-5100, firmware 1.10, Android 2.3.7 / API 10. These observations do not establish compatibility with other bodies or firmware.

| Version | 中文 | English | 日本語 |
| --- | --- | --- | --- |
| 0.1.1 / 0.1b | 10 个滤镜切换，照片与一段黑白视频保存验证 | Ten selections applied; JPEGs and one monochrome clip inspected | 10種類の切り替え、JPEG と白黒動画1本を確認 |
| 0.1.2 / 0.1c | 录像格式／画质菜单获用户确认 | User confirmed movie format/quality controls | 動画形式・画質メニューの操作を利用者が確認 |
| 0.1.3 / 0.1d | 安装、启动、默认风格成功；新操作获用户总体确认 | Install, startup and default look verified; general user confirmation of new controls | 導入・起動・初期フィルターを確認。新操作について利用者の総合的確認あり |

**0.1b saved-output measurements / 已保存文件检查 / 保存ファイルの確認：**

- PROVIA JPEG: 6000 × 4000, color present.
- ACROS JPEG: 6000 × 4000, decoded R = G = B at every pixel.
- ACROS movie: XAVC S, H.264, 1920 × 1080, 60000/1001 fps (~59.94), duration 8.5085 s; stereo PCM at 48 kHz.
- Full audio/video decode passed. Nine 1 fps samples, resized to 320 × 180 and decoded as RGB24, were achromatic at every sampled pixel. This does not test every full-resolution frame for neutrality or assess audio quality by listening.

中文：上述视频证明黑白处理进入了保存的视频；不证明色彩精确匹配富士 ACROS。0.1b 的素材结果不能当作 0.1d 所有滤镜、强度、格式组合的逐项验证。应用内回放只列出照片，视频须在原机对应格式的回放模式查看。未公开原始素材、设备日志或私人拍摄信息。

English: The clip demonstrates that monochrome processing reached saved video, not that it matches Fujifilm ACROS accurately. The 0.1b evidence is not an exhaustive 0.1d look/strength/format test. In-app playback lists stills; use the corresponding native movie view for video. Private captures, device logs and personal recording metadata are not published.

日本語：この動画は白黒処理が保存映像に反映された証拠であり、富士フイルム ACROS との正確な一致を示すものではありません。0.1b の結果は、0.1d の全組み合わせを確認したことにはなりません。アプリ内再生は写真のみで、動画は標準の対応形式の再生画面で確認します。個人の素材、機器ログ、撮影情報は公開しません。

## 0.3.0-alpha / 本地开发版 / Local development / ローカル開発版

中文：0.3.0（机内显示 `0.3a`）目前为本地开发版本，未发布。新增选择页实时取景、停留预览、中心键确认和返回恢复；15 个滤镜使用不同的字母／颜色图标。快速选择会取消上一次尚未执行的预览，等待 120 ms 后仅应用最后一项；确认时立即处理当前项，应用失败不提交该选择。关闭或暂停菜单会取消待执行预览，并尝试恢复进入菜单时已确认的滤镜。**这些菜单生命周期、实机画面、拍照／录像保存与响应耗时仍未验证；120 ms 不是实测延迟。**

English: 0.3.0 (on-camera `0.3a`) is a local, unpublished development build. It adds live camera view while browsing, preview on highlight, center confirmation, cancellation restore, and fifteen distinct color/letter badges. Rapid selections cancel pending preview work and apply only the latest choice after 120 ms; confirmation flushes the current choice immediately and does not commit a failed application. Closing or pausing the browser cancels queued preview work and attempts to restore the look committed before entry. **Menu lifecycle behavior, the actual camera display, saved photographs/video and response times remain unverified. The 120 ms setting is not measured latency.**

日本語：0.3.0（カメラ内表示 `0.3a`）は未公開のローカル開発版です。一覧中のライブビュー、選択項目のプレビュー、中央ボタンでの確定、キャンセル時の復帰、15種類の色・略称アイコンを追加します。連続操作では未実行のプレビューを取り消し、120 ms後に最後の項目だけを適用します。確定時は現在の項目をすぐ処理し、適用に失敗した選択は保存しません。メニュー終了・一時停止時に予約処理を取り消し、開く前の確定済みフィルターへの復帰を試みます。**メニューの動作、実際の画面、写真／動画保存、応答時間は実機未検証です。120 msは実測の遅延ではありません。**

中文：参数改为按「滤镜＋强度」分别初始化，共 60 个独立数据类。首次选用只创建该组合的两个数组（矩阵和曲线，净数据 2,084 字节），避免在 `RicohHook` 初始化时创建全部 120 个数组（净数据 125,040 字节）；此字节数不包括对象、类或运行时开销。菜单可用性检查只识别 ID，不触发数据加载。全部既有色彩参数保留，生成数组已与公开 0.2.0 的 120 个编译数组逐项比较。最终签名 APK 已重新解码，全部 120 个数组与 0.2.0 逐项一致，15 个图标链接与资源、685 个签名条目及相同签名证书检查通过；生成代码的 11 项预览控制流程检查通过。**没有实机启动时间或提速百分比结论。**

English: Parameters initialize separately for each look/strength pair in 60 holder classes. First selection creates two arrays for that pair (matrix and curve, 2,084 payload bytes), instead of initializing all 120 arrays in `RicohHook` (125,040 payload bytes). These counts exclude object, class and runtime overhead. Menu availability checks recognize IDs without loading the arrays. Existing color parameters are retained; generated arrays were compared exactly against all 120 compiled arrays in published 0.2.0. The final signed APK was decoded again: all 120 arrays exactly match 0.2.0; all 15 badge links/resources, 685 signed entries and the unchanged signing certificate passed checks. Eleven emitted-code preview control-flow checks passed. **There is no hardware startup-time measurement or percentage-speedup claim.**

日本語：「フィルター＋強度」ごとに60個の独立したクラスでパラメータを初期化します。初回選択でその組み合わせの行列とカーブの2配列（データ部分2,084バイト）を作り、`RicohHook`で全120配列（同125,040バイト）を一括初期化しません。オブジェクト、クラス、実行環境の管理領域はこの数に含みません。メニューの利用可否判定はIDだけを確認し、配列を読み込みません。既存の色パラメータを維持し、生成配列を公開0.2.0の全120配列と照合しました。最終署名APKを再展開し、全120配列の0.2.0との完全一致、15種類のアイコン参照とリソース、685署名項目、同一署名証明書を確認しました。生成コードのプレビュー制御フロー11項目も検査済みです。**起動時間の実測や高速化率の主張はありません。**

Before a camera-tested release, check still preview and movie standby separately: rapid movement followed by center; MENU/back and half-shutter cancellation; leaving and reopening the browser; preview-application failure; saved JPEGs and movies with the confirmed look; and cold/warm startup timing. Preserve private captures locally; do not attach them to public reports by default.

## 0.2.0-alpha / 胶片工坊 / Film Studio

`FilmStudio-0.2.0-alpha-movie.apk` — SHA-256:

```text
88632d187f75c6560c2b67b64d9de9774226d8a78fd7ba3330270493e8b0ad2a
```

中文：本版把应用名改为「胶片工坊」，合并 10 个富士参考风格与 5 个上游理光／街头风格。对最终签名 APK 重新反编译后，核对了全部 120 组数组（15 风格 × 4 强度 × 矩阵／Gamma）、菜单与查询映射。与 0.1.3 比较，原有 80 组富士数组逐项一致；新增理光 100% 参数与固定版本上游一致。曲线边界、强度端点、684 个签名条目、同一签名证书及包内许可检查通过。相机内版本名为 `0.2a`，包名不变。**实机覆盖安装显示 Success，启动成功，已安装版本读回为 0.2a。运行日志观察到原有富士风格及理光正片、负片、高反差黑白、森山风的参数应用成功；正负逆冲仅有静态检查。尚未验证本版照片／录像保存、全部强度或录像待机下的全部切换，也未做新色彩校准。**

English: The app is renamed 胶片工坊 / Film Studio and combines ten Fujifilm-reference with five upstream Ricoh/street presets. Round-trip decompilation of the final signed APK verified all 120 arrays (15 looks × 4 strengths × matrix/gamma), menu IDs and lookups. All 80 existing Fujifilm arrays match 0.1.3 exactly; Ricoh at 100% matches the pinned upstream. Curve bounds, strength endpoints, 684 signed entries, the retained certificate and bundled legal files passed. The on-camera version is `0.2a`; the package is unchanged. **The in-place camera update returned Success, the app launched, and the installed version read back as 0.2a. Runtime logs showed successful application of existing Fujifilm profiles and Ricoh Positive, Negative, High Contrast B&W and Moriyama; Cross Process has only static checks. Saved photographs/video, all strengths and all movie-standby transitions remain unverified for this version. No new color calibration was performed.**

日本語：アプリ名を「胶片工坊 / Film Studio」に変更し、富士参照10種と上流リコー／ストリート風5種を統合。最終署名 APK を再展開し、120配列（15種類 × 4強度 × 行列／Gamma）、メニューと参照処理を確認しました。既存の富士80配列は0.1.3と完全一致し、リコー100%も指定版の上流と一致します。カーブ範囲、強度端点、684署名項目、継続する署名証明書、同梱ライセンスを確認。カメラ内表示は `0.2a`、パッケージ名は維持しています。**実機の上書き更新は Success、起動成功、インストール済み版は0.2aと確認しました。既存の富士参照と、リコーのポジ・ネガ・高反差白黒・森山風で適用成功ログを確認。クロスプロセスは静的検証のみです。本版の写真／動画保存、全強度、動画待機中の全切り替えは未検証で、新たな色彩校正も行っていません。**

## 0.1.3-alpha 发布 APK / Previous release / 旧公開 APK

`FujiStyle-0.1.3-alpha-movie.apk` — SHA-256:

```text
5757a59a5ce9983a2294a18bf120235c43a490a1eda1b1345d112a3369b1a1ef
```

中文：发行打包只新增 `assets/legal/` 下的4份许可／来源文件。与原先实机验证的 APK 比较，全部原有代码、资源与其他非签名条目字节一致，签名证书相同；684个条目的完整性、清单摘要及 APK 签名验证通过。此补充许可证后的文件没有再次安装到相机，因此不把它描述为新的全流程实机验证。Releases 附有 `RELEASE-VERIFICATION.json` 和 `SHA256SUMS.txt`。

English: Release packaging adds four license/attribution files under `assets/legal/`. All original code, resources and other non-signature entries are byte-identical to the previously camera-tested APK, and the signing certificate is unchanged. Integrity, manifest digests and signature checks passed for 684 entries. This repacked file was not reinstalled on the camera, so it is not a new end-to-end hardware test. Releases include `RELEASE-VERIFICATION.json` and `SHA256SUMS.txt`.

日本語：公開用のパッケージには `assets/legal/` のライセンス・出典4ファイルだけを追加しています。実機確認済み APK の既存コード、リソース、その他の非署名エントリーはすべてバイト単位で一致し、署名証明書も同じです。684エントリーの整合性、マニフェストのダイジェスト、署名を検証しました。この再梱包ファイルは実機へ再インストールしていないため、新たな実機全工程検証とは扱いません。Releases に `RELEASE-VERIFICATION.json` と `SHA256SUMS.txt` を添付します。

## 数值近似 / Numerical approximation / 数値的な近似

The fit uses paired official LUT samples with an uncalibrated WDR-709 neutral proxy. Fixed random seed: 5100. Training points after clipping exclusions: 75,866; independent validation points: 22,760. Errors below are pooled absolute RGB-channel errors on a normalized 0–1 output scale, **not ΔE, a percentage match, or measured a5100 color accuracy**.

| Look | Mean absolute error | 95th percentile absolute error |
| --- | ---: | ---: |
| PROVIA | 0.0650 | 0.2278 |
| Velvia | 0.0629 | 0.2373 |
| ASTIA | 0.0663 | 0.2333 |
| CLASSIC CHROME | 0.0811 | 0.2287 |
| REALA ACE | 0.1254 | 0.3185 |
| PRO Neg. Std | 0.0726 | 0.2223 |
| CLASSIC Neg. | 0.0802 | 0.2514 |
| ETERNA | 0.0784 | 0.2074 |
| ETERNA BLEACH BYPASS | 0.0808 | 0.2068 |
| ACROS | 0.1037 | 0.2548 |

中文：训练和验证样本相互独立，均取自官方中性 LUT 的未剪裁区间。误差是在 0–1 的 RGB 数值上计算的绝对误差，不是“相似度百分比”或实拍 ΔE。部分颜色误差明显，REALA ACE 的平均误差尤其较大。3×3 行列与共同明暗曲线无法完整表达复杂 LUT；索尼处理顺序和传递函数也未做实测标定。

English: Independent training and validation use the unclipped region of the neutral LUT. Some colors have substantial errors, particularly the mean error for REALA ACE. A 3×3 matrix and one common tone curve cannot reproduce the complete nonlinear LUT. Sony's processing order and transfer functions have not been measured and calibrated.

日本語：学習と検証には独立した標本を用い、中性 LUT のクリップされていない領域を評価しています。表は 0–1 の RGB 絶対誤差であり、一致率や実写の ΔE ではありません。特に REALA ACE の平均誤差など、無視できない差があります。3×3 行列と共通カーブでは複雑な LUT を完全には表現できず、ソニー側の処理順序や伝達特性も未校正です。

## 本地检查 / Local checks / ローカル検査

Optional compiled-payload regression check after decompiling the signed APK:

```sh
java -jar inputs/apktool.jar d -r output/FilmStudio-0.3.0-alpha-movie.apk -o build-local/verify-030
python tools/check_combined.py --decoded build-local/verify-030 --upstream-hook inputs/upstream/src/smali/RicohHook.smali
python tools/check_live_preview.py build-local/verify-030
python -m unittest discover -s tools -p test_filter_icons.py --previous-decoded PATH_TO_DECODED_020
```

Use a fresh verification directory. Replace `PATH_TO_DECODED_020` with a separately decoded released 0.2.0 APK to compare all 120 arrays. If that reference is unavailable, omit `--previous-decoded`; the check still compares the final holder arrays against the local fitted profiles and pinned Ricoh source. A decoded 0.1.3 reference is also accepted for the eighty earlier Fujifilm arrays. These checks also reject eager initialization in the hook or preset-availability lookup and verify each holder/reference pair. They read local files and do not connect to the camera.


After completing the rights and input steps in the [installation guide](INSTALL.en.md):

```sh
python tools/check_strength.py
python tools/check_build.py
```

Run these after a local build, which creates `profiles/film_studio.json` from the existing fitted profiles and pinned upstream hook. They do not connect to the camera. They verify:

- Fifteen profiles, four strengths, 3×3 dimensions, 1024-point monotonic curves and 10-bit bounds. Neutral rows remain neutral; intentional Ricoh tints retain their original row sums at 100%.
- A bit-identical 100% endpoint and mathematical 0% identity endpoint; 0% is not an app menu choice.
- `.cube` red/green/blue ordering and exported-grid round trips.
- APK archive integrity, file and manifest digests, and the detached signature against the embedded certificate. This is integrity checking, not trust in the signer or proof of device compatibility.

中文：参数强度检查保证 100% 保持原值、数学上的 0% 为恒等变换、曲线单调且不超界。APK 校验检查归档与签名完整性，不证明签名者可信、应用安全或能在其他相机运行。

日本語：強度検査では100%の一致、数学上の0%の恒等変換、カーブの単調性と範囲を確認します。APK 検査はアーカイブ・署名の整合性を調べるもので、署名者の信頼性、安全性、他機種での動作を保証しません。

For optional inspection of your own selected captures, install `requirements-media.txt` and separately install FFmpeg/ffprobe. The capture checker reads only the files you specify:

```sh
python -m pip install -r requirements-media.txt
python tools/verify_capture.py --provia YOUR_PROVIA.JPG --acros YOUR_ACROS.JPG --movie YOUR_ACROS.MP4 --output validation/my-capture-check.json
```

中文：将示例文件名替换为自己选定的测试素材。生成的报告可能含文件名和 EXIF 时间；仅供本地检查，公开前须去除私人信息。需要 Pillow、FFmpeg 和 ffprobe，这些不是构建 APK 的必需工具。

日本語：ファイル名を自分で選んだテスト素材に置き換えてください。レポートにはファイル名や EXIF 時刻が含まれるため、公開前に個人情報を削除します。Pillow、FFmpeg、ffprobe は素材検査用で、APK のビルドには不要です。

Still unverified / 尚未验证 / 未検証：all encoded format × look × strength combinations; other camera models; long recording reliability; RAW image-data changes; colorimetric matching; thermal and battery behavior under extended use. Re-test your intended settings before important shooting.
