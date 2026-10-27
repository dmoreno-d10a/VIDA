"""Autorización: el único lugar donde se decide si una petición pasa.

Esta es la decisión central del plan. El front oculta las opciones que el rol
no puede usar, pero eso es comodidad, no seguridad: la barrera está aquí, y se
aplica igual cuando alguien escribe la dirección a mano (RF-05).

El rol se lee de la base de datos **en cada petición**, no se guarda en la
sesión. Así, cambiar el rol de alguien aplica de inmediato, y revocarle el
acceso lo deja afuera sin esperar a que la sesión expire (RF-15).
"""

from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.bd import obtener_sesion_bd
from app.modelos.usuario import Rol, Usuario
from app.seguridad.sesiones import COOKIE_SESION, usuario_de_la_sesion

# Un solo mensaje para todo lo que signifique "no hay sesión válida": sesión
# ausente, vencida, revocada o sin rol. No se distingue entre ellas (RF-09).
SIN_SESION = "No hay una sesión activa. Identifícate para continuar."

# Sin la palabra «rol» a propósito: la respuesta de una negación no describe
# la opción pedida ni por qué se exige (RF-05).
SIN_PERMISO = "No tienes acceso a esta opción."


def usuario_actual(
    peticion: Request,
    sesion_bd: Annotated[Session, Depends(obtener_sesion_bd)],
) -> Usuario:
    """Resuelve el usuario de la petición, o la rechaza.

    Es la dependencia que exige sesión. Cualquier ruta que la use queda
    protegida; una ruta que no la use queda abierta, así que agregar rutas sin
    ella es el error a vigilar (lo barre T035).
    """
    usuario = usuario_de_la_sesion(sesion_bd, peticion.cookies.get(COOKIE_SESION))
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=SIN_SESION
        )
    return usuario


UsuarioAutenticado = Annotated[Usuario, Depends(usuario_actual)]


def exigir_administrador(usuario: UsuarioAutenticado) -> Usuario:
    """Exige el rol Administrador.

    Al negar no se devuelve ningún dato de la opción pedida: el cuerpo solo
    lleva el motivo (RF-05).
    """
    if usuario.rol is not Rol.ADMINISTRADOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=SIN_PERMISO
        )
    return usuario


Administrador = Annotated[Usuario, Depends(exigir_administrador)]
