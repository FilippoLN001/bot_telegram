import logging
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import json
import telegram
from scraping import chiamataUnistudium,ricerca,chiudi
from selenium.webdriver.chrome.service import Service as ChromeService
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

SCELTA, LEZIONI, ESAMI, LAUREE = range(4)



def error_handler(update, context):
    """Log degli errori non gestiti."""
    logging.error(msg="Exception while handling an update:", exc_info=context.error)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about their gender."""
    user = update.message.from_user
    logger.info("L'utente %s ha iniziato la conversazione", user.first_name)
    reply_keyboard = [["Lezioni", "Esami", "Lauree"]]

    await update.message.reply_text(
        
        "Ciao! Il mio nome è Ricerca Lezioni Esami Lauree. "
        "invia /cancel per smettere di parlare con me.\n\n"
        "Cosa stai cercando?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Ricerca"
        ),
    )

    return SCELTA


async def scelta(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

 try:
    
    pass
    user = update.message.from_user
    text = update.message.text
    logger.info("L'utente %s, ha scelto: %s",user.first_name,update.message.text)
    if "Lezioni" in text:
       
        await update.message.reply_text("Scrivi la materia che stai ricercando...")
        return LEZIONI
    elif "Esami" in text:
        reply_keyboard = [["Esami primo anno", "Esami secondo anno", "Esami terzo anno"]]
        await update.message.reply_text("Di quale anno sei interessato/a?",
                                        reply_markup=ReplyKeyboardMarkup(
                                            reply_keyboard, one_time_keyboard=True, input_field_placeholder="?"
                                        ))
        return ESAMI
    else:
        return LAUREE
 
 except Exception as e:
        logger.error("Exception during scelta: %s", e, exc_info=True)
        return ConversationHandler.END

async def lezioni(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
 try:
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_path = "C:/Users/Filippo/Downloads/chrome-win64/chrome-win64/chromedriver.exe"
    chrome_service = webdriver.ChromeService(executable_path=chrome_path)
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
    driver.get("https://unistudium.unipg.it/cercacorso.php")
    user = update.message.from_user
    await update.message.reply_text("Ricercando la materia...")
    text = update.message.text
    if text.lower() == '/cancel':
            await update.message.reply_text("Hai annullato la ricerca. Digita /start per iniziare una nuova ricerca.")
            chiudi(driver)
            return ConversationHandler.END
    
    logger.info("L'utente %s, Ha scelto la materia : %s",user.first_name,update.message.text)
        #chiamate per la ricerca
    chiamataUnistudium(text, driver) 
    paginated_results = paginate_text(ricerca(driver))
    

    if not bool(paginated_results):
        await update.message.reply_text("Nessun risultato trovato riprova.")
        return LEZIONI
    else:
        sent_pages = set()
        for page in paginated_results:
            print("ciclo delle pagine")
            await update.message.reply_text(page)
            sent_pages.add(page)
            logger.info("paginazione del risultato")
    chiudi(driver)
    return await menu(update, context)
    
 except ValueError as ve:
    await update.message.reply_text(str(ve))
    return LEZIONI
 except telegram.error.BadRequest as bad_request_exception:
    if "Message text is empty" in str(bad_request_exception):
        await update.message.reply_text("La materia cercata non è valida. Per favore, riprova.")
    else:
        # Stampa il messaggio di errore solo se non è causato da un risultato generico o errato
        await update.message.reply_text("Il risultato è generico o errato riprova.")
    return LEZIONI
 except Exception as e:
        logger.error("Exception during lezioni: %s", e, exc_info=True)
        return ConversationHandler.END

async def esami(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Gestisci il messaggio dell'utente durante lo stato ESAMI
    user_data = context.user_data
    text = update.message.text
    context.user_data["choice"] = text
    user_data = user_data["choice"]
    print("prima scelta ", user_data)

    reply_keyboard = [["Esami primo anno", "Esami secondo anno", "Esami terzo anno"]]

    await update.message.reply_text(
        "Di quale anno sei interessato/a?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="?"
        ),
    )

    print(ESAMI)
    return ESAMI
    

async def lauree(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Gestisci il messaggio dell'utente durante lo stato LAUREE
    """Se entra in lauree visualizza tutte le date delle laure del dipartimento"""

    user = update.message.from_user
    logger.info("Utente: %s ha scelto lauree.", user.first_name)
    user_data = context.user_data
    text = update.message.text
    context.user_data["choice"] = text
    user_data = user_data["choice"]
    print("scelta ", user_data)
    file = open('database.json')
    data = json.load(file)
    await update.message.reply_text("Ecco a te le date delle prossime lauree :")
    Lauree_2023 = data.get('Lauree 2023-2024', [])
    formatted_data = '\n\n'.join([
        f"Data: {lezione['Data : ']} , \nOrario: {lezione['Orario : ']},"
        f"\nLink aula : {lezione['Link : ']}"
        for lezione in Lauree_2023])
    await update.message.reply_text(formatted_data)
    return await menu(update, context)

async def anno(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Se entra in anno deve scegliere l'anno che vuole visionare le lezioni"""
    user_data = context.user_data
    text = update.message.text
    context.user_data["choice"] = text
    user_data = user_data["choice"]
    print("seconda scelta ", user_data)
    file = open('database.json')
    data = json.load(file)
    if "Esami primo anno" in user_data:
        Esami_primo_anno = data.get('Esami_primo_anno', [])
        formatted_data = '\n\n'.join([
            f"{lezione['Materia : ']} \n- Docente: {lezione['Docente : ']}\nOrario: {lezione['Orario : ']}\nAula: {lezione['Aula : ']}"
            f"\nLink esame: {lezione['Link : ']}"
            for lezione in Esami_primo_anno])
        await update.message.reply_text(formatted_data)

    elif "Esami secondo anno" in user_data:
        Esami_secondo_anno = data.get('Esami_secondo_anno', [])
        formatted_data = '\n\n'.join([
            f"{lezione['Materia : ']} \n- Docente: {lezione['Docente : ']}\nOrario: {lezione['Orario : ']}\nAula: {lezione['Aula : ']}"
            f"\nLink esame: {lezione['Link : ']}"
            for lezione in Esami_secondo_anno])
        await update.message.reply_text(formatted_data)

    elif "Esami terzo anno" in user_data:
        Esami_terzo_anno = data.get('Esami_terzo_anno', [])
        formatted_data = '\n\n'.join([
            f"{lezione['Materia : ']} \n- Docente: {lezione['Docente : ']}\nOrario: {lezione['Orario : ']}\nAula: {lezione['Aula : ']}"
            f"\nLink esame: {lezione['Link : ']}"
            for lezione in Esami_terzo_anno])
        await update.message.reply_text(formatted_data)

    else:
        await update.message.reply_text("Non ho trovato niente che corrisponda a quello che mi hai chiesto riprova scrivendo\n /cancel e riavvia il bot")

    return await menu(update, context)
 

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("L'utente %s ha richiesto il menu.", user.first_name)

    # Messaggio di menu
    reply_keyboard = [["Lezioni", "Esami", "Lauree"]]
    await update.message.reply_text(
        "Ecco a te il link delle lezioni della materia che stavi cercando,"
        "Per cancellare la concersazone digita /cancel oppure ricerca una nuova lezione.",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Ricerca"
        ),
    )
    return SCELTA

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Ciao! Grazie per aver usato il bot spero che sia stato d'auito...", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("6360134762:AAEKs4sxvXKAffJsVV0V4UWZANAySMLiAxc").build()
    application.add_handler(CommandHandler("menu", menu))

    application.add_error_handler(error_handler)
    # Add conversation handler with the states 
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        
        states={  
           SCELTA: [MessageHandler(filters.Regex("^Lezioni$"),scelta),
                    MessageHandler(filters.Regex("^Lauree$"), lauree),
                    MessageHandler(filters.Regex("^Esami$"), esami)],

            LEZIONI: [MessageHandler(filters.TEXT,lezioni)],

            ESAMI: [MessageHandler(filters.Regex("^(Esami primo anno|Esami secondo anno|Esami terzo anno)$"),anno)],

            LAUREE: [MessageHandler(filters.Regex("^Lauree$"), lauree)],
            
        },
        
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

def paginate_text(text, max_length=2048):
    if len(text) <= max_length:
        print(len(text))
    pages = []
    start = 0
    while start < len(text):
        print("sono dentro while")
        end = start + max_length
        pages.append(text[start:end])
        start = end
        print("ciclo quante volte conto lo start :",start)
    return pages

if __name__ == "__main__":
    main()


