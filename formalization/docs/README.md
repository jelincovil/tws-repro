# formalization/docs/

Documentación auxiliar de la formalización en Lean 4.

## Contenido

| Fichero | Qué es |
|---------|--------|
| `axioms_audit.txt` | Salida literal de `#print axioms` sobre las cinco declaraciones exportadas, con toolchain, revisión de mathlib y lectura del resultado. |

`axioms_audit.txt` no se edita a mano. Se regenera con

```bash
./scripts/print_axioms.sh docs/axioms_audit.txt
```

y luego se restituye la prosa de cabecera alrededor del bloque literal. El
bloque debe coincidir carácter a carácter con lo que imprime

```bash
lake env lean scripts/print_axioms.lean
```

Verificado por última vez el 2026-09-10: el bloque literal coincide con
`./scripts/print_axioms.sh`; `sorry` count 0; ningún `sorryAx`.

## Documentación que podría ir aquí

- Diagrama de dependencias entre hipótesis y teoremas
- Mapeo paper ↔ Lean (qué definición del paper corresponde a qué declaración
  Lean); hoy ese mapeo vive en la tabla «Key declarations» de
  `../README.md`

## Referencia

- Overview y cómo ejecutar: `../README.md`
- Código fuente con docstrings: `../TWS/Skeleton.lean`
- Guía de instalación: `../../docs/SETUP.md`
