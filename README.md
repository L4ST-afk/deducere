# 对鸟 Deducere · 证据链根因定位与故障归因

[中文](README.md) · [English](README.en.md)

<!-- cover slot: once `docs/cover.jpg` lands, insert
     <img src="docs/cover.jpg" alt="对鸟 Deducere — 墨绿毡布上四枚分离錾金鸟铭牌，四鸟相向，眼宝为祖母绿、白钻、红宝石、蓝宝石，间杂 20 世纪贸易彩珠" width="720">
     ⛔ No placeholder link while the image is missing. -->

> 视觉造型、四鸟四宝对位、錾金与彩珠源流及三层对仗（时间／空间／含义）的定版规则见 [references/visual-language.md](references/visual-language.md)。

> 乐清山歌，四鸟对答。
> 问飞过青又青，答羽色何处生；
> 问打铜铃声声急，答机括何处鸣。
> 疑窦未破，赤瞳如烽；一问一证，循迹追踪。
> 不凭臆测改一字，必先致赤而后绿，断在坏源初生处。

**问题排查与根因定位 Skill**：只凭可复现证据链定位故障根源，用先复现、排序假设、单一变量最小插桩与隔离试改，把「瞎猜乱改」与「真正修好」彻底拆开。

中文名取自温州乐清国家级非遗民歌**《对鸟》**（一问一答、以唱对答、不合律则不续）；外文名 *Deducere*（回溯引出、推演至根因）。定名与读音正字见 [references/naming.md](references/naming.md)。

---

## 四问三账（构造核心）

调试不是六步流水线，而是四个可反复进入的问，加三本互不替代的账。问无固定顺序，只有一道单向约束：**过程账绿灯不替结果账结账**。

| 问 | 封面鸟 | 回答什么 | 出口（机器可判） | 出口（人判，标证据级） |
|---|---|---|---|---|
| 辨征 | 青翠·祖母绿 | 这条红断言的是确切症状吗 | `verify_red_green.py --expect red` rc=0（非零＋命中症状正则） | 断言用户确切症状，不是「没崩」〔L1〕 |
| 循链 | 白鸽·白钻 | 因果链落到哪行、坏值在哪出生 | — | 多条可证伪假设（≥2）、`file:line` 本会话打开、平凡原因先排〔L0〕 |
| 验真 | 雉鸡·红宝石 | 同一条命令先红后绿了吗 | `--expect green` rc=0（先红后绿同一条命令） | 接缝跑真实触发链，源头修不挡症状〔L1〕 |
| 净痕 | 长尾巴丁·蓝宝石 | 探针拔净、断源防再犯了吗 | `check_clean.py` rc=0 | 六项人工清单＋八段汇报＋结果账隔期〔L0〕 |

**三账**：过程账（当下可判，机器＋本会话）、结果账（隔期才可判，人或隔期复验）、证据账（标 L0/L1/L2 与可回读路径）。四问全绿只说明过程合规；结果账无隔期数据就是「证据不足」，⛔ 写「已解决」。

> **止损硬阈值**：同根因连续 **2 轮**修复未转绿、或 **3 轮**插桩未证伪任何假设，立即止损整理。阈值为闭合闸门的 L0 取值，待真实代码 bug 实测后校准，见 [pending-thresholds.md](references/pending-thresholds.md) T3。
> **判据唯一载体**：30 条判据（问法／判违规／症状句）见 [references/判据表.md](references/判据表.md)，按四问分 J1–J30；正文与展开卷只引编号，不复写判据句。

---

## 自检与日常命令

离线回归（零依赖、不联网）：

```bash
python3 scripts/selftest.py                      # 语法冒烟，期望 PASS、退出码 0
python3 -m unittest discover -s tests -q         # 双硬闸业务回归，期望 OK、退出码 0
```

排查与交付前硬闸：

```bash
# 1. 修复前锁死红灯（必须非 0 退出码且命中症状正则）
python3 scripts/verify_red_green.py --expect red --cmd "<repro-cmd>" --match "<error-regex>"

# 2. 修复后验证转绿（同一条命令必须返回 0）
python3 scripts/verify_red_green.py --expect green --cmd "<repro-cmd>"

# 3. 交付前扫描工作区，拦截残留 [DEBUG-*] 探针（发现残留退出码 1）
python3 scripts/check_clean.py --repo .
```

## 目录

```text
对鸟Deducere/
├── SKILL.md                  # 四问三账总纲、硬闸与横切闸（判据句不在本页）
├── references/
│   ├── 判据表.md              # 30 条判据（问法／判违规／症状句／可选深读）
│   ├── field-notes-7.md        # 七次实地排障手记（第一手资料与回改建议）
│   ├── naming.md             # 定名、读音钉死、落选名与诚实缺口
│   ├── feedback-loops.md     # 十种接缝、回路收紧、非确定 bug 与降级
│   ├── hypothesis-methods.md # 兄弟件对照、边界二分、合议流程与降级
│   ├── anti-patterns.md      # 源头修反模式、个例/普遍二分、防再犯三选一
│   ├── reporting-and-handoff.md # 汇报模板、收尾清理清单、逐项验证与交接对接
│   ├── provenance.md         # 独立实现声明、构造来源、血缘切断说明
│   ├── visual-language.md    # 封面/题图视觉定版：四鸟四宝、錾金与彩珠源流、三层对仗
│   └── pending-thresholds.md # 待校准阈值（P 池，90 天到期即删）
├── scripts/
│   ├── verify_red_green.py   # 先红后绿证伪硬闸
│   ├── check_clean.py        # 探针残留收尾洁癖闸
│   ├── selftest.py           # 语法级离线冒烟自检
│   └── human-loop.template.sh # 必须人介入时的结构化人工回路模板（本件自出）
└── tests/
│   └── test_deducere.py      # 27 组双硬闸业务回归用例
```

## 封面器物隐喻（设计彩蛋）

<details>
<summary>🎨 封面题记与四宝隐喻（点击展开）</summary>

封面取意乐清民歌《对鸟》四问四答：四枚錾金鸟牌相向而置，各嵌一眼宝，隐喻调试排障的四个关键心法。题记押庚青韵（名／明／成／萌）：

> 四鸟相向，以问酬答。
> 何鸟飞过青又青？
> 羽征先辨，识其名；
> 何鸟声里打铜铃？
> 循链下溯，祸始明；
> 何鸟羽上红夹绿？
> 先赤后碧，验乃成；
> 何鸟抹把胭脂唇？
> 迹净揩除，患不萌。

| 封面金鸟 | 眼嵌宝玉 | 题记对答 | 隐喻问 |
|---|---|---|---|
| 青翠（绿鸠） | 祖母绿 | 羽征先辨，识其名 | 辨征问：断言确切症状，不逐虚影 |
| 白鸽 | 白钻 | 循链下溯，祸始明 | 循链问：多条可证伪，一次只变一个变量 |
| 雉鸡（环颈雉） | 红宝石 | 先赤后碧，验乃成 | 验真问：同一条命令先复现赤、修复后转碧 |
| 长尾巴丁（红嘴蓝鹊） | 蓝宝石 | 迹净揩除，患不萌 | 净痕问：修在坏源初生处，拔针不留余痕 |

铭牌间隙散落的贸易彩珠（玛瑙／玉髓石珠与千花玻璃珠，单颗散放、不穿成串），隐喻跨系统流转的调用链与数据线索——顺珠寻线，方得真因。完整视觉定版见 [references/visual-language.md](references/visual-language.md)。
</details>

## 许可与本机件声明

本件为独立实现，非任何上游件的派生、翻译或改写；构造、判据、脚本、叙事与正文皆为本库自出，不附带 MIT 或其他上游许可义务。详见 [provenance.md](references/provenance.md)。

公开分发件不含本机声明与实地手记。
