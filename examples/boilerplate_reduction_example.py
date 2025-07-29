"""FLEXT API - Exemplo de redução drástica de boilerplate.

Demonstra como usar flext-core com prefixos corretos para
eliminar códigos repetitivos em APIs enterprise.
"""

from __future__ import annotations

from flext_core import (
    FlextContainerMixin,
    FlextLoggerMixin,
    FlextResult,
    flext_fail,
    flext_get_service,
    flext_ok,
    flext_pipeline,
    flext_register,
    flext_safe,
)

# =============================================================================
# ANTES: Muito boilerplate
# =============================================================================


class OldAPIService:
    """Exemplo do jeito antigo - muito boilerplate."""

    def __init__(self) -> None:
        self._logger = None
        self._container = None

    def get_logger(self):
        if not self._logger:
            import logging

            self._logger = logging.getLogger(__name__)
        return self._logger

    def process_request(self, data: dict) -> dict:
        try:
            # Validação manual
            if not data:
                return {"success": False, "error": "No data provided"}
            if "user_id" not in data:
                return {"success": False, "error": "Missing user_id"}

            # Processamento com muito try/catch
            result = self._do_processing(data)
            return {"success": True, "data": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _do_processing(self, data: dict) -> dict:
        # Simula processamento
        return {"processed": True, "user_id": data["user_id"]}


# =============================================================================
# DEPOIS: Zero boilerplate com flext-core
# =============================================================================


class NewAPIService(FlextContainerMixin, FlextLoggerMixin):
    """Exemplo novo - zero boilerplate usando flext-core."""

    @flext_safe
    def process_request(self, data: dict) -> FlextResult[dict]:
        """Processamento com zero boilerplate."""
        return (
            flext_pipeline(data)
            .validate(self._validate_data)
            .then(self._process_data)
            .then(self._format_response)
            .result()
        )

    def _validate_data(self, data: dict) -> FlextResult[dict]:
        """Validação fluent."""
        if not data:
            return flext_fail("No data provided")
        if "user_id" not in data:
            return flext_fail("Missing user_id")
        return flext_ok(data)

    def _process_data(self, data: dict) -> FlextResult[dict]:
        """Processamento sem try/catch."""
        return flext_ok({"processed": True, "user_id": data["user_id"]})

    def _format_response(self, data: dict) -> FlextResult[dict]:
        """Formatação final."""
        return flext_ok({"success": True, "data": data})


# =============================================================================
# EXEMPLO DE USO
# =============================================================================


def demonstrate_boilerplate_reduction() -> None:
    """Demonstra a redução de boilerplate."""
    # Configuração com zero boilerplate
    flext_register("api_service", NewAPIService())

    # Uso fluent
    service_result = flext_get_service("api_service")
    if service_result.is_success:
        service = service_result.data

        # Processamento com pipeline fluent
        result = service.process_request({"user_id": "123"})

        if result.is_success:
            pass

    # Comparação de linhas de código


if __name__ == "__main__":
    demonstrate_boilerplate_reduction()
