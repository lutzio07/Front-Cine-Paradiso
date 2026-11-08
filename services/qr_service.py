import base64
import io
import qrcode

def generar_qr_data_url(codigo_qr):
    imagen = qrcode.make(codigo_qr)
    buffer = io.BytesIO()
    imagen.save(buffer, format="PNG")
    codificado = base64.b64encode(buffer.getvalue()).decode("ascii")
    # El formato data URL permite mostrar la imagen sin guardar un archivo.
    return f"data:image/png;base64,{codificado}"