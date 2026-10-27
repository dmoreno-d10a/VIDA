"""Comprueba que los datos de prueba cumplen el Art. X.3: solo datos ficticios."""

from tests import datos_ficticios


def test_son_cinco_y_cubren_las_cinco_situaciones_de_acceso() -> None:
    assert len(datos_ficticios.TODOS) == 5

    roles_y_estados = {(u.rol, u.activo) for u in datos_ficticios.TODOS}
    assert ("RO", True) in roles_y_estados
    assert ("ADMINISTRADOR", True) in roles_y_estados
    assert (None, True) in roles_y_estados  # autenticado sin rol (RF-06)
    assert ("RO", False) in roles_y_estados  # acceso revocado (RF-15)

    administradores = [u for u in datos_ficticios.TODOS if u.rol == "ADMINISTRADOR"]
    assert len(administradores) == 2  # permite probar RF-16 sin quedarse sin ninguno


def test_ninguna_identificacion_apunta_a_una_persona_real() -> None:
    for usuario in datos_ficticios.TODOS:
        assert usuario.identificacion.endswith("@ejemplo.local")
    assert datos_ficticios.INEXISTENTE.endswith("@ejemplo.local")


def test_las_contrasenas_de_prueba_no_son_comunes_ni_cortas() -> None:
    from app.configuracion import obtener_configuracion

    configuracion = obtener_configuracion()
    comunes = {
        linea.strip().lower()
        for linea in configuracion.ruta_contrasenas_comunes.read_text(
            encoding="utf-8"
        ).splitlines()
        if linea.strip() and not linea.strip().startswith("#")
    }

    for usuario in datos_ficticios.TODOS:
        assert len(usuario.contrasena) >= configuracion.contrasena_min
        assert usuario.contrasena.lower() not in comunes
