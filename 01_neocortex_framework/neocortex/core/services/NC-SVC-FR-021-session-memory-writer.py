#!/usr/bin/env python3
"""
NC-SVC-FR-021 — SessionMemoryWriter
Registra turnos de conversa em session-log.jsonl e mantém hot_summary.
F2: integra com NC-TOOL-FR-044 (memory_auto MCP) e NC-HK-FR-004 (hooks).
"""

import json
import logging
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class SessionMemoryWriter:
    """
    Persiste turnos de conversa e fornece hot_summary para continuidade.

    Uso:
        smw = get_session_memory()
        smw.turn_record(user_msg="...", ai_response="...")
        hot = smw.get_hot_summary()
        handoff = smw.session_end(output_path=Path("memory/"))
    """

    def __init__(
        self,
        log_dir: Optional[Path] = None,
        hot_buffer_size: int = 10,
    ):
        self._log_dir = log_dir or (
            Path(__file__).parents[5]
            / ".claude"
            / "projects"
            / "c--Users-Lucas-Val-rio-Desktop-TURBOQUANT-V42"
            / "memory"
            / "session-logs"
        )
        self._log_dir.mkdir(parents=True, exist_ok=True)
        self._hot: deque = deque(maxlen=hot_buffer_size)
        self._session_date = datetime.now().strftime("%Y%m%d")
        self._log_path = self._log_dir / f"session-log-{self._session_date}.jsonl"
        self._turn_count = 0
        logger.info("SessionMemoryWriter: log em %s", self._log_path)

    # ── Core ──────────────────────────────────────────────────────────────────

    def turn_record(self, user_msg: str, ai_response: str) -> Dict:
        """Registra um turno de conversa. Retorna o entry persistido."""
        self._turn_count += 1
        ts = datetime.now().isoformat()
        tags = self._extract_tags(user_msg + " " + ai_response)
        entry = {
            "turn": self._turn_count,
            "timestamp": ts,
            "user_preview": user_msg[:120].strip(),
            "ai_summary": ai_response[:200].strip(),
            "tokens_est": self.estimate_tokens(user_msg + ai_response),
            "topic_tags": tags,
        }
        # Persistir em JSONL
        try:
            with open(self._log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.warning("SessionMemoryWriter: erro ao persistir turno %d: %s", self._turn_count, e)

        # Atualizar hot buffer
        self._hot.append(entry)
        logger.debug("turn_record: turno %d registrado", self._turn_count)
        return entry

    def get_hot_summary(self) -> List[Dict]:
        """Retorna os últimos N turnos (hot buffer)."""
        return list(self._hot)

    def get_hot_summary_text(self, max_chars: int = 2000) -> str:
        """Retorna hot_summary formatado como texto compacto."""
        lines = []
        for e in self._hot:
            lines.append(
                f"[T{e['turn']} {e['timestamp'][:16]}] "
                f"U: {e['user_preview'][:60]}... | "
                f"AI: {e['ai_summary'][:80]}..."
            )
        text = "\n".join(lines)
        return text[:max_chars]

    def session_end(self, output_path: Optional[Path] = None) -> Dict:
        """
        Encerra sessão: gera handoff compacto e salva em output_path.
        Retorna dict com stats da sessão.
        """
        output_path = output_path or self._log_dir.parent
        ts = datetime.now().strftime("%Y%m%dT%H%M%S")
        total_tokens = sum(e.get("tokens_est", 0) for e in self._hot)
        all_tags: List[str] = []
        for e in self._hot:
            all_tags.extend(e.get("topic_tags", []))
        top_tags = list(dict.fromkeys(all_tags))[:10]

        handoff = {
            "session_date": self._session_date,
            "session_end_ts": ts,
            "turns_total": self._turn_count,
            "hot_buffer_size": len(self._hot),
            "tokens_estimated": total_tokens,
            "top_topics": top_tags,
            "log_path": str(self._log_path),
            "hot_summary": self.get_hot_summary_text(),
        }

        handoff_file = output_path / f"handoff-{ts}.json"
        try:
            with open(handoff_file, "w", encoding="utf-8") as f:
                json.dump(handoff, f, ensure_ascii=False, indent=2)
            logger.info("SessionMemoryWriter: handoff salvo em %s", handoff_file)
        except Exception as e:
            logger.error("SessionMemoryWriter: erro ao salvar handoff: %s", e)

        return handoff

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Estimativa grosseira: ~4 chars/token."""
        return max(1, len(text) // 4)

    @staticmethod
    def _extract_tags(text: str) -> List[str]:
        """Extrai tags simples por frequência de palavras-chave NC."""
        keywords = [
            "litellm", "lexico", "lobe", "mcp", "tool", "ticket",
            "governança", "governance", "constitution", "roadmap",
            "kg", "knowledge", "pulse", "watchdog", "memory",
            "qwen", "deepseek", "ollama", "workflow", "ciclo",
        ]
        text_lower = text.lower()
        return [kw for kw in keywords if kw in text_lower]

    def stats(self) -> Dict:
        """Retorna estatísticas da sessão atual."""
        return {
            "session_date": self._session_date,
            "turns_recorded": self._turn_count,
            "hot_buffer_used": len(self._hot),
            "log_path": str(self._log_path),
            "log_exists": self._log_path.exists(),
        }


# Singleton
_smw_instance: Optional[SessionMemoryWriter] = None


def get_session_memory(log_dir: Optional[Path] = None) -> SessionMemoryWriter:
    """Retorna instância singleton do SessionMemoryWriter."""
    global _smw_instance
    if _smw_instance is None:
        _smw_instance = SessionMemoryWriter(log_dir=log_dir)
    return _smw_instance
