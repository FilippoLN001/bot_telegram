
from bs4 import BeautifulSoup

from selenium.common.exceptions import  NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Inizializza il browser

def chiamataUnistudium(ricerca, driver):
    # Trova un campo di input e inserisci dati
    input_element = driver.find_element(By.NAME, "query")
    input_element.send_keys(ricerca)
    # Trova il bottone e cliccalo
    button_element = driver.find_element(By.NAME, "submit")
    button_element.click()
    # Aspetta fino a 10 secondi che la tabella con le informazioni desiderate sia presente
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))

def ricerca(driver):
    # Estrai il testo della tabella con BeautifulSoup
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    element = soup.find('table')

    result_string = ''
    if element:
        table_rows = element.find_all('tr')
        for row in table_rows:
            columns = row.find_all('td')
            from urllib.parse import urljoin
            for col in columns:
                link_tag = col.find('a')
                if link_tag:
                    # Estrai l'attributo href dal tag <a>
                    link = link_tag.get('href')
                    link = urljoin(driver.current_url, link)
                    result_string += f"Link al meeting: {link}\n"
                else:
                    result_string += col.text + "\n"
    else:
        try:
            br_element = soup.find('br')
            if br_element:
                error_message = br_element.text
                if "0 risultati" in error_message:
                    result_string = "Nessun risultato trovato. Riprova con un'altra ricerca."
        except (AttributeError, IndexError, NoSuchElementException):
            result_string = "Errore sconosciuto durante la ricerca."

    return result_string

def chiudi(driver):
    # Chiudi il browser
    driver.quit()