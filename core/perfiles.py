"""
Gestión de perfiles de firma: cada perfil apunta a un .p12 y guarda
metadatos (nombre del firmante) para mostrar en la UI.

La contraseña del .p12 NUNCA se guarda en disco. Solo se guarda:
- ruta al archivo .p12 (el archivo original se copia a una carpeta segura
  de la app para que no dependa de que el usuario no mueva/borre el original)
- metadatos públicos del certificado (nombre, vigencia)

En Windows, la carpeta de perfiles debe protegerse adicionalmente con
DPAPI (ver core/almacenamiento_windows.py) para que solo la cuenta de
usuario de Windows pueda leer los .p12 copiados.
"""
import json
import shutil
import uuid
from dataclasses import dataclass, asdict
from pathlib import Path

from .certificado import cargar_p12, extraer_info, InfoCertificado, CertificadoInvalidoError


@dataclass
class Perfil:
    id: str
    nombre_mostrado: str
    ruta_p12: str
    info_certificado: dict  # InfoCertificado como dict, para serializar a JSON


class GestorPerfiles:
    def __init__(self, directorio_datos: str | Path):
        self.directorio_datos = Path(directorio_datos)
        self.directorio_p12 = self.directorio_datos / "certificados"
        self.archivo_indice = self.directorio_datos / "perfiles.json"

        self.directorio_p12.mkdir(parents=True, exist_ok=True)
        if not self.archivo_indice.exists():
            self._guardar_indice([])

    def _cargar_indice(self) -> list[dict]:
        return json.loads(self.archivo_indice.read_text(encoding="utf-8"))

    def _guardar_indice(self, perfiles: list[dict]) -> None:
        self.archivo_indice.write_text(
            json.dumps(perfiles, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    def crear_perfil(self, ruta_p12_original: str | Path, contrasena: str, nombre_mostrado: str | None = None) -> Perfil:
        """
        Valida el .p12 con la contraseña dada, lo copia a la carpeta segura
        de la app, y crea un registro de perfil. La contraseña NO se guarda.
        """
        _clave, certificado, _cadena = cargar_p12(ruta_p12_original, contrasena)
        info = extraer_info(certificado)

        perfil_id = str(uuid.uuid4())
        destino_p12 = self.directorio_p12 / f"{perfil_id}.p12"
        shutil.copy2(ruta_p12_original, destino_p12)

        perfil = Perfil(
            id=perfil_id,
            nombre_mostrado=nombre_mostrado or info.nombre_comun,
            ruta_p12=str(destino_p12),
            info_certificado=asdict(info),
        )

        perfiles = self._cargar_indice()
        perfiles.append(asdict(perfil))
        self._guardar_indice(perfiles)

        return perfil

    def listar_perfiles(self) -> list[Perfil]:
        return [Perfil(**p) for p in self._cargar_indice()]

    def obtener_perfil(self, perfil_id: str) -> Perfil | None:
        for p in self.listar_perfiles():
            if p.id == perfil_id:
                return p
        return None

    def eliminar_perfil(self, perfil_id: str) -> None:
        perfil = self.obtener_perfil(perfil_id)
        if perfil is None:
            return
        Path(perfil.ruta_p12).unlink(missing_ok=True)
        perfiles = [p for p in self._cargar_indice() if p["id"] != perfil_id]
        self._guardar_indice(perfiles)
