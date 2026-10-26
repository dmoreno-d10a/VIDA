"""Pruebas de contraseñas (HU-6, RF-17, RF-19, RF-20, RF-21, RF-23).

Hay tres puntos donde se fija una contraseña y la política debe aplicar en los
tres: cuando el Administrador crea el usuario, cuando el propio usuario la
cambia, y cuando el Administrador la restablece.

Las pruebas no dependen de los números de la política: los leen de
configuración, para que cambiarlos no rompa las pruebas (RF-23).
"""

import pytest
from fastapi.testclient import TestClient

from app.configuracion import obtener_configuracion
from tests import datos_ficticios as fic

PERFIL_CONTRASENA = "/perfil/contrasena"


def _entrar(cliente: TestClient, identificacion: str, contrasena: str):
    return cliente.post(
        "/acceso/entrar",
        json={"identificacion": identificacion, "contrasena": contrasena},
    )


def _contrasena_valida(sufijo: str = "") -> str:
    """Contraseña que cumple la política vigente, sin fijar su longitud aquí."""
    configuracion = obtener_configuracion()
    base = f"contrasena-nueva-valida-{sufijo}"
    return base.ljust(configuracion.contrasena_min, "7")[: configuracion.contrasena_max]


# --- El hash: nunca legible, nunca reversible (RF-19) ----------------------


def test_el_hash_no_contiene_la_contrasena_y_cambia_en_cada_calculo() -> None:
    from app.seguridad.contrasena import calcular_hash, verificar

    clara = _contrasena_valida("hash")
    primero = calcular_hash(clara)
    segundo = calcular_hash(clara)

    assert clara not in primero
    assert primero != segundo, "cada hash debe llevar su propia sal"
    assert verificar(clara, primero)
    assert verificar(clara, segundo)
    assert not verificar("otra-cosa-distinta-2211", primero)


# --- La política (RF-20), leída de configuración (RF-23) -------------------


def test_se_rechaza_una_contrasena_mas_corta_que_el_minimo() -> None:
    from app.seguridad.contrasena import ErrorDePolitica, validar_politica

    configuracion = obtener_configuracion()
    corta = "a" * (configuracion.contrasena_min - 1)

    with pytest.raises(ErrorDePolitica) as error:
        validar_politica(corta, identificacion="alguien@ejemplo.local")

    assert str(configuracion.contrasena_min) in str(error.value)


def test_se_rechaza_una_contrasena_mas_larga_que_el_maximo() -> None:
    from app.seguridad.contrasena import ErrorDePolitica, validar_politica

    configuracion = obtener_configuracion()
    larga = "a" * (configuracion.contrasena_max + 1)

    with pytest.raises(ErrorDePolitica):
        validar_politica(larga, identificacion="alguien@ejemplo.local")


def test_no_se_exige_combinacion_de_tipos_de_caracter() -> None:
    """Una frase larga en minúsculas es válida: así lo decidió la política."""
    from app.seguridad.contrasena import validar_politica

    configuracion = obtener_configuracion()
    frase = "la paciencia es un arbol de raiz amarga"[: configuracion.contrasena_max]

    validar_politica(frase, identificacion="alguien@ejemplo.local")


def test_se_rechazan_las_contrasenas_de_uso_comun() -> None:
    from app.seguridad.contrasena import ErrorDePolitica, validar_politica

    configuracion = obtener_configuracion()
    comunes = [
        linea.strip()
        for linea in configuracion.ruta_contrasenas_comunes.read_text(
            encoding="utf-8"
        ).splitlines()
        if linea.strip() and not linea.strip().startswith("#")
    ]
    # Una común que además cumple la longitud mínima, para que el rechazo sea
    # por ser común y no por ser corta.
    candidatas = [c for c in comunes if len(c) >= configuracion.contrasena_min]
    assert candidatas, "la lista debería traer alguna común lo bastante larga"

    with pytest.raises(ErrorDePolitica) as error:
        validar_politica(candidatas[0], identificacion="alguien@ejemplo.local")

    assert "com" in str(error.value).lower()


def test_el_rechazo_de_comunes_no_distingue_mayusculas() -> None:
    from app.seguridad.contrasena import ErrorDePolitica, validar_politica

    with pytest.raises(ErrorDePolitica):
        validar_politica("Documentacion", identificacion="alguien@ejemplo.local")


def test_se_rechaza_la_contrasena_que_contiene_la_identificacion() -> None:
    from app.seguridad.contrasena import ErrorDePolitica, validar_politica

    with pytest.raises(ErrorDePolitica):
        validar_politica(
            "ro.prueba-y-algo-mas-largo", identificacion="ro.prueba@ejemplo.local"
        )


def test_la_politica_sigue_los_limites_de_configuracion(monkeypatch) -> None:
    """RF-23: cambiar el mínimo por entorno cambia qué se acepta."""
    from app.configuracion import Configuracion
    from app.seguridad import contrasena as modulo

    configuracion = obtener_configuracion()
    permisiva = Configuracion(
        bd_url=configuracion.bd_url,
        contrasena_min=4,
        contrasena_max=configuracion.contrasena_max,
    )
    monkeypatch.setattr(modulo, "obtener_configuracion", lambda: permisiva)

    # Con el mínimo en 4, una contraseña de 5 pasa; con el de verdad (12) no.
    modulo.validar_politica("abcde", identificacion="alguien@ejemplo.local")


# --- HU-6: el usuario cambia su propia contraseña --------------------------


def test_el_usuario_cambia_su_contrasena_y_la_anterior_deja_de_servir(
    cliente: TestClient, usuarios
) -> None:
    _entrar(cliente, fic.RO.identificacion, fic.RO.contrasena)
    nueva = _contrasena_valida("cambio")

    cambio = cliente.patch(
        PERFIL_CONTRASENA,
        json={"contrasena_actual": fic.RO.contrasena, "contrasena_nueva": nueva},
    )

    assert cambio.status_code == 204
    cliente.post("/acceso/salir")
    assert _entrar(cliente, fic.RO.identificacion, fic.RO.contrasena).status_code == 401
    assert _entrar(cliente, fic.RO.identificacion, nueva).status_code == 200


def test_sin_acertar_la_contrasena_actual_no_se_cambia(
    cliente: TestClient, usuarios
) -> None:
    _entrar(cliente, fic.RO.identificacion, fic.RO.contrasena)

    respuesta = cliente.patch(
        PERFIL_CONTRASENA,
        json={
            "contrasena_actual": fic.CONTRASENA_EQUIVOCADA,
            "contrasena_nueva": _contrasena_valida("fallido"),
        },
    )

    assert respuesta.status_code == 401
    cliente.post("/acceso/salir")
    assert _entrar(cliente, fic.RO.identificacion, fic.RO.contrasena).status_code == 200


def test_la_contrasena_nueva_debe_cumplir_la_politica(
    cliente: TestClient, usuarios
) -> None:
    _entrar(cliente, fic.RO.identificacion, fic.RO.contrasena)

    respuesta = cliente.patch(
        PERFIL_CONTRASENA,
        json={"contrasena_actual": fic.RO.contrasena, "contrasena_nueva": "qwerty"},
    )

    assert respuesta.status_code == 422
    assert "detalle" in respuesta.json()


def test_no_se_acepta_la_misma_contrasena_que_ya_tiene(
    cliente: TestClient, usuarios
) -> None:
    """RF-20: al cambiarla, no debe aceptarse la inmediatamente anterior."""
    _entrar(cliente, fic.RO.identificacion, fic.RO.contrasena)

    respuesta = cliente.patch(
        PERFIL_CONTRASENA,
        json={
            "contrasena_actual": fic.RO.contrasena,
            "contrasena_nueva": fic.RO.contrasena,
        },
    )

    assert respuesta.status_code == 422


def test_ninguna_respuesta_del_cambio_devuelve_la_contrasena(
    cliente: TestClient, usuarios
) -> None:
    _entrar(cliente, fic.RO.identificacion, fic.RO.contrasena)
    nueva = _contrasena_valida("silencio")

    cambio = cliente.patch(
        PERFIL_CONTRASENA,
        json={"contrasena_actual": fic.RO.contrasena, "contrasena_nueva": nueva},
    )

    assert nueva not in cambio.text
    assert fic.RO.contrasena not in cambio.text


# --- RF-17 y RF-21: cambiarla es opcional y no vence ----------------------


def test_quien_nunca_cambia_su_contrasena_sigue_entrando(
    cliente: TestClient, usuarios
) -> None:
    """RF-17 y RF-21: no se obliga al primer ingreso ni vence por tiempo."""
    for _ in range(3):
        entrada = _entrar(cliente, fic.RO.identificacion, fic.RO.contrasena)
        assert entrada.status_code == 200
        assert "cambi" not in entrada.text.lower(), (
            "no debe exigirse ni sugerirse el cambio como condición para entrar"
        )
        cliente.post("/acceso/salir")


def test_el_usuario_no_puede_cambiar_la_contrasena_de_otro(
    cliente: TestClient, usuarios
) -> None:
    """La ruta de perfil actúa solo sobre quien tiene la sesión."""
    _entrar(cliente, fic.RO.identificacion, fic.RO.contrasena)

    respuesta = cliente.patch(
        PERFIL_CONTRASENA,
        json={
            "contrasena_actual": fic.ADMINISTRADOR.contrasena,
            "contrasena_nueva": _contrasena_valida("ajena"),
        },
    )

    assert respuesta.status_code == 401
    cliente.post("/acceso/salir")
    assert (
        _entrar(
            cliente, fic.ADMINISTRADOR.identificacion, fic.ADMINISTRADOR.contrasena
        ).status_code
        == 200
    )
