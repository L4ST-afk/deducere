#!/usr/bin/env bash
# 人工介入回路模板（本件自出）。
# 当辨征问建不出可无人值守跑的红灯、必须人点时，复制本文件、改下面的步骤、运行它。
# agent 跑脚本，人按终端提示操作；采集到的输出再喂回 agent 的四问三账。
#
# 用法：
#   bash human-loop.template.sh
#
# 两个助手：
#   step "<提示>"            → 显示操作提示，等人按 Enter
#   capture VAR "<问题>"      → 显示问题，把回答读进 VAR
#
# 末尾把采集值以 KEY=VALUE 打印，供 agent 解析。
# `capture` 会把值回显到终端供 agent 读取；因此采集的是观察结果，
# 登录／鉴权这类动作仍留给人，用 `step` 完成，agent 不碰凭据。

set -euo pipefail

step() {
  printf '\n>>> %s\n' "$1"
  read -r -p "    [完成后按 Enter] " _
}

capture() {
  local var="$1" question="$2" answer
  printf '\n>>> %s\n' "$question"
  read -r -p "    > " answer
  printf -v "$var" '%s' "$answer"
}

# --- 在此以下编辑 -------------------------------------------------------

step "打开应用到 http://localhost:3000 并登录。"

capture ERRORED "点『导出』按钮，是否抛错？(y/n)"

capture ERROR_MSG "粘贴报错原文（没有就写 none）："

# --- 在此以上编辑 -------------------------------------------------------

printf '\n--- 采集结果 ---\n'
printf 'ERRORED=%s\n' "$ERRORED"
printf 'ERROR_MSG=%s\n' "$ERROR_MSG"
