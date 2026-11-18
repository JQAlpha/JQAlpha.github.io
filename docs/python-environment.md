# Python 环境说明

> 本项目的 Python 环境配置与路径约定。**改动环境前先读这份文档。**

---

## 一、Python 解释器绝对路径

这台机器上**有三套** Python 入口，但只有两个是真实解释器：

| # | 绝对路径 | 版本 | 性质 | 本项目用途 |
|---|---|---|---|---|
| 1 | `C:\Users\LAPTOP-Gary\.workbuddy\binaries\python\versions\3.13.12\python.exe` | 3.13.14 | WorkBuddy 内置版 | ✅ **本项目用它** |
| 2 | `C:\Apps_Dev\Tools\miniconda3\python.exe` | 3.13.9 | Miniconda base | conda 各专用环境 |
| 3 | `C:\Users\LAPTOP-Gary\AppData\Local\Microsoft\WindowsApps\python.exe` | — | 微软商店占位符 | ❌ 不是真解释器 |

### 关键结论

**项目里所有 Python 调用都用绝对路径指向 #1**，不要依赖 `python` 这个命令能解析到它。

原因：不同终端解析结果不同。

| 终端 | `python` 解析到 | 数据分析栈 |
|---|---|---|
| Git Bash（WorkBuddy 会话） | #1 WorkBuddy 内置版 | ✅ 齐全 |
| Windows Terminal / PowerShell / CMD | #2 Miniconda base | ⚠️ 只有 pandas/numpy |

**更隐蔽的坑**：`pip` 命令在任何终端都指向 #2（miniconda），因为 `pip.exe` 在
`C:\Apps_Dev\Tools\miniconda3\Scripts\` 下。所以：

```bash
python script.py          # 用 #1 执行
pip install xxx           # 装到 #2 去了！
```

**包会装错地方**，而且 `pip list` 看到的和 `python -c "import xxx"` 实际能导入的
可能不是一回事。

---

## 二、正确的包安装方式

**永远用 `python -m pip`，不要用裸 `pip`：**

```bash
# ✅ 正确 —— pip 和 python 同一个解释器
"C:\Users\LAPTOP-Gary\.workbuddy\binaries\python\versions\3.13.12\python.exe" -m pip install xxx

# ❌ 错误 —— 装到另一个解释器
pip install xxx
```

项目内的脚本用 `python -m pip` 即可，因为 `python` 在项目上下文里已经是 #1。
但如果你在 PowerShell 里操作，请用上面的绝对路径形式。

---

## 三、环境变量现状

### 持久化（Windows 注册表，重启后仍生效）

**用户级**：
- `PYTHON*` / `CONDA*` / `PIP*` / `VIRTUAL_ENV` —— **均未设置**
- PATH 中与 Python 相关的条目（4 条，全部指向 Miniconda）：
  ```
  C:\Apps_Dev\Tools\miniconda3
  C:\Apps_Dev\Tools\miniconda3\Library\mingw-w64\bin
  C:\Apps_Dev\Tools\miniconda3\Library\usr\bin
  C:\Apps_Dev\Tools\miniconda3\Scripts
  ```

**系统级**：无 Python 相关变量

### 进程级（仅当前 WorkBuddy 会话，由运行时注入）

| 变量 | 值 | 说明 |
|---|---|---|
| `PYTHONPATH` | `C:\Apps\WorkBuddy\resources\app.asar.unpacked\cli\vendor\sandbox-center-runtime-kit\shim` | WorkBuddy 内部 shim，**不是**给项目用的 |
| `PYTHONDONTWRITEBYTECODE` | `1` | 不生成 .pyc |
| `PYTHONIOENCODING` | `utf-8` | 输出编码 |
| `PYTHONUTF8` | `1` | UTF-8 模式 |
| `CONDA_PREFIX` / `CONDA_DEFAULT_ENV` / `CONDA_PYTHON_EXE` | 空 | 未激活任何 conda 环境 |

> **注意** `PYTHONPATH` 指向 WorkBuddy 的内部 shim 目录。
> 如果你的脚本 import 了与标准库同名的模块，可能被这个 shim 劫持。
> 需要干净环境时用 `python -E`（忽略所有 PYTHON* 环境变量）或 `python -I`（隔离模式）。

---

## 四、Conda 环境

```
base         C:\Apps_Dev\Tools\miniconda3
akshare_p13  C:\Apps_Dev\Tools\miniconda3\envs\akshare_p13
brain_evn    C:\Apps_Dev\Tools\miniconda3\envs\brain_evn
env_xml      C:\Apps_Dev\Tools\miniconda3\envs\env_xml
qmt_p13      C:\Apps_Dev\Tools\miniconda3\envs\qmt_p13
```

这些专用环境与本项目**无关**，本项目统一用 #1。

---

## 五、已安装包（解释器 #1）

```
pandas       3.1.1        numpy        2.5.5        matplotlib  3.11.2
plotly       7.1.0        scipy        1.18.1       statsmodels 0.15.0
nbformat     5.11.1       nbconvert    7.17.2       papermill   2.7.0
jinja2       3.1.6        ipykernel    9.18.1       nbclient    0.11.0
```

site-packages：
```
C:\Users\LAPTOP-Gary\.workbuddy\binaries\python\versions\3.13.12\Lib\site-packages
```

---

## 六、项目内的工具

### `scripts/which_python.py` —— 解释器解析器

自动按优先级挑选满足依赖的解释器，用法：

```bash
python scripts/which_python.py           # 打印该用哪个解释器
python scripts/which_python.py --check   # 校验解释器与依赖完整性
python scripts/which_python.py --json    # JSON 输出（供其他脚本调用）
```

候选顺序：
1. `tools/python/python.exe`（项目内自带的解释器，当前不存在，留作扩展位）
2. WorkBuddy 内置版（**当前命中**）
3. Miniconda base

### `scripts/ipynb_to_md.py` —— Notebook 转文章

启动时会自检依赖，**若当前解释器缺包会自动转交**到正确解释器重新执行。
所以在 PowerShell 里用 `python scripts/ipynb_to_md.py` 也能正常工作。

参数：
- `--no-execute`：跳过执行，直接转换已保存的输出
- 指定文件名：`python scripts/ipynb_to_md.py 某文件.ipynb`

### `scripts/plot_config.py` —— Matplotlib 中文字体与配色

```python
import sys
sys.path.insert(0, '../scripts')
import plot_config
plot_config.apply()
```

解决三件事：
1. **中文字体**——默认 DejaVu Sans 无中文，标题会显示为方块。自动探测微软雅黑/黑体/宋体
2. **负号方块**——`axes.unicode_minus = False`
3. **配色统一**——与网站设计变量一致（`#2563eb` 主色）

另有 `plot_config.dark_theme()` 切换深色背景。

---

## 七、快速自检

```bash
cd C:/WorkSpace/github-pages

# 解释器与依赖
python scripts/which_python.py --check

# 完整链路：notebook → 文章 + 图表
python scripts/ipynb_to_md.py

# 构建
npm run build
npm run check
```

---

## 八、如果环境出问题

| 症状 | 原因 | 处理 |
|---|---|---|
| `ModuleNotFoundError` | 包装到了另一个解释器 | 用 `python -m pip install` 重装 |
| 图表中文是方块 | 没设中文字体 | notebook 里 `import plot_config; plot_config.apply()` |
| `pip install` 后 import 不到 | pip 与 python 不同源 | 永远用 `python -m pip` |
| import 被劫持 | `PYTHONPATH` 指向 WorkBuddy shim | 加 `python -E` 或 `python -I` |
| 脚本在 PowerShell 里报缺包 | PowerShell 的 python 是 Miniconda | 脚本已自动转交；手动调用时用 `python scripts/which_python.py` 查 |
