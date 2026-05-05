#!/usr/bin/env python3
"""---
NC-HK-FR-006-lexico-hook-chain.py
---
"""

"""---
NC-HK-FR-006-lexico-hook-chain.py
---
"""

"""
NC-HK-FR-006-lexico-hook-chain.py
LEXICO-006 — Sistema de Cadeia de Hooks Lexicais.

Objetivo: Executar hooks lexicais em cadeia com passagem de contexto,
priorização e composição de resultados.

Funcionalidades:
1. Execução sequencial de hooks com base em prioridade
2. Passagem de contexto entre hooks na cadeia
3. Composição de resultados parciais
4. Suporte a execução síncrona e assíncrona
5. Circuit breaker e fallback mechanisms
6. Integração com neocortex_context para gerenciamento de estado
"""

import asyncio
import logging
import threading
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)


class HookChainEvent(StrEnum):
    """Eventos suportados pela cadeia de hooks lexicais."""
    PRE_LEXICAL_ANALYSIS = "pre_lexical_analysis"
    POST_TOKENIZATION = "post_tokenization"
    SEMANTIC_ENRICHMENT = "semantic_enrichment"
    CONTEXT_COMPRESSION = "context_compression"
    CUSTOM = "custom"


class HookExecutionMode(StrEnum):
    """Modos de execução de hooks na cadeia."""
    SEQUENTIAL = "sequential"      # Executa um após o outro
    PARALLEL = "parallel"          # Executa em paralelo
    WATERFALL = "waterfall"        # Passa resultado de um para o próximo
    RACE = "race"                  # Primeiro que completar vence


class HookResultStatus(StrEnum):
    """Status de resultado de execução de hook."""
    SUCCESS = "success"
    SKIPPED = "skipped"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CIRCUIT_BREAKER = "circuit_breaker"


@dataclass
class HookChainContext:
    """Contexto passado através da cadeia de hooks."""
    event: HookChainEvent
    initial_data: dict[str, Any]
    current_data: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    execution_id: str = ""
    created_at: datetime = field(default_factory=datetime.now)

    def update(self, key: str, value: Any) -> None:
        """Atualiza dados atuais do contexto."""
        self.current_data[key] = value

    def merge(self, data: dict[str, Any]) -> None:
        """Mescla dados no contexto atual."""
        self.current_data.update(data)

    def get(self, key: str, default: Any = None) -> Any:
        """Obtém valor do contexto atual."""
        return self.current_data.get(key, default)

    def to_dict(self) -> dict[str, Any]:
        """Converte contexto para dicionário."""
        return {
            "event": self.event.value,
            "initial_data": self.initial_data.copy(),
            "current_data": self.current_data.copy(),
            "metadata": self.metadata.copy(),
            "execution_id": self.execution_id,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class HookExecutionResult:
    """Resultado da execução de um hook individual."""
    hook_name: str
    status: HookResultStatus
    output: Any | None = None
    error: str | None = None
    duration_ms: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Converte resultado para dicionário."""
        return {
            "hook_name": self.hook_name,
            "status": self.status.value,
            "output": self.output,
            "error": self.error,
            "duration_ms": self.duration_ms,
            "metadata": self.metadata
        }


@dataclass
class HookChainDefinition:
    """Definição de um hook na cadeia."""
    name: str
    handler: Callable[[HookChainContext], Any]
    priority: int = 100
    timeout_seconds: float = 3.0
    enabled: bool = True
    circuit_breaker_threshold: int = 3  # Número de falhas antes de abrir circuito
    fallback_handler: Callable | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class CircuitBreaker:
    """Circuit breaker para hooks individuais."""

    def __init__(self, failure_threshold: int = 3, reset_timeout: float = 30.0):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failure_count = 0
        self.last_failure_time: float | None = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self._lock = threading.Lock()

    def record_success(self):
        """Registra sucesso e reseta contador."""
        with self._lock:
            self.failure_count = 0
            self.state = "CLOSED"
            self.last_failure_time = None

    def record_failure(self):
        """Registra falha e atualiza estado."""
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"

    def should_allow(self) -> bool:
        """Verifica se a execução deve ser permitida."""
        with self._lock:
            if self.state == "CLOSED":
                return True

            if self.state == "OPEN":
                # Verificar se já passou tempo suficiente para tentar reset
                if self.last_failure_time and (
                    time.time() - self.last_failure_time > self.reset_timeout
                ):
                    self.state = "HALF_OPEN"
                    return True
                return False

            if self.state == "HALF_OPEN":
                # Permitir uma tentativa
                return True

            return False

    def get_state(self) -> dict[str, Any]:
        """Retorna estado atual do circuit breaker."""
        with self._lock:
            return {
                "state": self.state,
                "failure_count": self.failure_count,
                "last_failure_time": self.last_failure_time,
                "failure_threshold": self.failure_threshold,
                "reset_timeout": self.reset_timeout
            }


class LexicoHookChain:
    """Sistema de cadeia de hooks lexicais.

    Gerencia execução de múltiplos hooks em diferentes modos:
    - SEQUENTIAL: Executa hooks em sequência
    - PARALLEL: Executa hooks em paralelo
    - WATERFALL: Passa resultado de um hook para o próximo
    - RACE: Executa todos, primeiro que completar vence
    """

    def __init__(
        self,
        name: str,
        execution_mode: HookExecutionMode = HookExecutionMode.SEQUENTIAL,
        max_parallel_workers: int = 4
    ):
        self.name = name
        self.execution_mode = execution_mode
        self.max_parallel_workers = max_parallel_workers

        self._hooks: dict[str, HookChainDefinition] = {}
        self._circuit_breakers: dict[str, CircuitBreaker] = {}
        self._lock = threading.Lock()
        self._executor = ThreadPoolExecutor(max_workers=max_parallel_workers)

        # Estatísticas
        self._execution_stats: dict[str, Any] = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "total_duration_ms": 0.0
        }

    def add_hook(
        self,
        name: str,
        handler: Callable[[HookChainContext], Any],
        priority: int = 100,
        timeout_seconds: float = 3.0,
        enabled: bool = True,
        circuit_breaker_threshold: int = 3,
        fallback_handler: Callable | None = None,
        metadata: dict[str, Any] | None = None
    ) -> None:
        """Adiciona um hook à cadeia."""
        with self._lock:
            if name in self._hooks:
                logger.warning(f"Hook '{name}' já existe na cadeia '{self.name}', substituindo")

            hook_def = HookChainDefinition(
                name=name,
                handler=handler,
                priority=priority,
                timeout_seconds=timeout_seconds,
                enabled=enabled,
                circuit_breaker_threshold=circuit_breaker_threshold,
                fallback_handler=fallback_handler,
                metadata=metadata or {}
            )

            self._hooks[name] = hook_def
            self._circuit_breakers[name] = CircuitBreaker(
                failure_threshold=circuit_breaker_threshold
            )

            logger.info(f"Hook '{name}' adicionado à cadeia '{self.name}' (priority: {priority})")

    def remove_hook(self, name: str) -> bool:
        """Remove um hook da cadeia."""
        with self._lock:
            existed = name in self._hooks
            if existed:
                del self._hooks[name]
                del self._circuit_breakers[name]
                logger.info(f"Hook '{name}' removido da cadeia '{self.name}'")
            return existed

    def execute(
        self,
        event: HookChainEvent,
        initial_data: dict[str, Any],
        execution_id: str | None = None
    ) -> dict[str, Any]:
        """Executa a cadeia de hooks.

        Args:
            event: Tipo de evento a ser processado
            initial_data: Dados iniciais para o contexto
            execution_id: ID opcional para rastreamento

        Returns:
            Dicionário com resultados da execução
        """
        start_time = time.perf_counter()
        self._execution_stats["total_executions"] += 1

        # Criar contexto
        context = HookChainContext(
            event=event,
            initial_data=initial_data.copy(),
            current_data=initial_data.copy(),
            execution_id=execution_id or f"{self.name}_{int(time.time())}"
        )

        # Obter hooks habilitados e ordenar por prioridade
        hooks_to_execute = self._get_sorted_hooks()

        if not hooks_to_execute:
            logger.debug(f"Nenhum hook habilitado para cadeia '{self.name}'")
            return self._create_empty_result(context)

        logger.info(
            f"Executando cadeia '{self.name}' com {len(hooks_to_execute)} hooks "
            f"(mode: {self.execution_mode.value})"
        )

        # Executar baseado no modo
        if self.execution_mode == HookExecutionMode.SEQUENTIAL:
            results = self._execute_sequential(hooks_to_execute, context)
        elif self.execution_mode == HookExecutionMode.PARALLEL:
            results = self._execute_parallel(hooks_to_execute, context)
        elif self.execution_mode == HookExecutionMode.WATERFALL:
            results = self._execute_waterfall(hooks_to_execute, context)
        elif self.execution_mode == HookExecutionMode.RACE:
            results = self._execute_race(hooks_to_execute, context)
        else:
            raise ValueError(f"Modo de execução inválido: {self.execution_mode}")

        # Calcular duração
        duration_ms = (time.perf_counter() - start_time) * 1000
        self._execution_stats["total_duration_ms"] += duration_ms

        # Atualizar estatísticas
        successful = all(r.status == HookResultStatus.SUCCESS for r in results)
        if successful:
            self._execution_stats["successful_executions"] += 1
        else:
            self._execution_stats["failed_executions"] += 1

        # Criar resultado final
        final_result = self._create_final_result(context, results, duration_ms)

        logger.info(
            f"Cadeia '{self.name}' executada em {duration_ms:.2f}ms: "
            f"{sum(1 for r in results if r.status == HookResultStatus.SUCCESS)}/"
            f"{len(results)} hooks bem-sucedidos"
        )

        return final_result

    def _get_sorted_hooks(self) -> list[HookChainDefinition]:
        """Retorna hooks habilitados ordenados por prioridade (maior primeiro)."""
        with self._lock:
            enabled_hooks = [
                hook for hook in self._hooks.values()
                if hook.enabled
            ]

        # Ordenar por prioridade (maior valor = maior prioridade)
        return sorted(enabled_hooks, key=lambda h: h.priority, reverse=True)

    def _execute_sequential(
        self,
        hooks: list[HookChainDefinition],
        context: HookChainContext
    ) -> list[HookExecutionResult]:
        """Executa hooks em sequência."""
        results = []

        for hook_def in hooks:
            result = self._execute_single_hook(hook_def, context)
            results.append(result)

            # Se hook falhou e não temos fallback, podemos parar a cadeia
            if result.status != HookResultStatus.SUCCESS and not hook_def.fallback_handler:
                logger.warning(f"Hook '{hook_def.name}' falhou, interrompendo cadeia sequencial")
                break

        return results

    def _execute_parallel(
        self,
        hooks: list[HookChainDefinition],
        context: HookChainContext
    ) -> list[HookExecutionResult]:
        """Executa hooks em paralelo."""
        # Criar cópias do contexto para cada hook (para evitar race conditions)
        contexts = [
            HookChainContext(
                event=context.event,
                initial_data=context.initial_data.copy(),
                current_data=context.current_data.copy(),
                metadata=context.metadata.copy(),
                execution_id=context.execution_id,
                created_at=context.created_at
            )
            for _ in hooks
        ]

        # Submeter todos os hooks para execução paralela
        futures = []
        for hook_def, hook_context in zip(hooks, contexts, strict=False):
            future = self._executor.submit(
                self._execute_single_hook,
                hook_def,
                hook_context
            )
            futures.append((hook_def.name, future, hook_def.timeout_seconds))

        # Coletar resultados
        results = []
        for hook_name, future, timeout in futures:
            try:
                result = future.result(timeout=timeout)
                results.append(result)
            except FutureTimeoutError:
                results.append(HookExecutionResult(
                    hook_name=hook_name,
                    status=HookResultStatus.TIMEOUT,
                    error=f"Timeout após {timeout} segundos",
                    duration_ms=timeout * 1000
                ))
            except Exception as e:
                results.append(HookExecutionResult(
                    hook_name=hook_name,
                    status=HookResultStatus.FAILED,
                    error=str(e),
                    duration_ms=0.0
                ))

        return results

    def _execute_waterfall(
        self,
        hooks: list[HookChainDefinition],
        context: HookChainContext
    ) -> list[HookExecutionResult]:
        """Executa hooks em waterfall (resultado de um alimenta o próximo)."""
        results = []
        current_context = context

        for hook_def in hooks:
            result = self._execute_single_hook(hook_def, current_context)
            results.append(result)

            # Se hook foi bem-sucedido, atualizar contexto com output
            if result.status == HookResultStatus.SUCCESS and result.output is not None:
                if isinstance(result.output, dict):
                    current_context.merge(result.output)
                else:
                    current_context.update(f"{hook_def.name}_output", result.output)

            # Se hook falhou e não temos fallback, parar a cadeia
            if result.status != HookResultStatus.SUCCESS and not hook_def.fallback_handler:
                logger.warning(f"Hook '{hook_def.name}' falhou, interrompendo cadeia waterfall")
                break

        return results

    def _execute_race(
        self,
        hooks: list[HookChainDefinition],
        context: HookChainContext
    ) -> list[HookExecutionResult]:
        """Executa hooks em race (primeiro que completar vence)."""
        # Criar cópias do contexto
        contexts = [
            HookChainContext(
                event=context.event,
                initial_data=context.initial_data.copy(),
                current_data=context.current_data.copy(),
                metadata=context.metadata.copy(),
                execution_id=context.execution_id,
                created_at=context.created_at
            )
            for _ in hooks
        ]

        # Submeter todos os hooks
        futures = []
        for hook_def, hook_context in zip(hooks, contexts, strict=False):
            future = self._executor.submit(
                self._execute_single_hook,
                hook_def,
                hook_context
            )
            futures.append((hook_def.name, future, hook_def.timeout_seconds))

        # Esperar pelo primeiro que completar
        done, _not_done = asyncio.wait(
            [asyncio.wrap_future(future) for _, future, _ in futures],
            return_when=asyncio.FIRST_COMPLETED
        )

        # Coletar resultado do vencedor
        winner_result = None
        winner_name = None

        for completed in done:
            try:
                result = completed.result()
                winner_result = result
                # Encontrar nome do hook vencedor
                for hook_name, future, _ in futures:
                    if future.done() and not future.cancelled():
                        winner_name = hook_name
                        break
                break
            except Exception:
                continue

        # Cancelar os outros hooks
        for _, future, _ in futures:
            if not future.done():
                future.cancel()

        # Criar resultados para todos os hooks
        results = []
        for hook_def in hooks:
            if hook_def.name == winner_name and winner_result:
                results.append(winner_result)
            else:
                results.append(HookExecutionResult(
                    hook_name=hook_def.name,
                    status=HookResultStatus.SKIPPED,
                    error="Cancelado (race mode)",
                    duration_ms=0.0
                ))

        return results

    def _execute_single_hook(
        self,
        hook_def: HookChainDefinition,
        context: HookChainContext
    ) -> HookExecutionResult:
        """Executa um único hook individual."""
        circuit_breaker = self._circuit_breakers[hook_def.name]

        # Verificar circuit breaker
        if not circuit_breaker.should_allow():
            logger.warning(f"Circuit breaker aberto para hook '{hook_def.name}'")
            return HookExecutionResult(
                hook_name=hook_def.name,
                status=HookResultStatus.CIRCUIT_BREAKER,
                error="Circuit breaker aberto",
                duration_ms=0.0
            )

        start_time = time.perf_counter()

        try:
            # Executar handler principal
            output = hook_def.handler(context)
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Registrar sucesso
            circuit_breaker.record_success()

            return HookExecutionResult(
                hook_name=hook_def.name,
                status=HookResultStatus.SUCCESS,
                output=output,
                duration_ms=duration_ms,
                metadata=hook_def.metadata
            )

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Registrar falha
            circuit_breaker.record_failure()

            # Tentar fallback se disponível
            if hook_def.fallback_handler:
                try:
                    fallback_output = hook_def.fallback_handler(context)
                    return HookExecutionResult(
                        hook_name=hook_def.name,
                        status=HookResultStatus.SUCCESS,
                        output=fallback_output,
                        duration_ms=duration_ms,
                        metadata={**hook_def.metadata, "used_fallback": True}
                    )
                except Exception as fallback_error:
                    logger.error(f"Fallback também falhou para hook '{hook_def.name}': {fallback_error}")

            return HookExecutionResult(
                hook_name=hook_def.name,
                status=HookResultStatus.FAILED,
                error=str(e),
                duration_ms=duration_ms,
                metadata=hook_def.metadata
            )

    def _create_empty_result(self, context: HookChainContext) -> dict[str, Any]:
        """Cria resultado vazio quando não há hooks para executar."""
        return {
            "chain_name": self.name,
            "execution_id": context.execution_id,
            "event": context.event.value,
            "results": [],
            "context": context.to_dict(),
            "stats": {
                "total_hooks": 0,
                "successful_hooks": 0,
                "failed_hooks": 0,
                "skipped_hooks": 0,
                "duration_ms": 0.0
            }
        }

    def _create_final_result(
        self,
        context: HookChainContext,
        results: list[HookExecutionResult],
        duration_ms: float
    ) -> dict[str, Any]:
        """Cria resultado final da execução da cadeia."""
        successful = sum(1 for r in results if r.status == HookResultStatus.SUCCESS)
        failed = sum(1 for r in results if r.status == HookResultStatus.FAILED)
        skipped = sum(1 for r in results if r.status == HookResultStatus.SKIPPED)

        return {
            "chain_name": self.name,
            "execution_id": context.execution_id,
            "event": context.event.value,
            "execution_mode": self.execution_mode.value,
            "results": [r.to_dict() for r in results],
            "context": context.to_dict(),
            "stats": {
                "total_hooks": len(results),
                "successful_hooks": successful,
                "failed_hooks": failed,
                "skipped_hooks": skipped,
                "duration_ms": duration_ms,
                "chain_success": failed == 0
            },
            "timestamp": datetime.now().isoformat()
        }

    def get_hooks(self) -> list[dict[str, Any]]:
        """Retorna lista de hooks na cadeia."""
        with self._lock:
            return [
                {
                    "name": hook.name,
                    "priority": hook.priority,
                    "timeout_seconds": hook.timeout_seconds,
                    "enabled": hook.enabled,
                    "circuit_breaker_threshold": hook.circuit_breaker_threshold,
                    "has_fallback": hook.fallback_handler is not None,
                    "metadata": hook.metadata
                }
                for hook in self._hooks.values()
            ]

    def get_stats(self) -> dict[str, Any]:
        """Retorna estatísticas da cadeia."""
        with self._lock:
            stats = self._execution_stats.copy()
            stats["average_duration_ms"] = (
                stats["total_duration_ms"] / stats["total_executions"]
                if stats["total_executions"] > 0 else 0.0
            )
            stats["success_rate"] = (
                stats["successful_executions"] / stats["total_executions"]
                if stats["total_executions"] > 0 else 0.0
            )
            return stats

    def get_circuit_breaker_states(self) -> dict[str, dict[str, Any]]:
        """Retorna estados de todos os circuit breakers."""
        return {
            name: cb.get_state()
            for name, cb in self._circuit_breakers.items()
        }

    def shutdown(self):
        """Desliga a cadeia de hooks e libera recursos."""
        self._executor.shutdown(wait=False)
        logger.info(f"Cadeia de hooks '{self.name}' desligada")


# ── Fábrica de cadeias de hooks ─────────────────────────────────────────────

class LexicoHookChainFactory:
    """Fábrica para criação e gerenciamento de cadeias de hooks."""

    def __init__(self):
        self._chains: dict[str, LexicoHookChain] = {}
        self._lock = threading.Lock()

    def create_chain(
        self,
        name: str,
        execution_mode: HookExecutionMode = HookExecutionMode.SEQUENTIAL,
        max_parallel_workers: int = 4
    ) -> LexicoHookChain:
        """Cria uma nova cadeia de hooks."""
        with self._lock:
            if name in self._chains:
                logger.warning(f"Cadeia '{name}' já existe, retornando existente")
                return self._chains[name]

            chain = LexicoHookChain(name, execution_mode, max_parallel_workers)
            self._chains[name] = chain
            logger.info(f"Cadeia de hooks '{name}' criada")
            return chain

    def get_chain(self, name: str) -> LexicoHookChain | None:
        """Obtém uma cadeia de hooks existente."""
        with self._lock:
            return self._chains.get(name)

    def remove_chain(self, name: str) -> bool:
        """Remove uma cadeia de hooks."""
        with self._lock:
            if name in self._chains:
                chain = self._chains[name]
                chain.shutdown()
                del self._chains[name]
                logger.info(f"Cadeia de hooks '{name}' removida")
                return True
            return False

    def list_chains(self) -> list[dict[str, Any]]:
        """Lista todas as cadeias de hooks."""
        with self._lock:
            return [
                {
                    "name": name,
                    "execution_mode": chain.execution_mode.value,
                    "hook_count": len(chain._hooks),
                    "stats": chain.get_stats()
                }
                for name, chain in self._chains.items()
            ]

    def execute_chain(
        self,
        chain_name: str,
        event: HookChainEvent,
        initial_data: dict[str, Any],
        execution_id: str | None = None
    ) -> dict[str, Any] | None:
        """Executa uma cadeia de hooks específica."""
        chain = self.get_chain(chain_name)
        if not chain:
            logger.error(f"Cadeia '{chain_name}' não encontrada")
            return None

        return chain.execute(event, initial_data, execution_id)

    def shutdown_all(self):
        """Desliga todas as cadeias de hooks."""
        with self._lock:
            for name, chain in self._chains.items():
                try:
                    chain.shutdown()
                except Exception as e:
                    logger.error(f"Erro ao desligar cadeia '{name}': {e}")

            self._chains.clear()
            logger.info("Todas as cadeias de hooks desligadas")


# ── Integração com neocortex_context ────────────────────────────────────────

def create_lexico_chains() -> LexicoHookChainFactory:
    """Cria fábrica de cadeias de hooks com configurações padrão."""
    factory = LexicoHookChainFactory()

    # Cadeia para análise lexical pré-processamento
    factory.create_chain(
        name="pre_lexical_analysis",
        execution_mode=HookExecutionMode.SEQUENTIAL
    )

    # Cadeia para pós-tokenização
    factory.create_chain(
        name="post_tokenization",
        execution_mode=HookExecutionMode.PARALLEL
    )

    # Cadeia para enriquecimento semântico
    factory.create_chain(
        name="semantic_enrichment",
        execution_mode=HookExecutionMode.WATERFALL
    )

    # Cadeia para compressão de contexto
    factory.create_chain(
        name="context_compression",
        execution_mode=HookExecutionMode.SEQUENTIAL
    )

    logger.info("Fábrica de cadeias de hooks lexicais criada com 4 cadeias padrão")
    return factory


# ── Singleton global ────────────────────────────────────────────────────────

_chain_factory_instance: LexicoHookChainFactory | None = None


def get_chain_factory() -> LexicoHookChainFactory:
    """Singleton da fábrica de cadeias de hooks."""
    global _chain_factory_instance
    if _chain_factory_instance is None:
        _chain_factory_instance = create_lexico_chains()
    return _chain_factory_instance


# ── Funções de conveniência ────────────────────────────────────────────────

def execute_pre_lexical_analysis(data: dict[str, Any]) -> dict[str, Any]:
    """Executa cadeia de análise lexical pré-processamento."""
    factory = get_chain_factory()
    return factory.execute_chain(
        "pre_lexical_analysis",
        HookChainEvent.PRE_LEXICAL_ANALYSIS,
        data
    ) or {}


def execute_post_tokenization(data: dict[str, Any]) -> dict[str, Any]:
    """Executa cadeia de pós-tokenização."""
    factory = get_chain_factory()
    return factory.execute_chain(
        "post_tokenization",
        HookChainEvent.POST_TOKENIZATION,
        data
    ) or {}


def execute_semantic_enrichment(data: dict[str, Any]) -> dict[str, Any]:
    """Executa cadeia de enriquecimento semântico."""
    factory = get_chain_factory()
    return factory.execute_chain(
        "semantic_enrichment",
        HookChainEvent.SEMANTIC_ENRICHMENT,
        data
    ) or {}


def execute_context_compression(data: dict[str, Any]) -> dict[str, Any]:
    """Executa cadeia de compressão de contexto."""
    factory = get_chain_factory()
    return factory.execute_chain(
        "context_compression",
        HookChainEvent.CONTEXT_COMPRESSION,
        data
    ) or {}


if __name__ == "__main__":
    # Teste básico
    import sys
    logging.basicConfig(level=logging.INFO)

    # Criar fábrica
    factory = create_lexico_chains()

    # Obter cadeia de pré-análise lexical
    chain = factory.get_chain("pre_lexical_analysis")

    if chain:
        # Adicionar alguns hooks de exemplo
        def example_hook1(context: HookChainContext) -> dict[str, Any]:
            return {"processed_by": "hook1", "timestamp": datetime.now().isoformat()}

        def example_hook2(context: HookChainContext) -> dict[str, Any]:
            data = context.get("processed_by", "unknown")
            return {"processed_by": "hook2", "previous": data}

        chain.add_hook("example1", example_hook1, priority=200)
        chain.add_hook("example2", example_hook2, priority=100)

        # Executar cadeia
        result = chain.execute(
            HookChainEvent.PRE_LEXICAL_ANALYSIS,
            {"text": "Exemplo de texto para análise"}
        )

        print(f"Resultado da execução: {result}")

        # Listar cadeias
        print(f"\nCadeias disponíveis: {factory.list_chains()}")

    factory.shutdown_all()
    sys.exit(0)
