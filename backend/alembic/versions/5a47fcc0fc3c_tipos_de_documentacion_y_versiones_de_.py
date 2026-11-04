"""tipos de documentacion y versiones de formato

Las dos tablas de la funcionalidad 002. Tres cosas no las puede generar
`--autogenerate` y por eso este archivo se escribió a mano sobre lo generado:

1. La clave foránea cruzada. `tipo_documentacion.version_vigente_id` apunta a
   `formato_version`, y `formato_version.tipo_id` apunta de vuelta. Declararla
   dentro del `CREATE TABLE` falla porque cada tabla necesita que la otra
   exista, así que se agrega con un `ALTER` después de crear las dos.
2. El índice único del nombre va sobre `lower(trim(nombre))` y no sobre
   `nombre`. Si fuera sobre la columna, «Adapter Reverso» y «adapter reverso»
   convivirían, y para el Administrador son el mismo tipo (RF-02).
3. El orden del `downgrade`: la FK cruzada se suelta antes de borrar las
   tablas, o PostgreSQL rechaza el `DROP`.

Revision ID: 5a47fcc0fc3c
Revises: 63097bc89826
Create Date: 2026-11-04 17:19:49.085821

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '5a47fcc0fc3c'
down_revision: Union[str, Sequence[str], None] = '63097bc89826'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

NOMBRE_FK_VERSION_VIGENTE = "fk_tipo_documentacion_version_vigente"
NOMBRE_INDICE_NOMBRE = "ux_tipo_documentacion_nombre_normalizado"


def upgrade() -> None:
    """Upgrade schema."""
    # Sin la FK a `formato_version`: esa tabla todavía no existe.
    op.create_table(
        "tipo_documentacion",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(length=200), nullable=False),
        sa.Column("descripcion", sa.String(length=1000), nullable=True),
        sa.Column(
            "desactivado", sa.Boolean(), server_default="false", nullable=False
        ),
        sa.Column("version_vigente_id", sa.Integer(), nullable=True),
        sa.Column(
            "creado_en",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "actualizado_en",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "formato_version",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tipo_id", sa.Integer(), nullable=False),
        sa.Column("numero", sa.Integer(), nullable=False),
        sa.Column("nombre_archivo_original", sa.String(length=255), nullable=False),
        sa.Column("extension", sa.String(length=5), nullable=False),
        sa.Column("tamano_bytes", sa.Integer(), nullable=False),
        sa.Column("hash_sha256", sa.CHAR(length=64), nullable=False),
        sa.Column("ruta_almacenada", sa.String(length=500), nullable=False),
        sa.Column(
            "estructura", postgresql.JSONB(astext_type=sa.Text()), nullable=False
        ),
        sa.Column(
            "creado_en",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["tipo_id"], ["tipo_documentacion.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tipo_id", "numero", name="uq_formato_version_tipo_numero"),
    )
    op.create_index(
        op.f("ix_formato_version_tipo_id"),
        "formato_version",
        ["tipo_id"],
        unique=False,
    )

    # Ahora que las dos tablas existen, la FK cruzada.
    op.create_foreign_key(
        NOMBRE_FK_VERSION_VIGENTE,
        "tipo_documentacion",
        "formato_version",
        ["version_vigente_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # La unicidad del nombre, normalizada para comparar pero no para guardar
    # (Art. II: el dato del usuario se guarda tal como lo escribió).
    op.create_index(
        NOMBRE_INDICE_NOMBRE,
        "tipo_documentacion",
        [sa.text("lower(trim(nombre))")],
        unique=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(NOMBRE_INDICE_NOMBRE, table_name="tipo_documentacion")
    # Primero la FK cruzada: con ella puesta, el DROP de cualquiera de las dos
    # tablas falla.
    op.drop_constraint(
        NOMBRE_FK_VERSION_VIGENTE, "tipo_documentacion", type_="foreignkey"
    )
    op.drop_index(op.f("ix_formato_version_tipo_id"), table_name="formato_version")
    op.drop_table("formato_version")
    op.drop_table("tipo_documentacion")
