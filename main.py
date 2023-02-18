# main.py
import requests
import xbmcgui
import qrcode
import xbmcplugin
import xbmc
import sys
import os
import json


file_config = os.path.join(os.path.dirname(__file__), 'config.json')

app_data = {
    "name": "Kodi",
    "description": "A sample app",
    "permission": ["write:notes"]
}

if os.path.exists(file_config):
    with open(file_config) as config_file:
        config_data = json.load(config_file)

        if 'appSecret' in config_data:
            session_data = {
                "appSecret": config_data['appSecret']
            }
        else:
            config_data['appSecret'] = app_json['secret']
            with open(file_config, 'w') as config_file:
                json.dump(config_data, config_file, indent=4)

            session_data = {
                "appSecret": app_json['secret']
            }
else:
    app_response = requests.post("https://www.foxyhole.io/api/app/create", json=app_data)
    app_json = app_response.json()

    config_data = {
        'appSecret': app_json['secret']
    }
    with open(file_config, 'w') as config_file:
        json.dump(config_data, config_file, indent=4)

    session_data = {
        "appSecret": app_json['secret']
    }

# Effettua la richiesta POST per generare una sessione
session_response = requests.post("https://www.foxyhole.io/api/auth/session/generate", json=session_data)
session_json = session_response.json()

# Crea una finestra di tipo xbmcgui.WindowDialog
window = xbmcgui.WindowDialog()

# Verifica se l'utente sta usando Windows o Linux
platform = sys.platform
if platform == "win32":
    # Se l'utente sta usando Windows, usa la cartella temporanea come directory scrivibile
    directory = os.environ["TEMP"]
else:
    # Se l'utente sta usando Linux, usa la cartella home come directory scrivibile
    directory = os.path.expanduser("~")


# Verifica se la richiesta di generazione della sessione è stata effettuata con successo
if session_response.ok:
    print("Sessione generata con successo")
    print(session_json)
    print(session_json['url'])
    url = session_json['url']
    token = session_json['token']
    xbmc.log(f"Session url: {url}", level=2) 
    xbmc.log(f"Token: {token}", level=2) 

    # Crea un'etichetta con il testo "Scansiona il QR code"
    label = xbmcgui.ControlLabel(550, 100, 600, 50, "Scansiona il QR code:")

    # Crea l'immagine del QR code a partire dall'URL della sessione
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img_file = os.path.join(directory, "foxyhole_session_qr.png")
    img.save(img_file)

    # Crea un controllo immagine con l'immagine del QR code
    qr_control = xbmcgui.ControlImage(200, 50, 300, 300, img_file)

    lblAppSecret = xbmcgui.ControlLabel(550, 150, 600, 50, f"appSecret: {session_data['appSecret']}")

    # Crea un'etichetta con il token e l'URL della sessione
    token_label = xbmcgui.ControlLabel(550, 200, 600, 50, f"Token: {token}")


    button = xbmcgui.ControlButton(550, 300, 600, 50, 'Esegui richiesta')
    button.onClick(execute_request)

    # Aggiunge i controlli alla finestra
    window.addControl(label)
    window.addControl(qr_control)
    window.addControl(lblAppSecret)
    window.addControl(token_label)
    window.addControl(button)

def execute_request():
    response = requests.post("https://www.foxyhole.io/api/auth/session/userkey", json={"appSecret": session_data['appSecret'], "token": token})
    xbmc.log(f"userkey: {response}", level=2)

    # Mostra la finestra con l'etichetta e l'immagine del QR code
    window.show()
    window.doModal()

else:
    raise Exception("Errore durante la generazione della sessione, codice di stato: {}".format(session_response.status_code))

# Chiude il plugin
xbmcplugin.endOfDirectory(int(sys.argv[1]))
