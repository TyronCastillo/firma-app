"""
Módulo de gestión de certificados PKCS#12 (.p12)
Carga, valida y extrae información de certificados de firma electrónica.
"""
from dataclasses import dataclass
from pathlib import Path
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509 import Certificate


class CertificadoInvalidoError(Exception):
    """Se lanza cuando el .p12 no se puede abrir (contraseña incorrecta o archivo corrupto)."""
    pass


@dataclass
class InfoCertificado:
    nombre_comun: str
    organizacion: str | None
    pais: str | None
    numero_serie: str
    valido_desde: str
    valido_hasta: str
    emisor: str


def cargar_p12(ruta_archivo: str | Path, contrasena: str) -> tuple:
    """
    Carga un certificado .p12 y devuelve (clave_privada, certificado, cadena_ca).

    Lanza CertificadoInvalidoError si la contraseña es incorrecta o el
    archivo no es un PKCS#12 válido.
    """
    ruta = Path(ruta_archivo)
    if not ruta.exists():
        raise CertificadoInvalidoError(f"No se encontró el archivo: {ruta}")

    try:
        datos = ruta.read_bytes()
        clave_privada, certificado, cadena_ca = pkcs12.load_key_and_certificates(
            datos, contrasena.encode("utf-8")
        )
    except Exception as e:
        # cryptography lanza distintas excepciones según el motivo;
        # las normalizamos a un solo tipo de error de dominio.
        raise CertificadoInvalidoError(
            "No se pudo abrir el certificado. Verifica la contraseña o que el archivo no esté dañado."
        ) from e

    if clave_privada is None or certificado is None:
        raise CertificadoInvalidoError("El archivo .p12 no contiene una clave privada o certificado válido.")

    return clave_privada, certificado, cadena_ca


def extraer_info(certificado: Certificate) -> InfoCertificado:
    """Extrae los datos legibles del certificado para mostrar en la UI (perfil)."""
    from cryptography.x509.oid import NameOID

    def _attr(nombre_oid):
        try:
            return certificado.subject.get_attributes_for_oid(nombre_oid)[0].value
        except IndexError:
            return None

    return InfoCertificado(
        nombre_comun=_attr(NameOID.COMMON_NAME) or "(sin nombre)",
        organizacion=_attr(NameOID.ORGANIZATION_NAME),
        pais=_attr(NameOID.COUNTRY_NAME),
        numero_serie=str(certificado.serial_number),
        valido_desde=str(certificado.not_valid_before_utc),
        valido_hasta=str(certificado.not_valid_after_utc),
        emisor=certificado.issuer.rfc4514_string(),
    )


def esta_vigente(certificado: Certificate) -> bool:
    """Verifica que la fecha actual esté dentro del rango de validez del certificado."""
    import datetime
    ahora = datetime.datetime.now(datetime.timezone.utc)
    return certificado.not_valid_before_utc <= ahora <= certificado.not_valid_after_utc
