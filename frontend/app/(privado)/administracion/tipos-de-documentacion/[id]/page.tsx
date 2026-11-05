"use client";

import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";
import { useParams } from "next/navigation";

import { pedirApi } from "@/lib/api";

/**
 * Detalle de un tipo de documentación (HU-2, HU-3; RF-08, RF-21).
 *
 * **Esta pantalla es donde el Administrador revisa la estructura reconocida**,
 * y es la única revisión que existe: ninguna ruta le exige confirmar nada
 * antes de que el tipo quede activo. Por eso está dispuesta para comparar con
 * el archivo abierto al lado: las secciones con su nivel y en su orden, o las
 * hojas con sus columnas y la fila de la que salieron.
 *
 * Si la estructura no corresponde, se corrige el archivo y se vuelve a
 * cargar, que produce una versión nueva. No hay forma de editarla aquí: dejar
 * que la estructura guardada divergiera del archivo es lo que el Art. I no
 * admite.
 */

type Seccion = { nombre: string | null; nivel: number };
type Hoja = {
  nombre: string;
  fila_de_encabezados: number | null;
  columnas: string[];
};
type Estructura =
  | { clase: "word"; secciones: Seccion[] }
  | { clase: "excel"; hojas: Hoja[] };

type Version = {
  numero: number;
  nombre_archivo_original: string;
  extension: string;
  tamano_bytes: number;
  creado_en: string;
  estructura: Estructura;
};

type EntradaDeHistorial = {
  numero: number;
  nombre_archivo_original: string;
  creado_en: string;
  vigente: boolean;
};

type Detalle = {
  id: number;
  nombre: string;
  descripcion: string | null;
  estado: "incompleto" | "activo" | "desactivado";
  version_vigente: Version | null;
  historial: EntradaDeHistorial[];
};

const LEYENDA: Record<Detalle["estado"], string> = {
  incompleto: "Sin formato — los RO no lo ven",
  activo: "Activo — los RO lo ven",
  desactivado: "Desactivado — los RO no lo ven",
};

function fecha(iso: string): string {
  return new Date(iso).toLocaleString("es-CO");
}

/** Las secciones de un Word, sangradas por nivel para poder comparar. */
function EstructuraWord({ secciones }: { secciones: Seccion[] }) {
  return (
    <ol className="secciones">
      {secciones.map((seccion, posicion) => (
        <li
          key={posicion}
          style={{ marginLeft: `${(seccion.nivel - 1) * 1.5}rem` }}
        >
          {seccion.nombre === null ? (
            // Un título sin texto se muestra como tal: en blanco parecería un
            // error de la plataforma, y es lo que el archivo trae (RF-11).
            <em>(título sin texto)</em>
          ) : (
            seccion.nombre
          )}{" "}
          <small>nivel {seccion.nivel}</small>
        </li>
      ))}
    </ol>
  );
}

/** Las hojas de un Excel, con la fila de la que salieron los encabezados. */
function EstructuraExcel({ hojas }: { hojas: Hoja[] }) {
  return (
    <ul className="hojas">
      {hojas.map((hoja) => (
        <li key={hoja.nombre}>
          <strong>{hoja.nombre}</strong>{" "}
          <small>
            {hoja.fila_de_encabezados === null
              ? "sin encabezados"
              : `encabezados en la fila ${hoja.fila_de_encabezados}`}
          </small>
          {hoja.columnas.length > 0 ? (
            <ol className="columnas">
              {hoja.columnas.map((columna, posicion) => (
                // La posición va en la clave porque dos columnas pueden
                // llamarse igual, y las dos se conservan (RF-06).
                <li key={`${columna}-${posicion}`}>{columna}</li>
              ))}
            </ol>
          ) : null}
        </li>
      ))}
    </ul>
  );
}

export default function DetalleDeTipo() {
  const parametros = useParams<{ id: string }>();
  const id = parametros.id;

  const [detalle, setDetalle] = useState<Detalle | null>(null);
  const [aviso, setAviso] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [cargando, setCargando] = useState(false);

  const archivo = useRef<HTMLInputElement>(null);

  const cargar = useCallback(async () => {
    const respuesta = await pedirApi<Detalle>(`/tipos-de-documentacion/${id}`);
    if (respuesta.ok) {
      setDetalle(respuesta.datos);
    } else {
      setError(respuesta.detalle);
    }
  }, [id]);

  useEffect(() => {
    void cargar();
  }, [cargar]);

  async function subirFormato(evento: React.FormEvent) {
    evento.preventDefault();
    const elegido = archivo.current?.files?.[0];
    if (!elegido) {
      return;
    }

    setAviso(null);
    setError(null);
    // El análisis puede tardar hasta 30 s, y con el respaldo con IA es lo
    // normal que tarde: la espera es parte de la experiencia, así que la
    // pantalla tiene que decir que está trabajando.
    setCargando(true);

    const formulario = new FormData();
    formulario.append("archivo", elegido);

    const respuesta = await pedirApi<Version>(
      `/tipos-de-documentacion/${id}/formato`,
      { metodo: "POST", cuerpo: formulario },
    );
    setCargando(false);

    if (!respuesta.ok) {
      // El mensaje del backend se muestra tal como viene: es él quien sabe
      // qué pasó, y reescribirlo aquí sería mantener dos versiones del mismo
      // texto (Art. IV).
      setError(respuesta.detalle);
      return;
    }

    setAviso(
      `Formato cargado como versión ${respuesta.datos.numero}. Revisa abajo que la estructura corresponda a tu archivo.`,
    );
    if (archivo.current) {
      archivo.current.value = "";
    }
    await cargar();
  }

  if (detalle === null) {
    return (
      <section>
        {error ? (
          <p role="alert" className="error">
            {error}
          </p>
        ) : (
          <p>Cargando…</p>
        )}
        <p>
          <Link href="/administracion/tipos-de-documentacion">
            Volver a los tipos de documentación
          </Link>
        </p>
      </section>
    );
  }

  return (
    <section className="detalle-del-tipo">
      <p>
        <Link href="/administracion/tipos-de-documentacion">
          ← Tipos de documentación
        </Link>
      </p>

      <h1>{detalle.nombre}</h1>
      <p>{detalle.descripcion ?? "Sin descripción"}</p>
      <p>
        <strong>Estado:</strong> {LEYENDA[detalle.estado]}
      </p>

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

      <h2>
        {detalle.version_vigente ? "Reemplazar el formato" : "Cargar el formato"}
      </h2>
      <form onSubmit={subirFormato} className="cargar-formato">
        <label htmlFor="archivo-de-formato">
          Archivo de Word (.docx) o Excel (.xlsx)
        </label>
        <input
          id="archivo-de-formato"
          ref={archivo}
          type="file"
          accept=".docx,.xlsx"
          required
          disabled={cargando}
        />
        <button type="submit" disabled={cargando}>
          {cargando ? "Analizando el formato…" : "Cargar"}
        </button>
        {cargando ? (
          <p role="status">
            Analizando el formato. Puede tardar hasta medio minuto; no cierres
            esta página.
          </p>
        ) : null}
      </form>

      {detalle.version_vigente ? (
        <>
          <h2>Estructura reconocida</h2>
          <p>
            Versión {detalle.version_vigente.numero} ·{" "}
            {detalle.version_vigente.nombre_archivo_original} ·{" "}
            {fecha(detalle.version_vigente.creado_en)}
          </p>
          <p>
            Compárala con tu archivo abierto al lado. Si algo no corresponde,
            corrige el archivo y vuelve a cargarlo: la estructura no se edita
            aquí.
          </p>
          {detalle.version_vigente.estructura.clase === "word" ? (
            <EstructuraWord
              secciones={detalle.version_vigente.estructura.secciones}
            />
          ) : (
            <EstructuraExcel hojas={detalle.version_vigente.estructura.hojas} />
          )}
        </>
      ) : (
        <p>
          Este tipo todavía no tiene un formato cargado, así que ningún RO lo
          ve.
        </p>
      )}

      {detalle.historial.length > 0 ? (
        <>
          <h2>Historial de formatos</h2>
          <table>
            <thead>
              <tr>
                <th scope="col">Versión</th>
                <th scope="col">Archivo</th>
                <th scope="col">Desde</th>
                <th scope="col">Vigente</th>
              </tr>
            </thead>
            <tbody>
              {detalle.historial.map((entrada) => (
                <tr key={entrada.numero}>
                  <td>{entrada.numero}</td>
                  <td>{entrada.nombre_archivo_original}</td>
                  <td>{fecha(entrada.creado_en)}</td>
                  <td>{entrada.vigente ? "Sí" : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      ) : null}
    </section>
  );
}
