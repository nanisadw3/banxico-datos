# Banxico al día

22 indicadores oficiales del Banco de México (tipo de cambio, divisas, tasas de interés, CETES,
inflación, UDIS y reservas), actualizados cada día hábil, con su histórico en CSV.

**Página en vivo: <https://banxico-mcp.duckdns.org/>**, con explicaciones sencillas y una lectura
del día que se redacta sola a partir de los datos.

| Indicador | Serie SIE | Frecuencia | CSV |
|---|---|---|---|
| Tipo de cambio FIX (pesos por dólar) | `SF43718` | diaria | [`tipo_cambio_fix.csv`](docs/data/tipo_cambio_fix.csv) |
| Tipo de cambio de liquidación (DOF) (pesos por dólar) | `SF60653` | diaria | [`tipo_cambio_liquidacion.csv`](docs/data/tipo_cambio_liquidacion.csv) |
| Euro (pesos por euro) | `SF46410` | diaria | [`euro.csv`](docs/data/euro.csv) |
| Libra esterlina (pesos por libra) | `SF46407` | diaria | [`libra.csv`](docs/data/libra.csv) |
| Yen japonés (pesos por yen) | `SF46406` | diaria | [`yen.csv`](docs/data/yen.csv) |
| Dólar canadiense (pesos por dólar canadiense) | `SF60632` | diaria | [`dolar_canadiense.csv`](docs/data/dolar_canadiense.csv) |
| Inflación anual (INPC) (%) | `SP30578` | mensual | [`inflacion_anual.csv`](docs/data/inflacion_anual.csv) |
| Inflación mensual (INPC) (%) | `SP30577` | mensual | [`inflacion_mensual.csv`](docs/data/inflacion_mensual.csv) |
| Inflación subyacente anual (%) | `SP74662` | mensual | [`inflacion_subyacente.csv`](docs/data/inflacion_subyacente.csv) |
| Inflación no subyacente anual (%) | `SP74665` | mensual | [`inflacion_no_subyacente.csv`](docs/data/inflacion_no_subyacente.csv) |
| Índice Nacional de Precios al Consumidor (índice) | `SP1` | mensual | [`inpc.csv`](docs/data/inpc.csv) |
| Valor de la UDI (pesos por UDI) | `SP68257` | diaria | [`udis.csv`](docs/data/udis.csv) |
| Tasa objetivo (%) | `SF61745` | diaria | [`tasa_objetivo.csv`](docs/data/tasa_objetivo.csv) |
| TIIE de fondeo a un día (%) | `SF331451` | diaria | [`tiie_fondeo.csv`](docs/data/tiie_fondeo.csv) |
| TIIE 28 días (%) | `SF43783` | diaria | [`tiie_28.csv`](docs/data/tiie_28.csv) |
| TIIE 91 días (%) | `SF43878` | diaria | [`tiie_91.csv`](docs/data/tiie_91.csv) |
| TIIE 182 días (%) | `SF111916` | diaria | [`tiie_182.csv`](docs/data/tiie_182.csv) |
| CETES 28 días (%) | `SF43936` | semanal | [`cetes_28.csv`](docs/data/cetes_28.csv) |
| CETES 91 días (%) | `SF43939` | semanal | [`cetes_91.csv`](docs/data/cetes_91.csv) |
| CETES 182 días (%) | `SF43942` | semanal | [`cetes_182.csv`](docs/data/cetes_182.csv) |
| CETES 364 días (%) | `SF43945` | semanal | [`cetes_364.csv`](docs/data/cetes_364.csv) |
| Reservas internacionales (millones de dólares) | `SF43707` | semanal | [`reservas.csv`](docs/data/reservas.csv) |

Cada CSV tiene dos columnas, `fecha` (AAAA-MM-DD) y `valor`, con histórico desde enero de 2024.

## Cómo se actualiza

Una GitHub Action ([`actualizar.yml`](.github/workflows/actualizar.yml)) corre de lunes a viernes a
las 19:45 y 23:30 UTC, después de que Banxico publica el FIX. Descarga los últimos 60 días de cada serie
(Banxico a veces corrige datos recientes), los mezcla con el histórico y hace commit **solo si algo
cambió**, firmado como `github-actions[bot]`. Un día sin publicaciones no genera commit, así que el
historial de commits es también el historial de publicaciones de Banxico.

El servidor de la página solo hace `git pull` de este repo; no necesita el token de Banxico.

## Correrlo en local

Necesitas un token gratuito del SIE: <https://www.banxico.org.mx/SieAPIRest/service/v1/token>

```bash
export BANXICO_TOKEN=tu_token
python3 scripts/actualizar.py                      # solo usa la biblioteca estándar
python3 -m http.server 8765 --directory docs       # y abre http://127.0.0.1:8765
```

## Relación con mcp-banxico

Usa las series de [mcp-banxico](https://github.com/nanisadw3/mcp-banxico), el servidor MCP que conecta
agentes de IA con Banxico; las que no tienen herramienta propia se consultan igual que con su
herramienta `consultar_serie_sie`. Si Banxico cambia un ID de serie, este repo deja de
actualizarse ese mismo día, y eso avisa que también hay que revisar el servidor.

---

Fuente: Banco de México, Sistema de Información Económica (SIE). Proyecto independiente,
no afiliado ni respaldado por el Banco de México. Hecho por [Iñaki Sobera](https://inakisobera.me).
