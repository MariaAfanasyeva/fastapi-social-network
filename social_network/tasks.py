####### НИХУЯ НЕ РАБОТАЕТ В РБ, ПОЭТОМУ ИЩИ СЕРВИС ДЛЯ ОТПРАВКИ СООБЩЕНИЙ (НА КРАЙНЯК, ПИШИ СВОЙ SMTP-SERVER)



# from dotenv import load_dotenv
# import os


# import sib_api_v3_sdk
# from sib_api_v3_sdk.rest import ApiException

# load_dotenv()

# SECRET_KEY = os.environ.get("BREVO_API_KEY")

# configuration = sib_api_v3_sdk.Configuration()

# configuration.api_key["api-key"] = SECRET_KEY    

# api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

# def send_email(subject, html, to_address=None, receiver_username=None):
#     subject = subject
#     sender = {"name": "Maryia", "email": "masha.afanaseva0192@gmail.com"}
#     html_content = html
    
#     if to_address:
#         # You can add multiple email accounts to which you want to send the mail in this list of dicts
#         to = [{"email": "masha.afanaseva0192@gmail.com", "name": "Maryia"},
#               {"email": to_address, "name": receiver_username}]
#     else:
#         to = [{"email": "masha.afanaseva0192@gmail.com", "name": "Maryia"}]

#     # Create a SendSmtpEmail object
#     send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=to, html_content=html_content, sender=sender, subject=subject)

#     try:
#         # Send the email
#         api_response = api_instance.send_transac_email(send_smtp_email)
#         print(api_response)
#         return {"message": "Email sent successfully!"}
#     except ApiException as e:
#         print("Exception when calling SMTPApi->send_transac_email: %s\n" % e)
        
        
# content = "Hello from the other side"
# html = f"<h3>{content}</h3>"
# subject = "Test email from Brevo"
# to_address = "masha.afanaseva0129@gmail.com"
# receiver_username = "Maha Afanasyeva"
# print("Sending mail...")

# email_response = send_email(subject, html, to_address, receiver_username)

# print(email_response)


###################################

import logging
from json import JSONDecodeError

from databases import Database
from social_network.database import post_table
import httpx

from social_network.config import config

logger = logging.getLogger(__name__)


class APIResponseError(Exception):
    pass


async def _generate_cute_creature_api(prompt: str):
    logger.debug("Creating cute creature")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://api.deepai.org/api/cute-creature-generator",
                data={"text": prompt},
                headers={"api-key": "c629c015-40e2-4acf-a09e-34273e9abe44"},
                timeout=60
            )
            logger.debug(response)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as err:
            raise APIResponseError(
                f"API request failed with status code {err.response.status_code}"
            ) from err
        except (JSONDecodeError, TypeError) as err:
            raise APIResponseError("API response parsing failed") from err
        
        
async def generate_and_add_to_post(
    post_id: int,
    post_url: str,
    database: Database,
    prompt: str = "A blue shorthair cat is sitting on a couch"
):
    try:
        response = await _generate_cute_creature_api(prompt)
    except APIResponseError:
        return {"message": "Something went wrong"}
    
    logger.debug("Connecting to database to update post")
    
    query = (
        post_table.update()
        .where(post_table.c.id == post_id)
        .values(image_url=response["output_url"])
    )
    logger.debug(query)
    
    await database.execute(query)
    
    logger.debug("Database connection in background task closed")
    
    return {"post_url": post_url, "image_url": response["output_url"]}