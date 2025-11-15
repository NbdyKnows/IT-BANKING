from __future__ import annotations

import time
from typing import Dict, List, Optional

import requests
from azure.identity import InteractiveBrowserCredential
from prefect import flow, task, get_run_logger

# ====== CONFIGURACIÓN BÁSICA ======

# Cambia por el nombre real de tu workspace Synapse
SYNAPSE_WORKSPACE = "syn-interbank-lake"

# Lista de pipelines que quieres lanzar en orden
PIPELINES_BRONZE: List[str] = [
    # Núcleo financiero (core)
    "copy_core_account_to_bronze",        # cuentas → bronze
    "copy_core_customer_to_bronze",       # clientes → bronze
    #"copy_core_transaction_to_bronze",    # transacciones → bronze
    "copy_core_transaction_to_bronze2",    # transacciones → bronze

    # Operaciones / observabilidad
    "copy_ops_app_log_to_bronze",         # logs de aplicación → bronze
    "copy_ops_infra_metric_to_bronze",    # métricas de infraestructura → bronze
]

# Versión del API de Synapse (data plane)
SYNAPSE_API_VERSION = "2020-12-01"

# Credencial que usará DefaultAzureCredential (toma token del CLI, etc.)
credential = InteractiveBrowserCredential()


def _get_synapse_token() -> str:
    """Obtiene un token de acceso para Synapse usando DefaultAzureCredential."""
    # Scope para Synapse data plane
    scope = "https://dev.azuresynapse.net/.default"
    token = credential.get_token(scope)
    return token.token


@task(retries=3, retry_delay_seconds=10)
def lanzar_pipeline_synapse(pipeline_name: str,
                            parameters: Optional[Dict] = None) -> str:
    """
    Lanza un pipeline de Synapse vía REST y devuelve el runId.
    """
    logger = get_run_logger()
    logger.info(f"Lanzando pipeline Synapse: {pipeline_name}")

    token = _get_synapse_token()

    endpoint = f"https://{SYNAPSE_WORKSPACE}.dev.azuresynapse.net"
    url = f"{endpoint}/pipelines/{pipeline_name}/createRun"
    params = {"api-version": SYNAPSE_API_VERSION}

    # En Synapse, el body es un JSON con los parámetros (si no hay, mandamos {})
    body = parameters or {}

    resp = requests.post(
        url,
        params=params,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json=body,
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()
    run_id = data.get("runId")
    logger.info(f"Pipeline {pipeline_name} lanzado. runId={run_id}")
    return run_id


@task
def esperar_pipeline_synapse(run_id: str) -> str:
    """
    Hace polling al estado de un run hasta que termina.
    Devuelve el estado final (Succeeded, Failed, Cancelled, etc.).
    """
    logger = get_run_logger()
    token = _get_synapse_token()

    endpoint = f"https://{SYNAPSE_WORKSPACE}.dev.azuresynapse.net"
    url = f"{endpoint}/pipelineruns/{run_id}"
    params = {"api-version": SYNAPSE_API_VERSION}

    while True:
        resp = requests.get(
            url,
            params=params,
            headers={"Authorization": f"Bearer {token}"},
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        status = data.get("status")
        message = data.get("message")

        logger.info(f"Run {run_id} → status={status} | msg={message}")

        if status in {"Succeeded", "Failed", "Cancelled"}:
            return status

        # Espera 30 segundos y vuelve a consultar
        time.sleep(30)


@flow(name="interbank_etl_bronce")
def etl_interbank_bronce():
    """
    Orquesta la ejecución secuencial de los pipelines de Bronce.
    Aquí luego podemos añadir pasos para Plata/Oro o KPIs (MTTD/MTTR).
    """
    logger = get_run_logger()
    logger.info("Iniciando ETL Interbank → Zona Bronce")

    for pipeline_name in PIPELINES_BRONZE:
        logger.info(f"=== Ejecutando pipeline: {pipeline_name} ===")
        run_id = lanzar_pipeline_synapse(pipeline_name)
        status = esperar_pipeline_synapse(run_id)

        if status != "Succeeded":
            logger.error(
                f"Pipeline {pipeline_name} terminó en estado {status}. "
                "Deteniendo flujo."
            )
            raise RuntimeError(
                f"Error en pipeline {pipeline_name}, estado={status}"
            )

    logger.info("Todos los pipelines de Bronce terminaron OK ✅")


if __name__ == "__main__":
    # Permite correrlo manualmente para probar
    etl_interbank_bronce()
