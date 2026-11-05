#!/usr/bin/env python3
"""在线条目的片头片尾（跳过时间）。state/play_config.json。

飞牛影视的片头片尾不是一个「存起来再单独读」的设置，它跟着播放信息走：

  - 设置时：POST /v/api/v1/play/setConfigByItem  {guid, skip_opening, skip_ending}
  - 播放时：POST /v/api/v1/play/info 的返回里带 play_config {guid, skip_opening, skip_ending}

官方后端把这套配置挂在媒体库的条目上，而我们注入的在线条目在库里不存在，
所以设置请求虽然返回成功（上游对不存在的条目静默通过），播放时又拿不到——
表现就是「设置完当次有效，退出重进就复位」。

这里按 play/info 里的 parent_guid（剧集是 season guid）本地记一份：写请求仍照常
透传上游（本地片不受影响），播放时把 play_config 回填给客户端。

条目 guid 为空时一律不记录：那说明这条播放信息没有可用的归属，硬记会让不同影片
共用同一组片头片尾，错跳比记不住更糟。
"""
from __future__ import annotations

import json
import threading
import time
from pathlib import Path

_STATE = Path(__file__).resolve().parent.parent / "state" / "play_config.json"
_LOCK = threading.RLock()
_MAX = 2000

_data: dict[str, dict] = {}
_loaded = False


def _load() -> None:
    global _loaded
    if _loaded:
        return
    with _LOCK:
        if _loaded:
            return
        try:
            j = json.loads(_STATE.read_text(encoding="utf-8"))
            if isinstance(j, dict):
                _data.update({k: v for k, v in j.items() if isinstance(v, dict)})
        except Exception:
            pass
        _loaded = True


def _flush() -> None:
    try:
        _STATE.parent.mkdir(parents=True, exist_ok=True)
        tmp = _STATE.with_suffix(".tmp")
        tmp.write_text(json.dumps(_data, ensure_ascii=False), encoding="utf-8")
        tmp.replace(_STATE)
    except Exception:
        pass


def _secs(v) -> int:
    try:
        return max(0, int(float(v or 0)))
    except (TypeError, ValueError):
        return 0


def get(guid: str) -> dict | None:
    """该条目已保存的 play_config；没有记录返回 None（与改造前行为一致）。"""
    g = str(guid or "")
    if not g:
        return None
    _load()
    with _LOCK:
        rec = _data.get(g)
        if not rec:
            return None
        return {"guid": g,
                "skip_opening": _secs(rec.get("skip_opening")),
                "skip_ending": _secs(rec.get("skip_ending"))}


def update(guid: str, opening, ending) -> dict | None:
    g = str(guid or "")
    if not g:
        return None
    _load()
    rec = {"guid": g, "skip_opening": _secs(opening),
           "skip_ending": _secs(ending), "updated_at": int(time.time())}
    with _LOCK:
        _data[g] = rec
        if len(_data) > _MAX:
            drop = len(_data) - _MAX
            for k, _ in sorted(_data.items(),
                               key=lambda kv: kv[1].get("updated_at", 0))[:drop]:
                _data.pop(k, None)
        _flush()
    return {"guid": g, "skip_opening": rec["skip_opening"],
            "skip_ending": rec["skip_ending"]}


def count() -> int:
    _load()
    with _LOCK:
        return len(_data)
