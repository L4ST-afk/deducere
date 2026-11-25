# 贡献指南

改哪一层，跑什么检查，都写在这里。

## 改哪一层

| 层 | 文件 | 职责 |
|---|---|---|
| 总纲 | `SKILL.md` | 四问三账总纲、硬闸、资源导航；只写原则，不写判据句 |
| 判据 | `references/判据表.md` | 29 条判据的唯一载体（问法／判违规／症状句／深读） |
| 展开卷 | `references/*.md` | 各问的机制、方法、反模式；⛔ 复写判据句，只引 J 编号 |
| 执行器 | `scripts/*.py` | 红绿硬闸、净痕检查、自检；判据归口判据表，脚本不另立判据 |

改判据只改判据表一处；正文与展开卷只引编号。中英 README / CHANGELOG 同改。

## 提交前检查

```sh
python3 scripts/selftest.py                      # 离线自检，期望 PASS，退出码 0
python3 -m unittest discover -s tests -q         # 24 个测试，期望 OK
python3 scripts/check_clean.py --repo .          # 净痕检查
```

三条都过再提交。⛔ 不提交 `__pycache__/`、`.pyc`、评审记录与过程文档。

## 许可

提交即表示同意按本仓库 LICENSE（MIT）发布你的贡献。
