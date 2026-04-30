from __future__ import annotations

import hashlib
import json
from typing import Any


class CortexMCPAdapter:
    """Adapter boundary for Cortex MCP tool payloads.

    The host environment must provide the Cortex MCP tools; this class only
    keeps the emitted payload shape and generated IDs deterministic.
    """

    def _stable_id(self, prefix: str, payload: dict[str, Any]) -> str:
        digest = hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()[:20]
        return f"{prefix}_{digest}"

    def upsert_memory(self, payload: dict[str, Any]) -> str:
        memory_id = self._stable_id("mem", payload)
        print(json.dumps({"tool": "cortex.upsert_memory", "payload": payload, "memory_id": memory_id}, ensure_ascii=False))
        return memory_id

    def link_memories(self, from_id: str, to_id: str, relation: str) -> str:
        payload = {"from_id": from_id, "to_id": to_id, "relation": relation}
        link_id = self._stable_id("lnk", payload)
        print(json.dumps({"tool": "cortex.link_memories", "payload": payload, "link_id": link_id}, ensure_ascii=False))
        return link_id
