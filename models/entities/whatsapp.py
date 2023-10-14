import requests
import json

class WhatsApp:
    def __init__(self, token, idPhoneNumber):
        """
        Inicializa la clase WhatsApp.

        Parámetros:
        token: String. El token de autorización para la API de Facebook.
        idPhoneNumber: String. El número de teléfono ID asociado a la cuenta de Facebook.
        """

        self.token = token
        self.idPhoneNumber = idPhoneNumber
        self.url = f'https://graph.facebook.com/v17.0/{idPhoneNumber}/messages'
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

    def sendTemplate(self, numberPhone, templateName, nombrecomercial, code="es_ES"):
        """
        Envía un mensaje a través de la API de WhatsApp de Facebook.

        Parámetros:
        numberPhone: String. El número de teléfono al que se enviará el mensaje.
        templateName: String. El nombre de la plantilla aprobada que se utilizará para el mensaje.
        code: String. El código de idioma en el que se enviará el mensaje. Ejemplo: "en_US" para inglés (Estados Unidos).

        Devuelve:
        status_code: int. El código de estado de la respuesta.
        response_text: String. El texto de la respuesta.
        """
        data = {
            "messaging_product": "whatsapp",
            "to": numberPhone,
            "type": "template",
            "template": {
                "name": templateName,
                "language": {
                    "code": code
                },
                "components": [
                    {
                        "type": "header",
                        "parameters": [
                            {
                                "type": "text",
                                "text": nombrecomercial
                            }
                        ]
                    }
                ]
            }
        }

        response = requests.post(self.url, headers=self.headers, data=json.dumps(data))
        return response.status_code, response.text
    
    def sendMessage(self, numberPhone, message, code="en_US"):
        """
        Envía un mensaje a través de la API de WhatsApp de Facebook.

        Parámetros:
        numberPhone: String. El número de teléfono al que se enviará el mensaje.
        templateName: String. El nombre de la plantilla aprobada que se utilizará para el mensaje.
        code: String. El código de idioma en el que se enviará el mensaje. Ejemplo: "en_US" para inglés (Estados Unidos).

        Devuelve:
        status_code: int. El código de estado de la respuesta.
        response_text: String. El texto de la respuesta.
        """
        data = {
            "messaging_product": "whatsapp",
            "to": numberPhone,
            "type": "text",
            "text":{
                "body": message
            }
        }

        response = requests.post(self.url, headers=self.headers, data=json.dumps(data))
        return response.status_code, response.text
    


# Suponiendo que tienes tu token y número de teléfono ID
token = "EABmsLuH4fZAABO8xgJ8TeetKPlZCtOZAe6PsBgyAx8VHfaO3xpIPJIKsMX3ZAOz4ZCBVKMIWmkSluUcowAvmPGFbNDqZBcSy2gb4jJftiJ5sdnqZBeQOWu6JAZB4uNuGCv2lpfT7MXGZCnZCAXnAgL0iUPnxHxZCh21gIvhcW2ZBU34wzLKULxd5NLnKVv6YNmy4IZCX35TpfGK6YRenZCKRnEHxpQOdHNvPFhzbwm"
idPhoneNumber = "114366688398619"

whatsapp = WhatsApp(token, idPhoneNumber)

# Enviar un mensaje de texto
#recipient_phone_number = "56942199915"
#message_body = "Hola, este es un mensaje de prueba."
#status_code, response_text = whatsapp.sendMessage(recipient_phone_number, message_body)

#if status_code == 200:
#    print("Mensaje enviado exitosamente.")
#else:
#    print("Error al enviar el mensaje:", response_text)

# Enviar un mensaje usando una plantilla
#template_name = "welcome"
#nombrecomercial = "Rolando Rojas"
#status_code, response_text = whatsapp.sendTemplate(recipient_phone_number, template_name, nombrecomercial)

#if status_code == 200:
#    print("Mensaje de plantilla enviado exitosamente.")
#else:
#    print("Error al enviar el mensaje de plantilla:", response_text)