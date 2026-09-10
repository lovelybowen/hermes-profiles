# macOS 桌面应用排障（沙箱应用）

*本文件是 `systematic-debugging` 技能的参考文件，加载方式：*
*`skill_view('systematic-debugging', file_path='references/macos-desktop-troubleshooting.md')`*

**适用范围：** 仅当被调查的缺陷发生在 **macOS 桌面应用** 时适用。本项目的 R&D 语境以服务端 / Web / CLI 为主，默认不需要本文件。

从上游 Hermes 自带技能携带而来，未做改动。

---

**调试 macOS 应用，尤其是“图书”“音乐”或 App Store 应用等沙箱应用时：**

应用被限制在 `~/Library/Containers/<bundle-id>/` 下的沙箱容器中。

#### 定位容器

```bash
ls ~/Library/Containers/<bundle-id>/
# Data/Library/ - 偏好设置、缓存、数据库
# Data/Documents/ - 用户可见内容、导入队列
```

#### 检查配套 XPC 服务

许多 Apple 应用使用后台 XPC 服务执行文件操作：

```bash
# XPC 服务位于框架包或应用包中：
/System/Library/PrivateFrameworks/<Framework>.framework/XPCServices/
/System/Applications/<App>.app/Contents/XPCServices/
ps aux | grep -i "<service-name>"
```

#### 直接读取数据库

沙箱应用通常使用 SQLite/CoreData：

```bash
sqlite3 ~/Library/Containers/<bundle-id>/Data/Documents/<path>.sqlite ".tables"
sqlite3 ~/Library/Containers/<bundle-id>/Data/Documents/<path>.sqlite "SELECT * FROM ZTABLE LIMIT 10;"
```

#### 检查系统日志

```bash
log show --predicate 'process == "AppName"' --last 10m --style compact
log stream --predicate 'process == "AppName"' --style compact
```

#### 重置 TCC 权限

如果应用无法访问沙箱之外的文件，例如导入静默失败：

```bash
tccutil reset All com.apple.bundle-id
```

#### 理解 I/O 边界

- **安全作用域书签：**来自拖放或 `open` 命令的书签只能使用一次。如果导入失败，书签已被消耗，后续尝试会静默失败。
- **NSOpenPanel：**“文件 > 导入”对话框会创建新书签，因此测试更可靠。
- 如果 `open -b bundle-id file.ext` 对“下载”目录中的文件有效、对桌面文件无效，可能是 TCC 或分层访问问题，因为 macOS 为“下载”目录提供更宽松的访问权限。

#### 区分本地损坏与云同步损坏

重置容器可以修复本地状态，但不能修复 iCloud 同步损坏。云端问题的迹象包括：
- 完全删除容器并重新安装后问题仍然存在。
- 重启后导入仅成功一次，随后再次失效。
- 多台设备都出现相同问题。

**操作：**如果本地重置无法修复，iCloud 同步状态可能已经损坏。最后手段是“系统设置 → Apple ID → iCloud → 管理储存空间 → [应用] → 删除所有数据”。

#### 恢复选项（按升级顺序）

1. 终止并重启 XPC 服务（`kill -9 <PID>`），这只是临时措施，XPC 会重新启动。
2. 重置应用容器（`rm -rf ~/Library/Containers/<bundle-id>/`）。
3. 重置 TCC 权限（`tccutil reset All <bundle-id>`）。
4. 重启 Mac。
5. 删除应用的 iCloud 数据。
6. 创建一个用于测试的 macOS 用户。如果应用在该用户下正常，问题位于当前用户资料库，而不是系统。

