
from bs4 import BeautifulSoup

from selenium.common.exceptions import  NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Inizializza il browser

def chiamataUnistudium(ricerca,driver):
# Trova un campo di input e inserisci dati
    
    input_element = driver.find_element(By.NAME, "query")
    input_element.send_keys(ricerca)

        # Trova il bottone e cliccalo
    button_element = driver.find_element(By.NAME, "submit")
    button_element.click()
   # try:
        # Aspetta fino a 10 secondi che la tabella con le informazioni desiderate sia presente
    wait = WebDriverWait(driver, 10)
   # except TimeoutException:
    # # Se la tabella non è presente, controlla se ci sono "0 risultati"
    #     try:
    #         soup = BeautifulSoup(driver.page_source, 'html.parser')
    #         error_message = soup.find('form').find_all('br')[1].next_sibling.strip()
    #         if "0 risultati" in error_message:
    #             raise ValueError("Nessun risultato trovato. Riprova con un'altra ricerca.")
    #     except (AttributeError, IndexError, NoSuchElementException):
    #     # Se si verifica un'eccezione durante la ricerca degli elementi nel DOM, gestisci di conseguenza
            
    #         raise ValueError("Errore sconosciuto durante la ricerca.")
    # else:
    #     pass
        
def ricerca(driver):
# Estrai il testo della tabella con BeautifulSoup
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    element = soup.find('table')

    # Esempio: Estrai il testo di un elemento con una classe specifica
    result_string = ''
    if element:
        table_rows = element.find_all('tr')
        for row in table_rows:
            columns = row.find_all('td')
            for col in columns:
                result_string += col.text + "\n"
    else:
        # Cerca la stringa "0 risultati" direttamente nel contenuto HTML
        try:
            br_element = soup.find('br')
            if br_element:
                error_message = br_element.text
                if "0 risultati" in error_message:
                    result_string = "Nessun risultato trovato. Riprova con un'altra ricerca."
        except (AttributeError, IndexError, NoSuchElementException):
            # Se si verifica un'eccezione durante la ricerca degli elementi nel DOM, gestisci di conseguenza
            result_string = "Errore sconosciuto durante la ricerca."

    return result_string

def chiudi(driver):
# Chiudi il browser
    driver.quit()
    