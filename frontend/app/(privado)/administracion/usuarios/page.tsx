"use client";

import { useCallback, useEffect, useState } from "react";

import { pedirApi, type Rol } from "@/lib/api";

/**
 * Administración de usuarios (HU-5, RF-11 a RF-16).
 *
 * Las seis acciones del Administrador. Cuando una dejaría la plataforma sin
 * Administrador activo, el backend responde 409 y aquí se muestra ese motivo
 * sin ejecutar nada: la regla vive allá, no en esta pantalla (RF-16).
 */

type Fila = {
  id: number;
  identificacion: string;
  rol: Rol | null;
  activo: boolean;
};

const ROLES: { valor: Rol; nombre: string }[] = [
  { valor: "RO", nombre: "RO" },
  { valor: "ADMINISTRADOR", nombre: "Administrador" },
];

export default function AdministracionDeUsuarios() {
  const [filas, setFilas] = useState<Fila[]>([]);
  const [aviso, setAviso] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [identificacion, setIdentificacion] = useState("");
  const [rolNuevo, setRolNuevo] = useState<Rol>("RO");
  const [contrasena, setContrasena] = useState("");

  const cargar = useCallback(async () => {
    const respuesta = await pedirApi<Fila[]>("/usuarios");
    if (respuesta.ok) {
      setFilas(respuesta.datos);
    } else {
      setError(respuesta.detalle);
    }
  }, []);

  useEffect(() => {
    void cargar();
  }, [cargar]);

  /** Ejecuta una acción y refresca el listado, mostrando el motivo si falla. */
  async function ejecutar(
    ruta: string,
    opciones: { metodo: string; cuerpo?: unknown },
    mensajeDeExito: string,
  ) {
    setAviso(null);
    setError(null);

    const respuesta = await pedirApi(ruta, opciones);
    if (!respuesta.ok) {
      setError(respuesta.detalle);
      return false;
    }

    setAviso(mensajeDeExito);
    await cargar();
    return true;
  }

  async function crear(evento: React.FormEvent) {
    evento.preventDefault();
    const creado = await ejecutar(
      "/usuarios",
      { metodo: "POST", cuerpo: { identificacion, rol: rolNuevo, contrasena } },
      `Usuario ${identificacion} creado.`,
    );
    if (creado) {
      setIdentificacion("");
      setContrasena("");
      setRolNuevo("RO");
    }
  }

  async function cambiarRol(fila: Fila, rol: Rol) {
    await ejecutar(
      `/usuarios/${fila.id}/rol`,
      { metodo: "PATCH", cuerpo: { rol } },
      `${fila.identificacion} ahora es ${rol === "ADMINISTRADOR" ? "Administrador" : "RO"}.`,
    );
  }

  async function restablecerContrasena(fila: Fila) {
    const nueva = window.prompt(
      `Contraseña nueva para ${fila.identificacion}:`,
    );
    if (!nueva) {
      return;
    }
    await ejecutar(
      `/usuarios/${fila.id}/restablecer-contrasena`,
      { metodo: "POST", cuerpo: { contrasena: nueva } },
      `Contraseña de ${fila.identificacion} restablecida. La anterior ya no sirve.`,
    );
  }

  async function cambiarAcceso(fila: Fila) {
    await ejecutar(
      `/usuarios/${fila.id}/acceso`,
      { metodo: "PATCH", cuerpo: { activo: !fila.activo } },
      fila.activo
        ? `Acceso de ${fila.identificacion} revocado.`
        : `Acceso de ${fila.identificacion} restituido.`,
    );
  }

  async function eliminar(fila: Fila) {
    const confirmado = window.confirm(
      `¿Eliminar a ${fila.identificacion}? Esta acción no se puede deshacer.`,
    );
    if (!confirmado) {
      return;
    }
    await ejecutar(
      `/usuarios/${fila.id}`,
      { metodo: "DELETE" },
      `Usuario ${fila.identificacion} eliminado.`,
    );
  }

  return (
    <section className="usuarios">
      <h1>Administrar usuarios</h1>

      {aviso ? <p role="status" className="aviso">{aviso}</p> : null}
      {error ? <p role="alert" className="error">{error}</p> : null}

      <h2>Crear usuario</h2>
      <form onSubmit={crear} className="crear">
        <label htmlFor="nueva-identificacion">Identificación</label>
        <input
          id="nueva-identificacion"
          type="text"
          value={identificacion}
          onChange={(e) => setIdentificacion(e.target.value)}
          required
        />

        <label htmlFor="nuevo-rol">Rol</label>
        <select
          id="nuevo-rol"
          value={rolNuevo}
          onChange={(e) => setRolNuevo(e.target.value as Rol)}
        >
          {ROLES.map((rol) => (
            <option key={rol.valor} value={rol.valor}>
              {rol.nombre}
            </option>
          ))}
        </select>

        <label htmlFor="nueva-contrasena">Contraseña inicial</label>
        <input
          id="nueva-contrasena"
          type="password"
          autoComplete="new-password"
          value={contrasena}
          onChange={(e) => setContrasena(e.target.value)}
          required
        />

        <button type="submit">Crear usuario</button>
      </form>

      <h2>Usuarios de la plataforma</h2>
      <table>
        <thead>
          <tr>
            <th scope="col">Identificación</th>
            <th scope="col">Rol</th>
            <th scope="col">Acceso</th>
            <th scope="col">Acciones</th>
          </tr>
        </thead>
        <tbody>
          {filas.map((fila) => (
            <tr key={fila.id}>
              <td>{fila.identificacion}</td>
              <td>
                <select
                  aria-label={`Rol de ${fila.identificacion}`}
                  value={fila.rol ?? ""}
                  onChange={(e) => cambiarRol(fila, e.target.value as Rol)}
                >
                  {fila.rol === null ? <option value="">Sin rol</option> : null}
                  {ROLES.map((rol) => (
                    <option key={rol.valor} value={rol.valor}>
                      {rol.nombre}
                    </option>
                  ))}
                </select>
              </td>
              <td>{fila.activo ? "Activo" : "Revocado"}</td>
              <td className="acciones">
                <button type="button" onClick={() => restablecerContrasena(fila)}>
                  Restablecer contraseña
                </button>
                <button type="button" onClick={() => cambiarAcceso(fila)}>
                  {fila.activo ? "Revocar acceso" : "Restituir acceso"}
                </button>
                <button type="button" onClick={() => eliminar(fila)}>
                  Eliminar
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
