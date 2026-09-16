# formalization/scripts/

Scripts auxiliares para la formalización en Lean 4.

## Contenido

| Fichero | Qué hace |
|---------|----------|
| `check_all.sh` | `lake exe cache get` + `lake build` + auditoría de `sorry`. Sale con el código de `lake build`. |
| `print_axioms.sh` | Envoltorio de la auditoría de axiomas. Con argumento, además archiva la salida en ese fichero. |
| `print_axioms.lean` | Fichero Lean con los `#print axioms` de las cinco declaraciones exportadas. |

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
un `def main` ejecutable y aquí falla. Ese error estuvo en `lean_check.yml`.

## Salida esperada

`check_all.sh` termina en:

```
real sorry count: 0
RESULT: BUILD OK
```

`real sorry count` distinto de 0 es una regresión. El filtro descarta la prosa
de los docstrings: ocurrencias entre acentos graves (`` `sorry` ``, `` `sorryAx` ``),
identificadores que lo contienen (`sorryAx`) y guionizados (`sorry-free`).

`print_axioms.sh` debe reproducir exactamente el bloque literal archivado en
`docs/axioms_audit.txt`.

## Referencia

- Comando principal: `lake build` (desde `formalization/`)
- Código fuente: `TWS/Skeleton.lean`
- Auditoría archivada: `../docs/axioms_audit.txt`
- Makefile: `make lean` desde `tws-persistence-stability/` hace
  `cd formalization && lake build`; en Windows falla por `MAX_PATH`, hay que
  usar la copia de ruta corta.
