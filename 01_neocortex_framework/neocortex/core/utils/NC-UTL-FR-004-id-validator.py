"""---
_genealogy:
  injected_at: '2026-04-16T00:23:59.192138'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-UTL-FR-004-id-validator
tags:
  - neocortex-other
  - level-0
  - nc-prefix
  - python
---"""
"""
NC-UTL-FR-004-id-validator.py
FR-004  ID Validator: Validador de IDs e constantes compartilhadas.

Valida formatos de IDs NeoCortex (ticket, worker, session, nc_file, lobe) e fornece
funes de checksum, gerao de IDs e constante de erro permanente.
"""

import hashlib
import logging
import re
from datetime import datetime
from typing import Dict

logger = logging.getLogger(__name__)

# Constante compartilhada (importar de outros mdulos)
EXIT_CODE_PERMANENT = 42  # erros no-retentveis (padro Claude Code)


class IDValidator:
    """Validador de IDs no formato NeoCortex."""

    # Padres de IDs vlidos
    PATTERNS: Dict[str, re.Pattern] = {
        "ticket": re.compile(r"^NC-DS-\d{3}$"),
        "worker": re.compile(r"^worker-\d{4,5}-[a-f0-9]{4}$"),
        "session": re.compile(r"^sess-\d{8}-\d{6}$"),
        "nc_file": re.compile(r"^NC-[A-Z]+-[A-Z]+-\d{3}"),
        "lobe": re.compile(r"^NC-LBE-[A-Z]+-[A-Z0-9-]+\.mdc$"),
    }

    def validate(self, id_str: str, id_type: str) -> bool:
        """
        Valida se uma string corresponde ao padro do tipo de ID especificado.

        Args:
            id_str: String a validar (ex.: "NC-DS-034")
            id_type: Tipo de ID (ticket, worker, session, nc_file, lobe)

        Returns:
            True se vlido, False caso contrrio.
        """
        if id_type not in self.PATTERNS:
            logger.warning(f"Tipo de ID desconhecido: {id_type}")
            return False
        pattern = self.PATTERNS[id_type]
        match = pattern.match(id_str)
        valid = match is not None
        if not valid:
            logger.debug(f"ID invlido: '{id_str}' no corresponde a {pattern.pattern}")
        return valid

    def get_checksum(self, data: str) -> str:
        """
        Calcula checksum SHA-256 truncado para validao de integridade.

        Args:
            data: Dados a serem checksumados.

        Returns:
            String hexadecimal de 4 caracteres.
        """
        hash_obj = hashlib.sha256(data.encode())
        return hash_obj.hexdigest()[:4]

    def generate_session_id(self) -> str:
        """
        Gera um ID de sesso no formato sess-YYYYMMDD-HHMMSS.

        Returns:
            ID de sesso nico baseado no timestamp atual.
        """
        now = datetime.now()
        return f"sess-{now.strftime('%Y%m%d-%H%M%S')}"

    def generate_worker_id(self, port: int) -> str:
        """
        Gera um ID de worker no formato worker-PORT-HASH4.

        Args:
            port: Nmero da porta (4-5 dgitos).

        Returns:
            ID de worker com checksum do port.
        """
        port_str = str(port)
        if not (1000 <= port <= 99999):
            logger.warning(f"Porta fora do intervalo esperado: {port}")
        checksum = self.get_checksum(port_str)
        return f"worker-{port_str}-{checksum}"

    def is_permanent_error(self, exit_code: int) -> bool:
        """
        Determina se um cdigo de sada corresponde a um erro permanente.

        Args:
            exit_code: Cdigo de sada a verificar.

        Returns:
            True se exit_code == EXIT_CODE_PERMANENT (42).
        """
        return exit_code == EXIT_CODE_PERMANENT


# Funo de convenincia para uso imediato
def get_id_validator() -> IDValidator:
    """Retorna instncia singleton do validador de IDs."""
    return IDValidator()
