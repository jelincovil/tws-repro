# src/scripts/

Este directorio está reservado para scripts auxiliares del paquete de experimentos.

## Estado actual

Vacío. Los scripts principales de validación viven en `src/tws_validation/`.

## Scripts que podrían ir aquí

- `generate_synthetic_fields.py` — generación de campos sintéticos para experimentos
- `batch_compare.py` — comparación batch de múltiples configuraciones
- `plot_results.py` — generación de figuras desde CSVs de resultados

## Referencia

- Módulos principales: `src/tws_validation/`
- Resultados: `results/csv/`, `results/figures/`
- Parámetros: no hay archivo de configuración. Los valores por defecto viven en
  las firmas de las funciones y en los `argparse` de cada módulo; los valores
  canónicos que producen los números del manuscrito están fijados en
  `src/tws_validation/run_all.py` y replicados en el `Makefile`.
  (El antiguo `configs/default_config.yaml` fue eliminado: ningún módulo lo
  leía y contradecía al código.)
