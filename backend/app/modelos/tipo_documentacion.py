"""Modelos de los tipos de documentación y de las versiones de su formato.

Un tipo de documentación es una clase de documento que la plataforma sabe
generar; su formato es el archivo que cargó el Administrador y que define la
estructura del documento (Art. I).

Las dos tablas se apuntan mutuamente: una versión pertenece a un tipo, y el
tipo señala **cuál** de sus versiones es la vigente. Esa segunda referencia es
lo que hace imposible que dos versiones se declaren vigentes a la vez.
"""

from datetime import datetime

from sqlalchemy import (
    CHAR,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.bd import Base

# Los tres estados posibles de un tipo (RF-03). No son una columna: se derivan.
ESTADO_INCOMPLETO = "incompleto"
ESTADO_ACTIVO = "activo"
ESTADO_DESACTIVADO = "desactivado"


class TipoDocumentacion(Base):
    """Una clase de documento que la plataforma sabe generar."""

    __tablename__ = "tipo_documentacion"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Se guarda tal como lo escribió el Administrador (Art. II: no se normaliza
    # el dato del usuario). Lo que se normaliza es la comparación: la unicidad
    # la impone un índice sobre `lower(trim(nombre))` que crea la migración, no
    # un `unique=True` sobre la columna, porque «Adapter Reverso» y «adapter
    # reverso» son el mismo tipo para quien administra (RF-02).
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)

    descripcion: Mapped[str | None] = mapped_column(
        String(1000), nullable=True, default=None
    )

    # Decisión del Administrador, no deducible de nada: por eso sí se guarda
    # (RF-14). Desactivar no borra: el tipo y su historial siguen ahí.
    desactivado: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )

    # Sin versión vigente el tipo está incompleto y ningún RO lo ve (RF-16,
    # RF-19). `use_alter` deja que Alembic agregue esta FK con un ALTER
    # posterior: declararla dentro del CREATE falla porque cada tabla necesita
    # que la otra exista.
    version_vigente_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey(
            "formato_version.id",
            ondelete="SET NULL",
            use_alter=True,
            name="fk_tipo_documentacion_version_vigente",
        ),
        nullable=True,
        default=None,
    )

    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Todo el historial del tipo, de la versión más vieja a la más nueva. Se
    # borra con el tipo, que solo se puede borrar mientras está incompleto
    # (RF-15).
    versiones: Mapped[list["FormatoVersion"]] = relationship(
        back_populates="tipo",
        cascade="all, delete-orphan",
        foreign_keys="FormatoVersion.tipo_id",
        order_by="FormatoVersion.numero",
    )

    # La vigente, que es una de `versiones`. Se declara aparte porque la
    # relación va por la otra clave foránea, la que sale de esta tabla.
    version_vigente: Mapped["FormatoVersion | None"] = relationship(
        foreign_keys=[version_vigente_id],
        post_update=True,
    )

    @property
    def estado(self) -> str:
        """El estado del tipo (RF-03), derivado y no almacenado.

        El orden de las condiciones es la precedencia de `data-model.md`: un
        tipo desactivado que nunca tuvo formato se muestra como desactivado.

        Se deriva a propósito. Con una columna `estado` existiría el estado
        imposible «activo sin formato vigente», y habría que mantener
        sincronizados dos datos que dicen lo mismo.
        """
        if self.desactivado:
            return ESTADO_DESACTIVADO
        if self.version_vigente_id is None:
            return ESTADO_INCOMPLETO
        return ESTADO_ACTIVO

    @property
    def disponible_para_ro(self) -> bool:
        """Si un RO puede elegir este tipo (RF-16)."""
        return self.estado == ESTADO_ACTIVO

    def __repr__(self) -> str:
        return f"<TipoDocumentacion {self.nombre!r} ({self.estado})>"


class FormatoVersion(Base):
    """Una versión del formato de un tipo.

    Las versiones **solo se insertan**: no se borran ni se editan. Es lo que
    sostiene el Art. IX, porque una versión es el registro de qué estructura
    estaba vigente en un momento, y reescribirla borraría la trazabilidad del
    documento que se generó con ella (RF-21).
    """

    __tablename__ = "formato_version"
    __table_args__ = (
        # El número de versión es de cada tipo: los dos empiezan en 1 (RF-21).
        UniqueConstraint("tipo_id", "numero", name="uq_formato_version_tipo_numero"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    tipo_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tipo_documentacion.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    numero: Mapped[int] = mapped_column(Integer, nullable=False)

    # Tal como lo trajo el archivo, para que el Administrador reconozca cuál
    # cargó (RF-20). No es el nombre con el que se guarda en disco.
    nombre_archivo_original: Mapped[str] = mapped_column(String(255), nullable=False)

    extension: Mapped[str] = mapped_column(String(5), nullable=False)
    tamano_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    hash_sha256: Mapped[str] = mapped_column(CHAR(64), nullable=False)

    # **Relativa** al almacén configurado, nunca absoluta: una ruta absoluta en
    # la base rompe el sistema en cuanto se mueve el almacén, se despliega en
    # otra máquina o se trabaja en un worktree con otra configuración.
    ruta_almacenada: Mapped[str] = mapped_column(String(500), nullable=False)

    # La estructura reconocida, con la forma de `data-model.md`. Es la misma
    # venga de la lectura del archivo o de la propuesta de la IA: nada aquí
    # distingue su origen, a propósito.
    estructura: Mapped[dict] = mapped_column(JSONB, nullable=False)

    # El «desde cuándo» del historial (RF-21).
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    tipo: Mapped["TipoDocumentacion"] = relationship(
        back_populates="versiones",
        foreign_keys=[tipo_id],
    )

    def __repr__(self) -> str:
        return f"<FormatoVersion tipo={self.tipo_id} v{self.numero} ({self.extension})>"
