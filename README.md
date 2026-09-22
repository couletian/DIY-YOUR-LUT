#DIY YOUR LUT
Building on the “sony-a5100-film-studio” project, this skill gives people the ability to customize their own LUTs and import them into an existing Film Studio installation package.

This branch implements LUT DIY by building a visual LUT adjuster that can also import local images for preview in advance, and export custom LUTs into the existing “Film Studio” APK. This feature has been integrated into a skill tool that can be directly invoked by AI—“camera-lut-studio”.


# 胶片工坊 / Film Studio


**中文** · [English](README.en.md) · [日本語](README.ja.md)

面向 **Sony a5100 / ILCE-5100** 的非官方胶片风格实验工具。参考 [bonyback1 的 Ricoh 模组](https://github.com/bonyback1/sony-pmca-ricoh-mod) 的硬件色彩处理方法，并以 [富士公开的 GFX ETERNA 55 LUT](https://www.fujifilm-x.com/global/support/download/lut/) 为色彩研究参考，提供照片与实验性录像效果。

**已发布版本：0.3.0-alpha（机内 0.3a）。** 应用名称为「胶片工坊」，文档提供三种语言，当前相机应用界面主要为中文。本次更新增加切换预览、按需加载和不同滤镜图标，已获得 a5100 用户的实机总体确认。

**0.2.0 更名为「胶片工坊」，合并 10 个富士参考风格与 5 个上游理光／街头风格，共 15 个。** 相机菜单以「富士」「理光」前缀区分。包名与签名沿用旧版「富士风格」，可覆盖更新；原有色彩参数保持不变。旧版 [0.2.0-alpha](https://github.com/ukiki0718-netizen/sony-a5100-film-studio/releases/tag/v0.2.0-alpha) 和 [0.1.3-alpha](https://github.com/ukiki0718-netizen/sony-a5100-film-studio/releases/tag/v0.1.3-alpha) 仍保留供回退。

<a id="compatibility"></a>

## 机型兼容性

**目前只有 a5100 经过本项目实机验证，不是所有索尼相机都能使用。**

| 机型 | 本项目状态 |
| --- | --- |
| **a5100 / ILCE-5100，固件 1.10** | 已实测；具体功能和版本范围见下方验证记录 |
| a6000、a6300、a6500 | 上游列出的 PMCA 候选机型；本版本未实测 |
| a7、a7R、a7S、a7 II、a7R II、a7S II | 上游列出的 PMCA 候选机型；本版本未实测 |
| RX100 III／IV／V、RX10 II／III、RX1R II、HX90 | 上游列出的 PMCA 候选机型；本版本未实测 |
| a6400、a6700、a7 III、a7C | 不支持本应用依赖的 PlayMemories Camera Apps 安装方式 |
| 其他型号或固件 | 尚未评估，不能从相近型号推定兼容 |

候选名单依据[上游项目的机型说明](https://github.com/bonyback1/sony-pmca-ricoh-mod/blob/7c565898562c73c5073c54dfc831c8c3df9c24cf/README.md)，不是本项目新增录像、强度功能的测试结果。PMCA 是本应用依赖的机内应用平台；仅有 MTP 或手机遥控功能不代表支持它。

**录像菜单目前按 a5100 的规格编写，没有提供 4K 选项。** 不承诺在其他机型上开放其全部原生格式、帧率和码率。即使安装成功，也需分别确认取景、滤镜切换、JPEG 保存、录像开始／停止及文件回放，以及退出后的色彩恢复；不同机型的实际色彩也可能不同。反馈请附型号、固件、应用版本及具体测试项目。

## 下载与安装

**[直接下载 APK：0.3.0-alpha](https://github.com/ukiki0718-netizen/sony-a5100-film-studio/releases/download/v0.3.0-alpha/FilmStudio-0.3.0-alpha-movie.apk)** · [发行说明与校验文件](https://github.com/ukiki0718-netizen/sony-a5100-film-studio/releases/tag/v0.3.0-alpha)

下载 `FilmStudio-0.3.0-alpha-movie.apk` 后，按照[中文安装教程](docs/INSTALL.zh-CN.md)连接相机并安装，无需自己编译。**Code → Download ZIP 是源码，不是安装包。**

本发行版为非官方实验版本，仅有上文所列的 a5100 实机验证。APK 包含 Sony 基础应用内容和由富士公开 LUT 拟合出的参数；未确认针对这些第三方材料改编、再分发的独立授权。发布不表示获得 Sony 或 FUJIFILM 许可，也不保证免责；[版权与许可范围](LICENSING.md)单独说明各部分的权利。官方原始 LUT 和签名私钥不提供下载。

→ **[中文完整安装教程](docs/INSTALL.zh-CN.md)**：准备输入 → 本地构建 → 首次启用连接 → Wi-Fi ADB 安装 → 相机操作 → 更新与故障排查。

下载 APK 后，在文件所在目录运行以下命令（相机须已启用 Wi-Fi ADB）：

```sh
adb connect CAMERA_IP:5555
adb -s CAMERA_IP:5555 install -r FilmStudio-0.3.0-alpha-movie.apk
```

**IP 与隐私：** `CAMERA_IP` 只是占位符，必须替换为你自己的相机在 Tweak → Developer 中当前显示的 IP；不要原样输入，也不要照抄他人的地址。保留后面的 `:5555` 端口。公开教程使用占位符；分享截图或日志时，请遮住或删除真实 IP。

首次安装还需要教程中的准备步骤。

### 拿到 APK 后还要自己编译吗？

**不需要。已签名 APK 可以通过教程中的安装方式直接安装，能否运行仍取决于机型和环境。** 接收者不需要 Python、Java、Apktool 或签名私钥。只有自行修改和生成 APK 时，才需要本地构建章节；自行构建也不会自动解决第三方许可问题。

## 0.3.0 的变化

- 滤镜选择页保留相机实时取景。用方向键或拨轮移动到滤镜后，停留片刻即可预览；中心键确认，返回／取消恢复打开列表前的滤镜。请先确认，再拍照或按 MOVIE。
- 快速浏览时只应用最后停留的选择；代码设置了 120 ms 的等待，用于减少连续写入。这不是实机响应时间的保证。
- 15 个滤镜分别使用带字母缩写和颜色的图标，方便辨认；图标不是实拍效果样张。
- 按首次选用的「滤镜＋强度」加载矩阵与曲线，之后复用，避免启动时一次初始化全部组合。原有 15 个滤镜、四档强度的色彩参数保持不变。

**本次界面更新已获 a5100 用户实机总体确认。** 覆盖安装、启动和 15 个滤镜参数应用均有成功记录。预览、取消恢复、图标和操作流畅度检查后，用户反馈实机检测没有问题；未测量启动／切换耗时，也未逐项检验本版所有照片／录像保存组合。

## 功能

- 10 种富士官方 LUT 参考风格：PROVIA、Velvia、ASTIA、CLASSIC CHROME、REALA ACE、PRO Neg. Std、CLASSIC Neg.、ETERNA、ETERNA BLEACH BYPASS、ACROS。
- 5 种上游理光／街头风格：GR 正片、负片、高反差黑白、森山风、正负逆冲。来自社区模组，非理光官方 LUT。
- 拍照及录像待机时，按中心键进入滤镜选择。
- MENU 首页 →「滤镜强度」：**30% / 50% / 70% / 100%**。初始为 100%，拍照与录像共用，正常退出后保存选择。
- MENU 首页 →「拍照／录像模式」→ 动态影像 P/A/S/M，再设置「录像文件格式」及「录像帧率／画质」。显示相机支持的 XAVC S / AVCHD / MP4 组合，不强行开放另一 PAL/NTSC 制式。
- 按 MOVIE 开始／停止录像；录制过程中固定滤镜与强度。
- MENU 第 4 页可调整白平衡。滤镜以 STD 标准、对比度/饱和度/锐度为 0 作为基础，应用内不叠加原机人像、鲜艳等创意风格。
- 独立包名 `com.yuki.imaging.app.pictureeffectplus`，可与原 Ricoh 模组共存。

人像可先比较 30% 与 50%。强度减弱颜色矩阵和明暗曲线，并不识别人脸或自动校正肤色。**ACROS、理光高反差黑白和森山风在低于 100% 时会保留部分颜色；纯黑白请选 100%。**

## 已验证范围与限制

仅在一台 **a5100、固件 1.10、Android 2.3.7 / API 10** 上测试，不承诺其他机型兼容。

- 0.1.1：10 个风格菜单成功切换；PROVIA 彩色与 ACROS 黑白 JPEG 正常保存；ACROS XAVC S 1080p59.94 视频成功保存并完整解码。
- 0.1.2：录像格式和画质菜单获得用户可用性确认；尚未逐一分析所有格式生成的文件。
- 0.1.3：安装、启动及默认滤镜应用已验证，中心键与强度操作得到用户总体确认；未逐一检验每种风格、强度、录像格式的最终文件。
- 0.2.0：合并版安装、启动及部分滤镜参数应用成功；照片／录像保存仍限于历史验证范围。
- 0.3.0：覆盖安装、启动及 15 个滤镜参数应用成功；本次预览、取消恢复、图标和流畅度更新获用户实机总体确认。未测量耗时，也未逐项验证所有保存组合。

**应用内回放目前只显示照片。** 查看录像请退出应用，进入原机回放，并选择与文件对应的 XAVC S / AVCHD / MP4 观看模式。详情见 [验证说明](docs/VALIDATION.md)。

这不是富士机内胶片模拟的完整移植：官方 F-Log2 / F-Gamut LUT 不能直接套在普通索尼画面上。本工具以 WDR-709 为替代中性参考，拟合 3×3 颜色矩阵与 1024 点共同曲线；尚无 a5100 的实拍色彩标定，不模拟颗粒或传感器响应，某些风格误差较明显。

## 许可、版权与参考

本项目新增内容采用 **[PolyForm Noncommercial 1.0.0](LICENSE)**，属于非商用源码公开项目，不是 OSI 定义的开源许可。商业用途未获本许可授权；准确范围及例外以原文为准。第三方材料保持各自许可，不能用本项目声明撤销它们原有的权利。

**富士官方 LUT 与相关资料的版权归富士及相应权利人所有；参考这些资料不构成官方授权。** 本项目不代表 Sony、FUJIFILM 或 Ricoh。非商用、署名及免责声明均不能代替第三方许可或保证免责。

- [许可范围与版权说明／中英日](LICENSING.md)
- [第三方来源与修改说明](NOTICE)
- [参考来源](docs/SOURCES.md)
- [权利问题反馈](docs/RIGHTS.md)

除适用法律另有要求外，软件按现状提供，不保证兼容性、色彩准确性或无侵权。测试前备份存储卡，并先使用可丢弃的测试素材；本说明不排除依法不能排除的责任。
