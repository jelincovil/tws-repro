# formalization/docs/

Documentación auxiliar de la formalización en Lean 4.

## Contenido

| Fichero | Qué es |
|---------|--------|
| `axioms_audit.txt` | Salida literal de `#print axioms` sobre las declaraciones exportadas de `TWS/BoundComposition.lean` y `TWS/DaubechiesOpNorm.lean`. |

`axioms_audit.txt` no se edita a mano. Se regenera con

```bash
./scripts/print_axioms.sh docs/axioms_audit.txt
```

El fichero debe coincidir carácter a carácter con lo que imprime

```bash
lake env lean scripts/print_axioms.lean
```

La auditoría comprueba que cada teorema depende únicamente de
`propext`, `Classical.choice` y `Quot.sound` (o de un subconjunto de esos
tres). Cualquier nombre adicional —en particular `sorryAx`— hace fallar
`print_axioms.sh`. El esqueleto histórico en `archive/` no forma parte del
target `TWS` y no se audita.

Última verificación: 2026-10-21. El bloque literal fue regenerado con
`./scripts/print_axioms.sh docs/axioms_audit.txt`; las 25 declaraciones
auditadas solo dependen de los tres axiomas estándar.

## Mapa paper ↔ Lean

La tabla «Resultado matemático → declaración Lean → hipótesis recibidas →
contenido demostrado → contenido no formalizado» vive en
`../README.md`.  Resume:

- composición abstracta y su especialización localizada: formalizadas;
- identidades del filtro `db2`: formalizadas como álgebra finita;
- estabilidad de bottleneck, paisajes, proyección de marco y energía de
  Besov: argumentos matemáticos externos, no formalizados;
- experimentos numéricos: no formalizados.

## Referencia

- Overview y cómo ejecutar: `../README.md`
- Código fuente: `../TWS/BoundComposition.lean`, `../TWS/DaubechiesOpNorm.lean`
- Esqueleto histórico: `../archive/Skeleton_v2_historical.lean`
- Auditoría archivada: `axioms_audit.txt`
