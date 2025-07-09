import os
import hvac
import io
import base64
import qrcode

def get_secret_from_vault(secret_path, secret_name):
    """Récupère un secret depuis HashiCorp Vault."""
    try:
        client = hvac.Client(
            url=os.environ['VAULT_ADDR'],
            token=os.environ['VAULT_TOKEN'],
        )
        mount_point = 'secret'

        response = client.secrets.kv.v2.read_secret_version(
            mount_point=mount_point,
            path=secret_path,
        )

        return response['data']['data'][secret_name]
    except Exception as e:
        print(f"Erreur lors de la récupération du secret depuis Vault: {e}")
        # En cas d'échec, on utilise une valeur par défaut pour éviter de crasher
        return 'default-secret-key-for-dev-only'

def generate_qr_code(data):
    """Génère une image de QR Code en base64."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{img_str}"
