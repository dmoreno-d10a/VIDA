"""Pruebas de los tipos disponibles para el RO (HU-5, RF-16, CE-07).

Lo que esta ruta **no** debe devolver es tan importante como lo que devuelve:
ni tipos incompletos, ni desactivados, ni estructura, ni historial. Las
pruebas que lo comprueban están escritas contra la respuesta y no contra el
esquema, porque lo que se filtra por accidente se filtra en la respuesta.

Los dos casos que no deben aparecer —incompleto y desactivado— se prueban en
la **misma** base que uno activo: así se verifica que la consulta discrimina,
y no que una base vacía devuelve poco.
"""

from pathlib import Path

from fastapi.testclient import TestClient

from tests import datos_ficticios as fic

TIPOS = "/tipos-de-documentacion"
DISPONIBLES = "/tipos-de-documentacion-disponibles"


def _entrar(cliente: TestClient, usuario) -> None:
    respuesta = cliente.post(
        "/acceso/entrar",
        json={
            "identificacion": usuario.identificacion,
            "contrasena": usuario.contrasena,
        },
    )
    assert respuesta.status_code == 200


def _salir(cliente: TestClient) -> None:
    cliente.post("/acceso/salir")


def _montar_los_tres_estados(
    cliente: TestClient, formatos: dict[str, Path]
) -> dict[str, int]:
    """Deja en la base un tipo activo, uno incompleto y uno desactivado."""
    _entrar(cliente, fic.ADMINISTRADOR)

    creados = {}
    for clave, nombre in [
        ("activo", "Tipo activo"),
        ("incompleto", "Tipo incompleto"),
        ("desactivado", "Tipo desactivado"),
    ]:
        respuesta = cliente.post(TIPOS, json={"nombre": nombre})
        assert respuesta.status_code == 201
        creados[clave] = respuesta.json()["id"]

    for clave in ("activo", "desactivado"):
        assert cliente.post(
            f"{TIPOS}/{creados[clave]}/formato",
            files={
                "archivo": (
                    formatos["referencia"].name,
                    formatos["referencia"].read_bytes(),
                )
            },
        ).status_code == 201

    assert cliente.post(
        f"{TIPOS}/{creados['desactivado']}/activacion", json={"desactivado": True}
    ).status_code == 200

    _salir(cliente)
    return creados


# --- RF-16: solo los activos ------------------------------------------------


def test_el_ro_recibe_solo_los_tipos_activos(
    cliente: TestClient, usuarios, almacen_temporal, formatos_de_prueba
) -> None:
    _montar_los_tres_estados(cliente, formatos_de_prueba)
    _entrar(cliente, fic.RO)

    respuesta = cliente.get(DISPONIBLES)

    assert respuesta.status_code == 200
    assert [t["nombre"] for t in respuesta.json()] == ["Tipo activo"]


def test_un_tipo_incompleto_no_aparece(
    cliente: TestClient, usuarios, almacen_temporal, formatos_de_prueba
) -> None:
    """Un tipo sin formato no se puede usar, así que no se ofrece."""
    creados = _montar_los_tres_estados(cliente, formatos_de_prueba)
    _entrar(cliente, fic.RO)

    identificadores = [t["id"] for t in cliente.get(DISPONIBLES).json()]

    assert creados["incompleto"] not in identificadores


def test_un_tipo_desactivado_no_aparece(
    cliente: TestClient, usuarios, almacen_temporal, formatos_de_prueba
) -> None:
    """Aunque tenga formato vigente: desactivarlo es sacarlo de circulación."""
    creados = _montar_los_tres_estados(cliente, formatos_de_prueba)
    _entrar(cliente, fic.RO)

    identificadores = [t["id"] for t in cliente.get(DISPONIBLES).json()]

    assert creados["desactivado"] not in identificadores


def test_la_respuesta_no_trae_estructura_ni_historial_ni_versiones(
    cliente: TestClient, usuarios, almacen_temporal, formatos_de_prueba
) -> None:
    """RF-16: solo lo necesario para elegir."""
    _montar_los_tres_estados(cliente, formatos_de_prueba)
    _entrar(cliente, fic.RO)

    fila = cliente.get(DISPONIBLES).json()[0]

    assert set(fila) == {"id", "nombre", "descripcion"}


def test_sin_ningun_tipo_activo_la_respuesta_es_una_lista_vacia(
    cliente: TestClient, usuarios
) -> None:
    """No un 404: «no hay tipos» es una respuesta, no un error.

    Convertirlo en el mensaje explícito que pide HU-5 es del front.
    """
    _entrar(cliente, fic.RO)

    respuesta = cliente.get(DISPONIBLES)

    assert respuesta.status_code == 200
    assert respuesta.json() == []


def test_los_tipos_disponibles_van_ordenados_por_nombre(
    cliente: TestClient, usuarios, almacen_temporal, formatos_de_prueba
) -> None:
    _entrar(cliente, fic.ADMINISTRADOR)
    for nombre in ("Zeta", "Alfa", "Media"):
        tipo_id = cliente.post(TIPOS, json={"nombre": nombre}).json()["id"]
        assert cliente.post(
            f"{TIPOS}/{tipo_id}/formato",
            files={
                "archivo": (
                    formatos_de_prueba["referencia"].name,
                    formatos_de_prueba["referencia"].read_bytes(),
                )
            },
        ).status_code == 201
    _salir(cliente)
    _entrar(cliente, fic.RO)

    assert [t["nombre"] for t in cliente.get(DISPONIBLES).json()] == [
        "Alfa",
        "Media",
        "Zeta",
    ]


# --- Art. X.1: exige sesión, pero no rol ------------------------------------


def test_sin_sesion_la_ruta_responde_401(cliente: TestClient, usuarios) -> None:
    assert cliente.get(DISPONIBLES).status_code == 401


def test_el_administrador_tambien_la_puede_consultar(
    cliente: TestClient, usuarios, almacen_temporal, formatos_de_prueba
) -> None:
    """El Administrador también documenta: no se le niega esta ruta."""
    _montar_los_tres_estados(cliente, formatos_de_prueba)
    _entrar(cliente, fic.ADMINISTRADOR)

    respuesta = cliente.get(DISPONIBLES)

    assert respuesta.status_code == 200
    assert [t["nombre"] for t in respuesta.json()] == ["Tipo activo"]
