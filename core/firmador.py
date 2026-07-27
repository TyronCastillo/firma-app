"""
Módulo de firma electrónica de PDF (PAdES) usando pyHanko.
Toma un certificado .p12 ya cargado y un PDF, y produce un PDF firmado
con firma visible en la posición indicada.
"""
from dataclasses import dataclass
from pathlib import Path

from pyhanko.sign import signers, fields
from pyhanko.sign.fields import SigFieldSpec
from pyhanko.sign.signers.pdf_signer import PdfSignatureMetadata
from pyhanko.sign.signers.pdf_cms import SimpleSigner
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.stamp import TextStampStyle

from .certificado import cargar_p12, CertificadoInvalidoError


@dataclass
class PosicionFirma:
    """Coordenadas del recuadro de firma en el PDF, en puntos PDF (origen abajo-izquierda)."""
    pagina: int  # 0-indexed
    x0: float
    y0: float
    x1: float
    y1: float


class ErrorFirma(Exception):
    pass


def firmar_pdf(
    ruta_pdf_entrada: str | Path,
    ruta_pdf_salida: str | Path,
    ruta_p12: str | Path,
    contrasena_p12: str,
    posicion: PosicionFirma,
    texto_firma: str | None = None,
    nombre_campo: str = "Firma1",
) -> None:
    """
    Firma un PDF con un certificado .p12, colocando una firma visible
    en la posición indicada.

    Lanza CertificadoInvalidoError si el .p12/contraseña son inválidos,
    o ErrorFirma si algo falla durante el proceso de firma.
    """
    # Validamos el certificado primero para dar un mensaje de error claro
    # antes de tocar el PDF.
    _clave, certificado, cadena_ca = cargar_p12(ruta_p12, contrasena_p12)

    signer = signers.SimpleSigner.load_pkcs12(
        pfx_file=str(ruta_p12),
        passphrase=contrasena_p12.encode("utf-8"),
    )

    if texto_firma is None:
        cn = certificado.subject.rfc4514_string()
        texto_firma = f"Firmado digitalmente\n{cn}"

    ruta_pdf_entrada = Path(ruta_pdf_entrada)
    if not ruta_pdf_entrada.exists():
        raise ErrorFirma(f"No se encontró el PDF a firmar: {ruta_pdf_entrada}")

    try:
        with open(ruta_pdf_entrada, "rb") as inf:
            w = IncrementalPdfFileWriter(inf)

            fields.append_signature_field(
                w,
                sig_field_spec=SigFieldSpec(
                    sig_field_name=nombre_campo,
                    on_page=posicion.pagina,
                    box=(posicion.x0, posicion.y0, posicion.x1, posicion.y1),
                ),
            )

            meta = PdfSignatureMetadata(field_name=nombre_campo)

            stamp_style = TextStampStyle(
                stamp_text=texto_firma,
                background_opacity=0.6,
            )

            pdf_signer = signers.PdfSigner(
                meta,
                signer=signer,
                stamp_style=stamp_style,
            )

            ruta_pdf_salida = Path(ruta_pdf_salida)
            with open(ruta_pdf_salida, "wb") as outf:
                pdf_signer.sign_pdf(w, output=outf)

    except CertificadoInvalidoError:
        raise
    except Exception as e:
        raise ErrorFirma(f"Ocurrió un error al firmar el documento: {e}") from e
