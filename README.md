# Voting API

API REST para gestionar un sistema de votaciones: registro de votantes y candidatos, emisión de votos (uno por votante) y estadísticas de resultados.

**Stack:** Python 3.12, FastAPI, SQLAlchemy 2 (async), PostgreSQL 16, Alembic, pytest, Docker Compose.

## Ejecución con Docker

```bash
cp .env.example .env
docker compose up --build
```

La API queda en `http://localhost:8000` y la documentación Swagger en `http://localhost:8000/docs`. Las migraciones se aplican al arrancar el contenedor.

Si el puerto 5432 ya está ocupado en tu máquina, agrega `POSTGRES_PORT=5433` al `.env`. Si además corres la API o los tests fuera de Docker, usa ese mismo puerto en `DATABASE_URL` y en `TEST_DATABASE_URL`.

## Ejecución local

Requiere Python 3.12 y un PostgreSQL accesible (se puede levantar solo la base con `docker compose up -d --wait db`).

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

## Tests

Los tests usan PostgreSQL (la base `voting_test` la crea el contenedor al iniciar). No uso SQLite porque los tests de concurrencia dependen de cómo Postgres bloquea las filas.

```bash
docker compose up -d --wait db
pytest
```

Para usar otra base: `TEST_DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db pytest`.

## Autenticación

Todos los endpoints excepto `/auth/token`, `/health` y `/docs` requieren un JWT. Las credenciales del administrador se configuran en `.env` (`ADMIN_USERNAME`, `ADMIN_PASSWORD`).

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/auth/token \
  -d "username=admin&password=admin123" | jq -r .access_token)
```

En Swagger se puede usar el botón **Authorize** con las mismas credenciales.

## Endpoints

| Método | Ruta | Descripción | Respuestas |
|---|---|---|---|
| POST | `/auth/token` | Obtener token | 200, 401 |
| POST | `/voters` | Registrar votante | 201, 409, 422 |
| GET | `/voters` | Listar votantes (`page`, `size`, `name`, `has_voted`) | 200 |
| GET | `/voters/{id}` | Detalle de votante | 200, 404 |
| DELETE | `/voters/{id}` | Eliminar votante | 204, 404, 409 |
| POST | `/candidates` | Registrar candidato | 201, 409, 422 |
| GET | `/candidates` | Listar candidatos (`page`, `size`, `name`, `party`) | 200 |
| GET | `/candidates/{id}` | Detalle de candidato | 200, 404 |
| DELETE | `/candidates/{id}` | Eliminar candidato | 204, 404, 409 |
| POST | `/votes` | Emitir voto | 201, 404, 409, 422 |
| GET | `/votes` | Listar votos (`page`, `size`) | 200 |
| GET | `/votes/statistics` | Estadísticas de la votación | 200 |

Los errores siempre tienen el formato `{"detail": "..."}`. Los listados devuelven `{"items": [...], "total": n, "page": p, "size": s}`.

## Ejemplos con curl

```bash
# Registrar un candidato
curl -X POST http://localhost:8000/candidates \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"name": "Laura Restrepo", "email": "laura.restrepo@example.com", "party": "Alianza Verde"}'

# Registrar un votante
curl -X POST http://localhost:8000/voters \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"name": "Ana Torres", "email": "ana.torres@example.com"}'

# Emitir un voto
curl -X POST http://localhost:8000/votes \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"voter_id": 1, "candidate_id": 1}'

# Intentar votar de nuevo -> 409 {"detail": "Voter has already voted"}
curl -X POST http://localhost:8000/votes \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"voter_id": 1, "candidate_id": 2}'

# Listar votantes que ya votaron, segunda página
curl "http://localhost:8000/voters?has_voted=true&page=2&size=5" -H "Authorization: Bearer $TOKEN"

# Estadísticas
curl http://localhost:8000/votes/statistics -H "Authorization: Bearer $TOKEN"
```

## Estadísticas

Con 3 candidatos, 10 votantes registrados y 8 votos emitidos:

![Respuesta de /votes/statistics](docs/img/statistics.png)

Documentación interactiva:

![Swagger UI](docs/img/swagger.png)

## Notas

- Le agregué `email` a `Candidate`. El modelo del enunciado no lo tiene, pero sin un dato en común no hay cómo validar que un votante no sea candidato (por nombre no sirve, puede haber dos personas con el mismo nombre).
- Para evitar votos dobles el voto hace `UPDATE voters SET has_voted = true WHERE id = ? AND has_voted = false`. Si no actualiza ninguna fila es porque ya votó y se responde 409. Así, si llegan dos requests al mismo tiempo, solo uno pasa. Además hay un `UNIQUE(voter_id)` en `votes`.
- Marcar al votante, sumar el voto al candidato e insertar el voto van en la misma transacción. Si el candidato no existe no queda nada a medias.
- Como el email tiene que ser único entre dos tablas, el registro toma un `pg_advisory_xact_lock` sobre el email antes de validar, para que dos registros simultáneos con el mismo email no pasen los dos.
- No se puede borrar un votante que ya votó ni un candidato con votos (409), porque las estadísticas dejarían de cuadrar.
- Las estadísticas se leen en `REPEATABLE READ` para que los totales salgan consistentes aunque entren votos mientras se calculan. Los porcentajes van con dos decimales y son 0 si no hay votos.
- Los emails se guardan en minúsculas y los nombres sin espacios de sobra. En los filtros, `%` y `_` se buscan literal.

## Estructura

```
app/
  api/        routers HTTP
  core/       configuración, base de datos, seguridad, errores
  models/     modelos SQLAlchemy
  schemas/    modelos Pydantic de entrada y salida
  services/   reglas de negocio
migrations/   migraciones Alembic
tests/        tests de integración
```
