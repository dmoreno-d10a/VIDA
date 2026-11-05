"""Pruebas del versionado del formato (HU-4; RF-13, RF-20, RF-21, Art. IX).

El versionado es lo que sostiene el Art. IX: una versión es el registro de qué
estructura estaba vigente en un momento. Si un reemplazo borrara o reescribiera
la anterior, un documento generado hace dos meses dejaría de poder explicarse.

Por eso la prueba central no es que el reemplazo funcione, sino que **lo
anterior siga entero** después de tres reemplazos.
"""

from pathlib import Path

from fastapi.testclient import TestClient

from tests import datos_ficticios as fic

TIPOS = "/tipos-de-documentacion"


def _entrar(cliente: TestClient, usuario) -> None:
    respuesta = cliente.post(
        "/acceso/entrar",
        json={
            "identificacion": usuario.identificacion,
            "contrasena": usuario.contrasena,
        },
    )
    assert respuesta.status_code == 200


def _crear_tipo(cliente: TestClient, nombre: str) -> int:
    respuesta = cliente.post(TIPOS, json={"nombre": nombre})
    assert respuesta.status_code == 201
    return respuesta.json()["id"]


def _cargar(cliente: TestClient, tipo_id: int, ruta: Path, nombre: str | None = None):
    return cliente.post(
        f"{TIPOS}/{tipo_id}/formato",
        files={"archivo": (nombre or ruta.name, ruta.read_bytes())},
    )


def test_tres_reemplazos_conservan_las_tres_versiones_anteriores(
    cliente: TestClient,
    usuarios,
    almacen_temporal,
    formatos_de_prueba,
    estructuras_esperadas,
) -> None:
    """La prueba independiente de HU-4: nada de lo anterior se pierde.

    Se cargan cuatro formatos distintos en orden. Al final, cada versión debe
    conservar **su** archivo original, **su** hash y **su** estructura: no la
    del formato que quedó vigente.
    """
    _entrar(cliente, fic.ADMINISTRADOR)
    tipo_id = _crear_tipo(cliente, "Adapter Reverso")

    orden = [
        "referencia",
        "generalizacion_word",
        "generalizacion_excel",
        "referencia",
    ]
    cargadas = []
    for numero, clave in enumerate(orden, start=1):
        respuesta = _cargar(
            cliente, tipo_id, formatos_de_prueba[clave], nombre=f"v{numero}-{clave}"
            + formatos_de_prueba[clave].suffix
        )
        assert respuesta.status_code == 201
        assert respuesta.json()["numero"] == numero
        cargadas.append((numero, clave, respuesta.json()))

    # Las cuatro, consultadas una por una después de todos los reemplazos.
    for numero, clave, cuando_se_cargo in cargadas:
        guardada = cliente.get(f"{TIPOS}/{tipo_id}/formato/versiones/{numero}")
        assert guardada.status_code == 200
        ahora = guardada.json()
        assert ahora["estructura"] == estructuras_esperadas[clave]
        assert ahora["nombre_archivo_original"] == (
            cuando_se_cargo["nombre_archivo_original"]
        )
        assert ahora["tamano_bytes"] == cuando_se_cargo["tamano_bytes"]

    # Y se puede decir cuál está vigente (Art. IX).
    detalle = cliente.get(f"{TIPOS}/{tipo_id}").json()
    assert [v["numero"] for v in detalle["historial"]] == [4, 3, 2, 1]
    assert [v["numero"] for v in detalle["historial"] if v["vigente"]] == [4]


def test_cada_version_conserva_el_hash_de_su_propio_archivo(
    cliente: TestClient, usuarios, sesion_bd, almacen_temporal, formatos_de_prueba
) -> None:
    """RF-20: el hash es lo que ata la versión a un archivo concreto."""
    _entrar(cliente, fic.ADMINISTRADOR)
    tipo_id = _crear_tipo(cliente, "Adapter Reverso")
    _cargar(cliente, tipo_id, formatos_de_prueba["referencia"])
    _cargar(cliente, tipo_id, formatos_de_prueba["generalizacion_word"])

    # `sesion_bd` y no una sesión nueva: la prueba corre dentro de una
    # transacción que se revierte, y una conexión aparte no vería nada de lo
    # que la prueba acaba de insertar.
    from sqlalchemy import select

    from app.modelos.tipo_documentacion import FormatoVersion

    hashes = list(
        sesion_bd.scalars(
            select(FormatoVersion.hash_sha256)
            .where(FormatoVersion.tipo_id == tipo_id)
            .order_by(FormatoVersion.numero)
        ).all()
    )

    assert len(hashes) == 2
    assert hashes[0] != hashes[1]
    assert all(len(h) == 64 for h in hashes)


def test_reemplazar_por_un_archivo_identico_crea_una_version_nueva(
    cliente: TestClient, usuarios, almacen_temporal, formatos_de_prueba
) -> None:
    """CE-10: no se comparan contenidos para decidir si hay versión.

    Cargar dos veces el mismo archivo es una acción del Administrador, y el
    historial registra que la hizo. Decidir por él que «no cambió nada» sería
    suponer su intención, y además el archivo en disco es el mismo porque el
    nombre sale del hash: no se duplica nada.
    """
    _entrar(cliente, fic.ADMINISTRADOR)
    tipo_id = _crear_tipo(cliente, "Adapter Reverso")

    primera = _cargar(cliente, tipo_id, formatos_de_prueba["referencia"])
    segunda = _cargar(cliente, tipo_id, formatos_de_prueba["referencia"])

    assert primera.json()["numero"] == 1
    assert segunda.json()["numero"] == 2
    assert segunda.status_code == 201
    assert len(cliente.get(f"{TIPOS}/{tipo_id}").json()["historial"]) == 2


def test_un_reemplazo_invalido_deja_la_version_que_ya_tenia(
    cliente: TestClient,
    usuarios,
    almacen_temporal,
    formatos_de_prueba,
    estructuras_esperadas,
) -> None:
    """RF-10: el tipo queda exactamente como estaba, estructura incluida."""
    _entrar(cliente, fic.ADMINISTRADOR)
    tipo_id = _crear_tipo(cliente, "Adapter Reverso")
    _cargar(cliente, tipo_id, formatos_de_prueba["referencia"])

    assert cliente.post(
        f"{TIPOS}/{tipo_id}/formato",
        files={"archivo": ("roto.docx", b"PK\x03\x04basura")},
    ).status_code == 422

    detalle = cliente.get(f"{TIPOS}/{tipo_id}").json()
    assert detalle["estado"] == "activo"
    assert detalle["version_vigente"]["numero"] == 1
    assert detalle["version_vigente"]["estructura"] == (
        estructuras_esperadas["referencia"]
    )
    assert len(detalle["historial"]) == 1


def test_el_archivo_de_una_version_anterior_sigue_en_el_almacen(
    cliente: TestClient, usuarios, sesion_bd, almacen_temporal, formatos_de_prueba
) -> None:
    """RF-09, Art. IX: la estructura sin el archivo no basta.

    La 005 va a escribir el documento **dentro** del archivo original, así que
    perder el archivo de una versión anterior haría imposible reproducir un
    documento viejo.
    """
    _entrar(cliente, fic.ADMINISTRADOR)
    tipo_id = _crear_tipo(cliente, "Adapter Reverso")
    _cargar(cliente, tipo_id, formatos_de_prueba["referencia"])
    _cargar(cliente, tipo_id, formatos_de_prueba["generalizacion_word"])

    from sqlalchemy import select

    from app.formatos import almacen
    from app.modelos.tipo_documentacion import FormatoVersion

    rutas = list(
        sesion_bd.scalars(
            select(FormatoVersion.ruta_almacenada)
            .where(FormatoVersion.tipo_id == tipo_id)
            .order_by(FormatoVersion.numero)
        ).all()
    )

    assert len(rutas) == 2
    for ruta in rutas:
        # Relativa, nunca absoluta (RF-20).
        assert not Path(ruta).is_absolute()
        assert almacen.leer(ruta)
