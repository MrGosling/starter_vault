#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Три строки о состоянии хранилища при старте сессии.

ПАСПОРТ МЕХАНИЗМА
  Что делает: считает неразобранное в inbox, дату правки справки и открытые вопросы.
  Чем запускается: хук SessionStart в .claude/settings.json, матчер startup|resume|clear|compact|fork.
  Что на выходе: три строки в stdout, среда кладёт их в контекст агента.
  Кто читает: агент в первых токенах сессии.
  Почему не иначе: файл ничего не пишет на диск, поэтому его можно удалить в любой момент.
Выход всегда 0: старт сессии не должен падать из-за сводки.
"""
import os
import sys
import time

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()


def main():
    lines = []

    inbox = os.path.join(ROOT, "inbox")
    if os.path.isdir(inbox):
        # _о папке.md лежит в заготовке и разбору не подлежит
        n = len([f for f in os.listdir(inbox)
                 if f.endswith(".md") and not f.startswith("_")])
        lines.append("В inbox лежит неразобранного: %d." % n if n else "Inbox разобран.")

    ref = os.path.join(ROOT, "Справка о системе.md")
    if os.path.exists(ref):
        days = int((time.time() - os.path.getmtime(ref)) / 86400)
        if days == 0:
            lines.append("Справку правили сегодня.")
        else:
            lines.append("Справку правили %d дн. назад." % days)

    unclear = 0
    for cur, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for fn in files:
            if not fn.endswith(".md"):
                continue
            try:
                with open(os.path.join(cur, fn), encoding="utf-8", errors="replace") as f:
                    if "## Что неясно" in f.read():
                        unclear += 1
            except Exception:
                pass
    if unclear:
        lines.append("Файлов с открытым разделом «Что неясно»: %d." % unclear)

    if lines:
        print("Состояние хранилища:\n" + "\n".join("- " + x for x in lines))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        print("Сводка недоступна.")
        sys.exit(0)
