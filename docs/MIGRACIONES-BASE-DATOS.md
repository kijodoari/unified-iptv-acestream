# Migraciones de Base de Datos

## 📋 Descripción

Este proyecto usa **Alembic** para gestionar las migraciones de base de datos de forma profesional y automática.

## 🚀 Funcionamiento Automático

Las migraciones se ejecutan **automáticamente** cada vez que inicias el servidor:

```bash
docker-compose up -d
```

El servidor detecta si hay migraciones pendientes y las aplica antes de iniciar.

## 📁 Estructura de Migraciones

```
unified-iptv-acestream/
├── alembic/                    # Directorio de migraciones
│   ├── versions/               # Archivos de migración
│   │   ├── 001_initial_schema.py
│   │   ├── 002_add_external_url_setting.py
│   │   └── ...
│   ├── env.py                  # Configuración de entorno
│   └── script.py.mako          # Template para nuevas migraciones
├── alembic.ini                 # Configuración de Alembic
└── migrate.py                  # Script de gestión de migraciones
```

## 🛠️ Comandos Manuales

### Ver Estado Actual

```bash
# Dentro del contenedor
docker-compose exec unified-acestream python migrate.py current

# Fuera del contenedor (local)
python migrate.py current
```

### Ver Historial de Migraciones

```bash
docker-compose exec unified-acestream python migrate.py history
```

### Aplicar Migraciones Manualmente

```bash
docker-compose exec unified-acestream python migrate.py upgrade
```

### Revertir Última Migración

```bash
docker-compose exec unified-acestream python migrate.py downgrade
```

### Marcar Base de Datos como Actualizada (sin ejecutar migraciones)

```bash
docker-compose exec unified-acestream python migrate.py stamp head
```

## 📝 Crear Nueva Migración

### 1. Modificar los Modelos

Edita los modelos en `app/models/__init__.py`:

```python
# Ejemplo: Añadir nueva columna
class Channel(Base):
    __tablename__ = "channels"
    
    # ... columnas existentes ...
    
    # Nueva columna
    new_field = Column(String(255), nullable=True)
```

### 2. Generar Migración Automáticamente

```bash
# Dentro del contenedor
docker-compose exec unified-acestream alembic revision --autogenerate -m "Add new_field to channels"

# Fuera del contenedor (local)
alembic revision --autogenerate -m "Add new_field to channels"
```

Esto creará un nuevo archivo en `alembic/versions/` con el código de migración.

### 3. Revisar y Editar la Migración

Abre el archivo generado y revisa que los cambios sean correctos:

```python
def upgrade() -> None:
    # Añadir columna
    with op.batch_alter_table('channels', schema=None) as batch_op:
        batch_op.add_column(sa.Column('new_field', sa.String(length=255), nullable=True))


def downgrade() -> None:
    # Eliminar columna
    with op.batch_alter_table('channels', schema=None) as batch_op:
        batch_op.drop_column('new_field')
```

### 4. Aplicar la Migración

```bash
# Reiniciar el servidor (aplica automáticamente)
docker-compose restart

# O aplicar manualmente
docker-compose exec unified-acestream python migrate.py upgrade
```

## 🔄 Flujo de Trabajo Completo

### Cuando Modificas el Esquema de Base de Datos:

1. **Modificar modelos** en `app/models/__init__.py`
2. **Generar migración**:
   ```bash
   docker-compose exec unified-acestream alembic revision --autogenerate -m "Descripción del cambio"
   ```
3. **Revisar migración** generada en `alembic/versions/`
4. **Compilar y reiniciar**:
   ```bash
   docker-compose down
   docker-compose build
   docker-compose up -d
   ```
5. **Verificar** que la migración se aplicó correctamente

## 📊 Migraciones Actuales

### 001 - Initial Schema (25/01/2026)
- Creación de todas las tablas iniciales
- Tablas: categories, channels, users, epg_programs, epg_sources, scraper_urls, settings
- Índices y relaciones

### 002 - Add External URL Setting (25/01/2026)
- Añadido setting `external_url` para acceso remoto
- Permite configurar dominio externo para URLs de M3U/EPG

## ⚠️ Importante para SQLite

Este proyecto usa SQLite, que tiene limitaciones para modificar tablas. Por eso usamos `batch_alter_table`:

```python
# ✅ CORRECTO para SQLite
with op.batch_alter_table('table_name', schema=None) as batch_op:
    batch_op.add_column(sa.Column('new_column', sa.String(255)))

# ❌ INCORRECTO para SQLite (puede fallar)
op.add_column('table_name', sa.Column('new_column', sa.String(255)))
```

## 🔍 Solución de Problemas

### Error: "Can't locate revision identified by 'XXX'"

La base de datos no está marcada con ninguna revisión. Solución:

```bash
# Marcar la base de datos con la revisión actual
docker-compose exec unified-acestream python migrate.py stamp head
```

### Error: "Target database is not up to date"

Hay migraciones pendientes. Solución:

```bash
# Aplicar migraciones pendientes
docker-compose exec unified-acestream python migrate.py upgrade
```

### Error: "FAILED: Multiple head revisions are present"

Hay conflicto entre migraciones. Solución:

```bash
# Ver las revisiones conflictivas
docker-compose exec unified-acestream python migrate.py history

# Resolver manualmente o crear migración de merge
docker-compose exec unified-acestream alembic merge -m "Merge heads" head1 head2
```

### Resetear Base de Datos Completamente

⚠️ **CUIDADO**: Esto borrará todos los datos.

```bash
# Detener el servidor
docker-compose down

# Borrar la base de datos
rm data/unified-acestream.db

# Iniciar el servidor (creará nueva BD con migraciones)
docker-compose up -d
```

## 📚 Recursos

- [Documentación de Alembic](https://alembic.sqlalchemy.org/)
- [Tutorial de Alembic](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [Batch Operations (SQLite)](https://alembic.sqlalchemy.org/en/latest/batch.html)

## 🎯 Buenas Prácticas

1. **Siempre revisar** las migraciones autogeneradas antes de aplicarlas
2. **Probar en desarrollo** antes de aplicar en producción
3. **Hacer backup** de la base de datos antes de migraciones importantes
4. **Documentar** los cambios en el mensaje de la migración
5. **Usar batch_alter_table** para SQLite
6. **No modificar** migraciones ya aplicadas (crear nueva migración)

## 🔐 Seguridad

- Las migraciones se ejecutan con los mismos permisos que la aplicación
- No incluir datos sensibles en las migraciones
- Revisar las migraciones autogeneradas por seguridad

---

**Última actualización**: 25 de enero de 2026
