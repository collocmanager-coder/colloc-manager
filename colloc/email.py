from django.conf import settings
import requests

BREVO_API_BASE_URL = "https://api.brevo.com/v3.1/send"

def send_brevo_email(to_email, subject, text_content, html_content=None):
    """
    Envoie un email via l'API Brevo.
    
    Parameters:
        to_email (str): Adresse email du destinataire
        subject (str): Sujet de l'email
        text_content (str): Contenu texte de l'email
        html_content (str, optional): Contenu HTML de l'email. Si None, le texte sera utilisé
    Returns:
        response (dict): Résultat de l'API Brevo
    """

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "api-key": settings.BREVO_API_KEY
    }

    data = {
        "messages": [
            {
                "from": {
                    "email": settings.BREVO_SENDER_EMAIL,
                    "name": settings.BREVO_SENDER_NAME
                },
                "to": [{"email": to_email}],
                "subject": subject,
                "textContent": text_content,
                "htmlContent": html_content or text_content
            }
        ]
    }

    response = requests.post(BREVO_API_BASE_URL, headers=headers, json=data)

    try:
        response_data = response.json()
    except Exception:
        response_data = {"error": "Impossible de parser la réponse de Brevo"}

    return response.status_code, response_data
