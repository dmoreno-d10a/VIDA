"""Pruebas de la administración de usuarios (HU-5, RF-11 a RF-16).

Las seis acciones del Administrador, más la que debe fallar **siempre**:
dejar la plataforma sin ningún Administrador activo. Esa última se prueba por
las tres vías que podrían causarla —revocar, eliminar y cambiar de rol— y
también cuando el Administrador la ejecuta sobre su propia cuenta.
"""

from fastapi.testclient import TestClient

from tests import datos_ficticios as fic

USUARIOS = "/usuarios"


def _entrar(cliente: TestClient, usuario) -> None:
    respuesta = cliente.post(
        "/acceso/entrar",
        json={
            "identificacion": usuario.identificacion,
            "contrasena": usuario.contrasena,
        },
    )
    assert respuesta.status_code == 200


def _id_de(cliente: TestClient, identificacion: str) -> int:
    listado = cliente.get(USUARIOS).json()
    for fila in listado:
        if fila["identificacion"] == identificacion:
            return fila["id"]
    raise AssertionError(f"{identificacion} no aparece en el listado")


# --- RF-11: listar ----------------------------------------------------------


def test_el_listado_muestra_identificacion_rol_y_estado(
    cliente: TestClient, usuarios
) -> None:
    _entrar(cliente, fic.ADMINISTRADOR)

    respuesta = cliente.get(USUARIOS)

    assert respuesta.status_code == 200
    filas = respuesta.json()
    assert len(filas) == len(fic.TODOS)
    for fila in filas:
        assert set(fila) == {"id", "identificacion", "rol", "activo"}


def test_el_listado_nunca_incluye_contrasenas(cliente: TestClient, usuarios) -> None:
    """RF-19: ninguna contraseña legible, para nadie, ni para el Administrador."""
    _entrar(cliente, fic.ADMINISTRADOR)

    cuerpo = cliente.get(USUARIOS).text.lower()

    assert "contrasena" not in cuerpo
    assert "hash" not in cuerpo
    for usuario in fic.TODOS:
        assert usuario.contrasena.lower() not in cuerpo


# --- RF-12: crear -----------------------------------------------------------


def test_el_administrador_crea_un_usuario_que_despues_puede_entrar(
    cliente: TestClient, usuarios
) -> None:
    _entrar(cliente, fic.ADMINISTRADOR)
    nuevo = {
        "identificacion": "nuevo.ro@ejemplo.local",
        "rol": "RO",
        "contrasena": "contrasena-del-nuevo-ro-4821",
    }

    creacion = cliente.post(USUARIOS, json=nuevo)

    assert creacion.status_code == 201
    assert creacion.json()["identificacion"] == nuevo["identificacion"]
    assert creacion.json()["rol"] == "RO"
    assert "contrasena" not in creacion.text.lower()

    cliente.post("/acceso/salir")
    entrada = cliente.post(
        "/acceso/entrar",
        json={
            "identificacion": nuevo["identificacion"],
            "contrasena": nuevo["contrasena"],
        },
    )
    assert entrada.status_code == 200
    assert entrada.json()["rol"] == "RO"


def test_no_se_puede_crear_un_usuario_con_identificacion_repetida(
    cliente: TestClient, usuarios
) -> None:
    _entrar(cliente, fic.ADMINISTRADOR)

    respuesta = cliente.post(
        USUARIOS,
        json={
            "identificacion": fic.RO.identificacion,
            "rol": "RO",
            "contrasena": "otra-contrasena-valida-7719",
        },
    )

    assert respuesta.status_code == 409
    assert "existe" in respuesta.json()["detalle"].lower()


def test_la_contrasena_inicial_debe_cumplir_la_politica(
    cliente: TestClient, usuarios
) -> None:
    """RF-20: la política también aplica a lo que define el Administrador."""
    _entrar(cliente, fic.ADMINISTRADOR)

    respuesta = cliente.post(
        USUARIOS,
        json={
            "identificacion": "otro.ro@ejemplo.local",
            "rol": "RO",
            "contrasena": "123456",
        },
    )

    assert respuesta.status_code == 422


def test_no_se_puede_crear_un_usuario_con_un_rol_que_no_existe(
    cliente: TestClient, usuarios
) -> None:
    """RF-02: solo existen RO y Administrador."""
    _entrar(cliente, fic.ADMINISTRADOR)

    respuesta = cliente.post(
        USUARIOS,
        json={
            "identificacion": "raro@ejemplo.local",
            "rol": "SUPERADMIN",
            "contrasena": "contrasena-valida-del-raro-3390",
        },
    )

    assert respuesta.status_code == 422


# --- RF-13: cambiar rol -----------------------------------------------------


def test_al_cambiar_el_rol_el_usuario_ve_las_opciones_del_rol_nuevo(
    cliente: TestClient, usuarios
) -> None:
    _entrar(cliente, fic.ADMINISTRADOR)
    id_ro = _id_de(cliente, fic.RO.identificacion)

    cambio = cliente.patch(f"{USUARIOS}/{id_ro}/rol", json={"rol": "ADMINISTRADOR"})

    assert cambio.status_code == 200
    assert cambio.json()["rol"] == "ADMINISTRADOR"

    cliente.post("/acceso/salir")
    _entrar(cliente, fic.RO)
    assert cliente.get(USUARIOS).status_code == 200


# --- RF-14: restablecer contraseña ------------------------------------------


def test_al_restablecer_la_contrasena_la_anterior_deja_de_servir(
    cliente: TestClient, usuarios
) -> None:
    _entrar(cliente, fic.ADMINISTRADOR)
    id_ro = _id_de(cliente, fic.RO.identificacion)
    nueva = "contrasena-restablecida-del-ro-5502"

    restablecimiento = cliente.post(
        f"{USUARIOS}/{id_ro}/restablecer-contrasena", json={"contrasena": nueva}
    )

    assert restablecimiento.status_code == 204
    cliente.post("/acceso/salir")

    with_anterior = cliente.post(
        "/acceso/entrar",
        json={"identificacion": fic.RO.identificacion, "contrasena": fic.RO.contrasena},
    )
    assert with_anterior.status_code == 401

    con_nueva = cliente.post(
        "/acceso/entrar",
        json={"identificacion": fic.RO.identificacion, "contrasena": nueva},
    )
    assert con_nueva.status_code == 200


def test_la_contrasena_restablecida_debe_cumplir_la_politica(
    cliente: TestClient, usuarios
) -> None:
    _entrar(cliente, fic.ADMINISTRADOR)
    id_ro = _id_de(cliente, fic.RO.identificacion)

    respuesta = cliente.post(
        f"{USUARIOS}/{id_ro}/restablecer-contrasena", json={"contrasena": "password"}
    )

    assert respuesta.status_code == 422


# --- RF-15: revocar y eliminar ----------------------------------------------


def test_al_revocar_el_acceso_el_usuario_queda_sin_entrar(
    cliente: TestClient, usuarios
) -> None:
    _entrar(cliente, fic.ADMINISTRADOR)
    id_ro = _id_de(cliente, fic.RO.identificacion)

    revocacion = cliente.patch(f"{USUARIOS}/{id_ro}/acceso", json={"activo": False})

    assert revocacion.status_code == 200
    assert revocacion.json()["activo"] is False
    cliente.post("/acceso/salir")

    assert (
        cliente.post(
            "/acceso/entrar",
            json={
                "identificacion": fic.RO.identificacion,
                "contrasena": fic.RO.contrasena,
            },
        ).status_code
        == 401
    )


def test_se_puede_devolver_el_acceso_a_un_usuario_revocado(
    cliente: TestClient, usuarios
) -> None:
    _entrar(cliente, fic.ADMINISTRADOR)
    id_revocado = _id_de(cliente, fic.REVOCADO.identificacion)

    respuesta = cliente.patch(
        f"{USUARIOS}/{id_revocado}/acceso", json={"activo": True}
    )

    assert respuesta.status_code == 200
    cliente.post("/acceso/salir")
    assert (
        cliente.post(
            "/acceso/entrar",
            json={
                "identificacion": fic.REVOCADO.identificacion,
                "contrasena": fic.REVOCADO.contrasena,
            },
        ).status_code
        == 200
    )


def test_al_eliminar_un_usuario_desaparece_del_listado_y_no_entra(
    cliente: TestClient, usuarios
) -> None:
    _entrar(cliente, fic.ADMINISTRADOR)
    id_ro = _id_de(cliente, fic.RO.identificacion)

    eliminacion = cliente.delete(f"{USUARIOS}/{id_ro}")

    assert eliminacion.status_code == 204
    identificaciones = [f["identificacion"] for f in cliente.get(USUARIOS).json()]
    assert fic.RO.identificacion not in identificaciones

    cliente.post("/acceso/salir")
    assert (
        cliente.post(
            "/acceso/entrar",
            json={
                "identificacion": fic.RO.identificacion,
                "contrasena": fic.RO.contrasena,
            },
        ).status_code
        == 401
    )


# --- RF-16: la plataforma nunca se queda sin Administrador activo -----------


def _dejar_un_solo_administrador(cliente: TestClient) -> int:
    """Revoca el segundo Administrador y devuelve el id del que queda."""
    id_segundo = _id_de(cliente, fic.SEGUNDO_ADMINISTRADOR.identificacion)
    assert (
        cliente.patch(f"{USUARIOS}/{id_segundo}/acceso", json={"activo": False}).status_code
        == 200
    )
    return _id_de(cliente, fic.ADMINISTRADOR.identificacion)


def test_no_se_puede_revocar_al_unico_administrador(
    cliente: TestClient, usuarios
) -> None:
    _entrar(cliente, fic.ADMINISTRADOR)
    id_unico = _dejar_un_solo_administrador(cliente)

    respuesta = cliente.patch(f"{USUARIOS}/{id_unico}/acceso", json={"activo": False})

    assert respuesta.status_code == 409
    assert "administrador" in respuesta.json()["detalle"].lower()


def test_no_se_puede_eliminar_al_unico_administrador(
    cliente: TestClient, usuarios
) -> None:
    _entrar(cliente, fic.ADMINISTRADOR)
    id_unico = _dejar_un_solo_administrador(cliente)

    respuesta = cliente.delete(f"{USUARIOS}/{id_unico}")

    assert respuesta.status_code == 409


def test_no_se_puede_degradar_al_unico_administrador(
    cliente: TestClient, usuarios
) -> None:
    _entrar(cliente, fic.ADMINISTRADOR)
    id_unico = _dejar_un_solo_administrador(cliente)

    respuesta = cliente.patch(f"{USUARIOS}/{id_unico}/rol", json={"rol": "RO"})

    assert respuesta.status_code == 409


def test_la_regla_aplica_tambien_sobre_la_propia_cuenta(
    cliente: TestClient, usuarios
) -> None:
    """Es el caso que deja la plataforma inutilizable con un solo clic."""
    _entrar(cliente, fic.ADMINISTRADOR)
    id_propio = _dejar_un_solo_administrador(cliente)

    assert cliente.delete(f"{USUARIOS}/{id_propio}").status_code == 409
    assert (
        cliente.patch(f"{USUARIOS}/{id_propio}/acceso", json={"activo": False}).status_code
        == 409
    )
    assert cliente.patch(f"{USUARIOS}/{id_propio}/rol", json={"rol": "RO"}).status_code == 409

    # Y sigue dentro: la operación no se ejecutó a medias.
    assert cliente.get(USUARIOS).status_code == 200


def test_con_dos_administradores_si_se_puede_degradar_a_uno(
    cliente: TestClient, usuarios
) -> None:
    """La regla protege al último, no a cualquier Administrador."""
    _entrar(cliente, fic.ADMINISTRADOR)
    id_segundo = _id_de(cliente, fic.SEGUNDO_ADMINISTRADOR.identificacion)

    assert cliente.patch(f"{USUARIOS}/{id_segundo}/rol", json={"rol": "RO"}).status_code == 200


def test_un_usuario_que_no_existe_responde_que_no_se_encontro(
    cliente: TestClient, usuarios
) -> None:
    _entrar(cliente, fic.ADMINISTRADOR)

    assert cliente.delete(f"{USUARIOS}/999999").status_code == 404
