# Firma Electrónica (prototipo tipo Firmatic)

App de escritorio 100% local para firmar PDFs con certificado .p12 (PKCS#12),
compatible con las entidades certificadoras acreditadas por ARCOTEL en Ecuador
(Registro Civil, Security Data, ANF AC, ANAC).

## Instalación

Requiere Python 3.11+ instalado.

```bash
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

## Ejecutar

```bash
python main.py
```

## Estructura

```
firma-app/
├── core/               # Lógica pura, sin dependencias de UI (testeable/portable)
│   ├── certificado.py  # Cargar y validar .p12
│   ├── firmador.py     # Firma PAdES del PDF
│   └── perfiles.py     # Gestión de perfiles (guarda .p12 + metadatos, nunca la contraseña)
├── ui/                 # Interfaz PyQt6
│   ├── pantalla_inicio.py
│   ├── pantalla_perfiles.py
│   ├── dialogo_nuevo_perfil.py
│   ├── pantalla_firmar.py
│   ├── visor_pdf.py     # Previsualización + selección de posición de firma
│   └── ventana_principal.py
├── main.py
└── requirements.txt
```

## Flujo de uso (igual que Firmatic)

1. Abre la app → **Perfiles** → **+** → selecciona tu `.p12` e ingresa la contraseña.
2. Vuelve a inicio → **Firmar PDF** → selecciona el documento.
3. Arrastra un recuadro sobre el PDF donde quieres que aparezca la firma.
4. Elige el perfil, ingresa la contraseña, presiona **Firmar documento**.
5. Elige dónde guardar el PDF firmado.

## Dónde se guardan los datos

- Perfiles y copias de los `.p12`: `%USERPROFILE%\.firma-app-datos\`
- Las contraseñas **nunca** se guardan en disco; se piden en cada firma.

## Pendientes para producción (siguientes pasos sugeridos)

- [ ] Cifrar la carpeta de certificados con **DPAPI** de Windows (actualmente
      solo están protegidos por los permisos del sistema de archivos del usuario)
- [ ] Vista previa multi-página (hoy solo se posiciona en la página 1)
- [ ] Validación de la cadena de certificación contra las CAs raíz de ARCOTEL
- [ ] Timestamp (TSA) para firmas con validez a largo plazo (LTV)
- [ ] Empaquetado como `.exe` standalone con PyInstaller, para no requerir Python
      instalado en la máquina del usuario final
- [ ] Firma de múltiples documentos en lote

## Nota sobre licencias

Este prototipo usa **pyHanko** (librería PAdES en Python, licencia MIT),
lo cual evita los costos/restricciones de licencia de librerías comerciales
como iText, manteniendo la app 100% libre de usar y distribuir.
