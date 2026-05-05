"""---
_genealogy:
  injected_at: '2026-04-16T00:23:57.192714'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: templates
level: 3
parent_ssot: NC-CFG-FR-001-plugin
tags:
  - tem
---
"""



"""
test_example.py  Template de testes unitrios para plugins do NeoCortex.

Substitua este arquivo pelos testes reais do seu plugin.
"""

import sys
from pathlib import Path

import pytest

# Adicione o caminho do plugin ao sys.path para importao
plugin_dir = Path(__file__).parent.parent
sys.path.insert(0, str(plugin_dir))


class TestExamplePlugin:
    """Exemplo de classe de testes."""

    def test_placeholder(self) -> None:
        """Teste de exemplo que sempre passa."""
        assert 1 + 1 == 2

    def test_hook_example(self) -> None:
        """Teste de hook de exemplo."""
        # Importe os hooks do seu plugin
        try:
            from hooks.NC_HK_EXAMPLE import example_pre_tool_use
        except ImportError:
            pytest.skip("Hook de exemplo no disponvel")

        context = {"tool": "write_file", "params": {"filePath": "/tmp/test.txt"}}
        result = example_pre_tool_use(context)
        assert isinstance(result, dict)
        assert "validation_passed" in result or "__block__" in result

    def test_plugin_metadata(self) -> None:
        """Verifica se plugin.json  vlido."""
        import json

        metadata_path = plugin_dir / "NC-CFG-FR-001-plugin.json"
        assert metadata_path.exists()

        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        required_fields = [
            "name",
            "version",
            "neocortex_min_version",
            "hooks",
            "commands",
        ]
        for field in required_fields:
            assert field in metadata, f"Campo obrigatrio faltando: {field}"

        # Verifica formato do nome
        assert metadata["name"].startswith("NC-TOOL-FR-"), (
            "Nome deve seguir padro NC-TOOL-FR-*"
        )

    @pytest.mark.asyncio
    async def test_async_hook(self) -> None:
        """Teste de hook assncrono (se houver)."""
        # Exemplo de teste assncrono
        # from hooks.NC_HK_EXAMPLE import async_example_hook
        # result = await async_example_hook({})
        # assert result is None
        pass


if __name__ == "__main__":
    # Execuo direta para debug
    pytest.main([__file__, "-v"])
