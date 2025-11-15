# 🏦 Interbank ETL Pipeline - Prefect

Este repositorio contiene la orquestación de pipelines ETL para el proyecto Interbank utilizando **Prefect** como motor de flujo de trabajo y **Azure Synapse Analytics** como plataforma de procesamiento de datos.

## 📋 Propósito

El objetivo principal de este proyecto es automatizar y orquestar la ejecución secuencial de pipelines de datos que procesan información financiera y operativa desde diferentes fuentes hacia la arquitectura de datos en capas (Bronze, Silver, Gold) alojada en Azure.

## 🎯 Funcionalidades

- **Orquestación de Pipelines**: Ejecuta de manera secuencial múltiples pipelines de Synapse en la capa Bronze
- **Autenticación Azure**: Utiliza credenciales interactivas del navegador para acceder a los recursos de Azure Synapse
- **Monitoreo y Logging**: Implementa logging detallado usando Prefect para rastrear el estado de cada pipeline
- **Manejo de Errores**: Incluye reintentos automáticos (3 intentos) y detención del flujo en caso de fallas
- **Polling Inteligente**: Espera y monitorea el estado de cada pipeline hasta su finalización

## 📦 Pipelines Incluidos

### Capa Bronze (Datos Crudos)

#### Núcleo Financiero (Core)
- `copy_core_account_to_bronze`: Ingesta de cuentas bancarias
- `copy_core_customer_to_bronze`: Ingesta de información de clientes
- `copy_core_transaction_to_bronze2`: Ingesta de transacciones financieras

#### Operaciones y Observabilidad
- `copy_ops_app_log_to_bronze`: Ingesta de logs de aplicación
- `copy_ops_infra_metric_to_bronze`: Ingesta de métricas de infraestructura

## 🏗️ Arquitectura

```
┌─────────────────┐
│  Prefect Flow   │
│  (Orquestador)  │
└────────┬────────┘
         │
         ├─► Pipeline 1: Cuentas → Bronze
         ├─► Pipeline 2: Clientes → Bronze
         ├─► Pipeline 3: Transacciones → Bronze
         ├─► Pipeline 4: Logs → Bronze
         └─► Pipeline 5: Métricas → Bronze
                    │
                    ▼
         ┌──────────────────────┐
         │  Azure Synapse       │
         │  (syn-interbank-lake)│
         └──────────────────────┘
```

## 🚀 Requisitos

- Python 3.8+
- Prefect
- Azure Identity
- Requests
- Acceso configurado a Azure Synapse Workspace: `syn-interbank-lake`

## 📥 Instalación

```bash
pip install prefect azure-identity requests
```

## 🔧 Configuración

Antes de ejecutar el flujo, asegúrate de:

1. Tener acceso al workspace de Synapse: `syn-interbank-lake`
2. Configurar las credenciales de Azure (se abrirá un navegador para autenticación interactiva)
3. Verificar que los pipelines listados existan en tu workspace de Synapse

## ▶️ Uso

### Ejecución Manual

```bash
python flows/interbank_etl.py
```

### Ejecución con Prefect

```bash
prefect deployment build flows/interbank_etl.py:etl_interbank_bronce -n interbank-bronze
prefect deployment apply etl_interbank_bronce-deployment.yaml
```

## 📊 Monitoreo

El flujo proporciona información detallada durante la ejecución:
- Estado de lanzamiento de cada pipeline
- RunId de cada ejecución
- Polling del estado cada 30 segundos
- Mensaje de éxito o error al finalizar

## ⚠️ Manejo de Errores

- **Reintentos**: Cada pipeline tiene 3 intentos automáticos con 10 segundos de espera entre intentos
- **Detención en falla**: Si un pipeline falla, el flujo completo se detiene y reporta el error
- **Estados monitoreados**: Succeeded, Failed, Cancelled

## 🔮 Evolución Futura

Este repositorio está diseñado para crecer y soportar:
- Pipelines de capa Silver (datos refinados)
- Pipelines de capa Gold (datos agregados)
- Cálculo de KPIs operativos (MTTD, MTTR)
- Notificaciones y alertas
- Integración con sistemas de monitoreo

## 📝 Estructura del Proyecto

```
interbank-prefect/
├── flows/
│   └── interbank_etl.py    # Flujo principal de orquestación
└── README.md               # Este archivo
```

## 🤝 Contribución

Para contribuir a este proyecto:
1. Crea una rama con tu funcionalidad
2. Asegúrate de mantener el logging detallado
3. Prueba los pipelines en un ambiente de desarrollo
4. Documenta cualquier cambio en la configuración

## 📄 Licencia

Proyecto interno de Interbank.

---

**Mantenido por**: Equipo de Data Engineering - Interbank
