"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { pedirApi } from "@/lib/api";

/**
 * Listado de tipos de documentación (HU-1, RF-01 a RF-03).
 *
 * Muestra los tres estados tal como los informa el backend, sin deducir
 * ninguno aquí: el estado es una propiedad derivada del modelo, y repetir esa
 * lógica en el front sería otro lugar donde puede quedar distinta.
 *
 * El nombre y la descripción se envían tal como los escribió el
 * Administrador: esta pantalla no les quita espacios ni les cambia
 * mayúsculas. Si el nombre choca con otro tipo, el backend responde 409 y
 * aquí se muestra ese motivo (Art. II).
 */

type Estado = "incompleto" | "activo" | "desactivado";

type VersionVigente = {
  numero: number;
  extension: string;
  creado_en: string;
};

type Fila = {
  id: number;
  nombre: string;
  descripcion: string | null;
  estado: Estado;
  version_vigente: VersionVigente | null;
};

const LEYENDA: Record<Estado, string> = {
  incompleto: "Sin formato — los RO no lo ven",
  activo: "Activo — los RO lo ven",
  desactivado: "Desactivado — los RO no lo ven",
};

export default function TiposDeDocumentacion() {
  const [filas, setFilas] = useState<Fila[]>([]);
  const [aviso, setAviso] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [nombre, setNombre] = useState("");
  const [descripcion, setDescripcion] = useState("");

  const cargar = useCallback(async () => {
    const respuesta = await pedirApi<Fila[]>("/tipos-de-documentacion");
    if (respuesta.ok) {
      setFilas(respuesta.datos);
    } else {
      setError(respuesta.detalle);
    }
  }, []);

  useEffect(() => {
    void cargar();
  }, [cargar]);

  async function crear(evento: React.FormEvent) {
    evento.preventDefault();
    setAviso(null);
    setError(null);

    const respuesta = await pedirApi<Fila>("/tipos-de-documentacion", {
      metodo: "POST",
      cuerpo: {
        nombre,
        // Una descripción vacía se manda como ausente, no como "": el
        // backend trata las dos igual, pero mandar el dato que es evita que
        // se vean distintas en la base.
        descripcion: descripcion.trim() === "" ? null : descripcion,
      },
    });

    if (!respuesta.ok) {
      setError(respuesta.detalle);
      return;
    }

    setAviso(
      `Tipo «${respuesta.datos.nombre}» creado. Cárgale un formato para que los RO puedan usarlo.`,
    );
    setNombre("");
    setDescripcion("");
    await cargar();
  }

  /** Ejecuta una acción y refresca, mostrando el motivo si el backend la niega. */
  async function ejecutar(
    ruta: string,
    opciones: { metodo: string; cuerpo?: unknown },
    mensajeDeExito: string,
  ) {
    setAviso(null);
    setError(null);

    const respuesta = await pedirApi(ruta, opciones);
    if (!respuesta.ok) {
      // Tal como viene: el backend es quien sabe por qué no se puede, y su
      // mensaje ya ofrece la alternativa cuando la hay (RF-15).
      setError(respuesta.detalle);
      return;
    }

    setAviso(mensajeDeExito);
    await cargar();
  }

  async function cambiarActivacion(fila: Fila) {
    const desactivar = fila.estado !== "desactivado";
    await ejecutar(
      `/tipos-de-documentacion/${fila.id}/activacion`,
      { metodo: "POST", cuerpo: { desactivado: desactivar } },
      desactivar
        ? `«${fila.nombre}» quedó desactivado: los RO ya no lo ven.`
        : `«${fila.nombre}» volvió a circulación.`,
    );
  }

  async function eliminar(fila: Fila) {
    const confirmado = window.confirm(
      `¿Eliminar «${fila.nombre}»? Esta acción no se puede deshacer.`,
    );
    if (!confirmado) {
      return;
    }
    await ejecutar(
      `/tipos-de-documentacion/${fila.id}`,
      { metodo: "DELETE" },
      `Tipo «${fila.nombre}» eliminado.`,
    );
  }

  return (
    <section className="tipos-de-documentacion">
      <h1>Tipos de documentación</h1>

      {aviso ? (
        <p role="status" className="aviso">
          {aviso}
        </p>
      ) : null}
      {error ? (
        <p role="alert" className="error">
          {error}
        </p>
      ) : null}

      <h2>Crear tipo</h2>
      <form onSubmit={crear} className="crear">
        <label htmlFor="nuevo-nombre">Nombre</label>
        <input
          id="nuevo-nombre"
          type="text"
          maxLength={200}
          value={nombre}
          onChange={(e) => setNombre(e.target.value)}
          required
        />

        <label htmlFor="nueva-descripcion">Descripción (opcional)</label>
        <textarea
          id="nueva-descripcion"
          maxLength={1000}
          value={descripcion}
          onChange={(e) => setDescripcion(e.target.value)}
        />

        <button type="submit">Crear tipo</button>
      </form>

      <h2>Tipos registrados</h2>
      {filas.length === 0 ? (
        <p>
          Todavía no hay ningún tipo de documentación. Crea el primero con el
          formulario de arriba.
        </p>
      ) : (
        <table>
          <thead>
            <tr>
              <th scope="col">Nombre</th>
              <th scope="col">Descripción</th>
              <th scope="col">Estado</th>
              <th scope="col">Formato vigente</th>
              <th scope="col">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {filas.map((fila) => (
              <tr key={fila.id}>
                <td>
                  <Link href={`/administracion/tipos-de-documentacion/${fila.id}`}>
                    {fila.nombre}
                  </Link>
                </td>
                <td>{fila.descripcion ?? "—"}</td>
                <td>{LEYENDA[fila.estado]}</td>
                <td>
                  {fila.version_vigente
                    ? `Versión ${fila.version_vigente.numero} (.${fila.version_vigente.extension})`
                    : "Ninguno"}
                </td>
                <td className="acciones">
                  <button
                    type="button"
                    onClick={() => cambiarActivacion(fila)}
                  >
                    {fila.estado === "desactivado" ? "Reactivar" : "Desactivar"}
                  </button>
                  <button type="button" onClick={() => eliminar(fila)}>
                    Eliminar
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}
