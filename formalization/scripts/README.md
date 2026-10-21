# formalization/scripts/

Scripts auxiliares para la formalización en Lean 4.

## Contenido

| Fichero | Qué hace |
|---------|----------|
| `check_all.sh` | `lake exe cache get` + `lake build` + auditoría de `sorry`, `admit` y declaraciones `axiom` explícitas en las fuentes de la librería. |
| `print_axioms.sh` | Envoltorio de la auditoría de axiomas. Comprueba que no aparezca ningún axioma fuera de `propext`, `Classical.choice`, `Quot.sound`. Con argumento, archiva la salida. |
| `print_axioms.lean` | Fichero Lean con los `#print axioms` de las declaraciones exportadas de `BoundComposition` y `DaubechiesOpNorm`. |

## Uso

```bash
# desde formalization/ (en Windows, desde la copia de ruta corta:
# ver «Windows: build from a short path» en ../README.md)
./scripts/check_all.sh
./scripts/print_axioms.sh docs/axioms_audit.txt
```

`print_axioms.lean` **se elabora, no se ejecuta**. La invocación correcta es

```bash
lake env lean scripts/print_axioms.lean
```

`lake env lean --run scripts/print_axioms.lean` es incorrecto: `--run` espera
un `def main` ejecutable y aquí falla.

## Salida esperada

`check_all.sh` termina en:

```
real sorry count: 0
real admit count: 0
explicit axiom declarations: 0
RESULT: BUILD OK
```

Cualquier recuento distinto de 0 es una regresión. El filtro descarta la
prosa de los docstrings: ocurrencias entre acentos graves (`` `sorry` ``,
`` `sorryAx` ``), identificadores que lo contienen (`sorryAx`) y guionizados
(`sorry-free`). El directorio `archive/` queda fuera de la auditoría porque
no pertenece al target `TWS`.

`print_axioms.sh` debe reproducir exactamente el bloque literal archivado en
`docs/axioms_audit.txt` y termina con

```
axiom audit: only [propext, Classical.choice, Quot.sound] (or subsets).
```

## Referencia

- Comando principal: `lake build` (desde `formalization/`)
- Código fuente: `TWS/BoundComposition.lean`, `TWS/DaubechiesOpNorm.lean`
- Esqueleto histórico: `archive/Skeleton_v2_historical.lean`
- Auditoría archivada: `../docs/axioms_audit.txt`
- Makefile: `make lean` desde la raíz hace `cd formalization && lake build`;
  en Windows falla por `MAX_PATH`, hay que usar la copia de ruta corta.
