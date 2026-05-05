from __future__ import annotations

import hashlib
import json
from typing import Any


class CortexMCPAdapter:
    """Adapter boundary for Cortex MCP tool payloads.

    The host environment must provide the Cortex MCP tools; this class only
    keeps the emitted payload shape and generated IDs deterministic.
    """

    _ENTITY_LIST_FIELDS = ("people", "places", "themes", "bible_references")

    def _normalize_entity_list(self, values: Any) -> list[str]:
        if not isinstance(values, list):
            raise TypeError("entity-bearing fields must be lists")

        normalized: list[str] = []
        seen: set[str] = set()
        for value in values:
            if not isinstance(value, str):
                raise TypeError("entity-bearing fields must contain strings")
            item = value.strip()
            if not item or item in seen:
                continue
            seen.add(item)
            normalized.append(item)
        return normalized

    def _normalize_entity_payload(self, payload: dict[str, Any]) -> bool:
        normalized = False
        for field in self._ENTITY_LIST_FIELDS:
            if field in payload:
                payload[field] = self._normalize_entity_list(payload[field])
                normalized = True

        if normalized:
            metadata = payload.setdefault("metadata", {})
            if not isinstance(metadata, dict):
                raise TypeError("payload metadata must be a dict when present")
            metadata.setdefault("entity_resolution", "normalize")
            metadata.setdefault("normalization_policy", "entity-canonicalization")

        return normalized

    def _stable_id(self, prefix: str, payload: dict[str, Any]) -> str:
        # If payload already has an 'id', use it
        if "id" in payload:
            return payload["id"]
        # Use canonical_id if present for determinism
        if "canonical_id" in payload:
            return payload["canonical_id"]
            
        digest = hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()[:20]
        return f"{prefix}_{digest}"

    def upsert_memory(self, payload: dict[str, Any]) -> str:
        self._normalize_entity_payload(payload)
        payload.setdefault("retention_policy", "protected")
        memory_id = self._stable_id("mem", payload)
        # Ensure 'id' is in the payload for the final tool call
        payload["id"] = memory_id
        # Remove canonical_id if it was just used for generating the id
        if "canonical_id" in payload:
            del payload["canonical_id"]
            
        print(json.dumps({"tool": "cortex.store", "payload": payload}, ensure_ascii=False))
        return memory_id

    def link_memories(self, from_id: str, to_id: str, relation: str) -> str:
        payload = {
            "source_id": from_id,
            "target_id": to_id,
            "relation": relation,
            "retention_policy": "protected",
        }
        print(json.dumps({"tool": "cortex.link", "payload": payload}, ensure_ascii=False))
        return f"{from_id}->{to_id}"
