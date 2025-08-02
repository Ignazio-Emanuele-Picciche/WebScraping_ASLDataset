# TODO: fare driver.get(CART_URL) per andare direttamente al carrello


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time

# --- Configurazione Iniziale ---

# URL della pagina di ricerca iniziale
START_URL = "https://dai.cs.rutgers.edu/dai/s/dai"
CART_URL = "https://dai.cs.rutgers.edu/dai/s/cart?redirect=dai"

# Seleziona il tuo browser. Assicurati di avere il WebDriver corrispondente.
driver = webdriver.Chrome()
wait = WebDriverWait(driver, 20)

driver.get(START_URL)

# --- FASE DI LOGIN AUTOMATICO ---
try:
    print("\n--- Sto cercando e cliccando il pulsante 'Login'... ---")

    # Trova e clicca il pulsante di login
    login_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "/html/body/header/div/ul/li[4]/a"))
    )
    login_button.click()

    # Inserisci email
    print("Inserendo l'email...")
    email_field = wait.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                "/html/body/center/center/form/center/table[1]/tbody/tr[3]/td[3]/input",
            )
        )
    )
    email_field.send_keys("ie.picciche@alcampus.it")

    # Inserisci password
    print("Inserendo la password...")
    password_field = wait.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                "/html/body/center/center/form/center/table[1]/tbody/tr[4]/td[3]/input",
            )
        )
    )
    password_field.send_keys("foDwig-pithod-6wakra")

    # Conferma il login
    print("Cliccando sul pulsante di conferma login...")
    confirm_button = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "/html/body/center/center/form/center/table[1]/tbody/tr[5]/td[3]/input[1]",
            )
        )
    )
    confirm_button.click()

    print("Login effettuato con successo.")
except TimeoutException:
    print(
        "ERRORE: Impossibile completare il login automatico. Verifica i selettori o la pagina."
    )
    driver.quit()
    exit()

# --- NUOVO PASSAGGIO: CLICCARE SUBMIT ---
try:
    print("\\n--- Sto cercando e cliccando il pulsante 'Submit' (Search)... ---")

    # Scorri fino in fondo alla pagina per trovare il pulsante submit
    print("Scorrendo verso il fondo della pagina...")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)  # Attendi che lo scroll sia completato

    # Prima verifichiamo tutti i pulsanti presenti nella pagina
    print("Debug: Cercando tutti i pulsanti nella pagina...")
    all_buttons = driver.find_elements(By.XPATH, "//button | //input[@type='submit']")
    print(f"Trovati {len(all_buttons)} pulsanti")

    for i, btn in enumerate(all_buttons):
        try:
            tag_name = btn.tag_name
            btn_class = btn.get_attribute("class")
            btn_type = btn.get_attribute("type")
            btn_text = btn.text
            print(
                f"  Pulsante {i+1}: tag='{tag_name}', class='{btn_class}', type='{btn_type}', text='{btn_text}'"
            )
        except:
            print(f"  Pulsante {i+1}: impossibile leggere attributi")

    # Proviamo diversi selettori per trovare il pulsante submit
    submit_button = None
    selectors = [
        "//button[@type='submit' and contains(@class, 'btn-success')]",
        "//button[contains(@class, 'btn-success') and contains(text(), 'SUBMIT')]",
        "//button[contains(@class, 'btn-success')]",
        "//button[@type='submit']",
        "//button[contains(text(), 'SUBMIT')]",
        "//input[@type='submit']",  # Fallback per input submit
    ]

    for selector in selectors:
        try:
            print(f"Provando selettore: {selector}")
            submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
            print(f"Pulsante trovato con selettore: {selector}")
            break
        except TimeoutException:
            print(f"Selettore fallito: {selector}")
            continue

    if submit_button:
        # Scorri verso il pulsante per assicurarsi che sia visibile
        driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
        time.sleep(1)
        submit_button.click()
        print("Pulsante cliccato. Ora si procede con l'analisi dei risultati.")
    else:
        raise TimeoutException("Nessun pulsante submit trovato")

except TimeoutException:
    print("ERRORE: Impossibile trovare il pulsante 'Submit'/'Search' dopo il login.")
    print("Assicurati di essere sulla pagina giusta o che il pulsante sia visibile.")
    driver.quit()
    exit()


# --- FASE DI SCRAPING DELLE PAGINE DEI RISULTATI ---
page_number = 1
while True:
    print(f"\\n--- Elaborazione Pagina dei Risultati {page_number} ---")
    try:
        # Attendi che la tabella dei risultati sia caricata dopo aver cliccato submit
        wait.until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='main']/table//a"))
        )

        # Trova tutti i link delle occorrenze nella pagina corrente (colonna Occurrences)
        sign_links = driver.find_elements(
            By.XPATH,
            "//*[@id='main']/table/tbody/tr/td[2]/a | //*[@id='main']/table/tbody/tr/td[2]/strong/a",
        )

        if not sign_links:
            print(
                "Nessun link di occorrenza trovato in questa pagina. Potrebbe essere la fine."
            )
            break

        print(f"Trovati {len(sign_links)} link di occorrenze in questa pagina.")

        # Itera su ogni link di segno nella pagina
        for i in range(len(sign_links)):
            # È necessario ritrovare gli elementi ad ogni ciclo perché la pagina si ricarica
            current_sign_links = wait.until(
                EC.presence_of_all_elements_located(
                    (
                        By.XPATH,
                        "//*[@id='main']/table/tbody/tr/td[2]/a | //*[@id='main']/table/tbody/tr/td[2]/strong/a",
                    )
                )
            )
            link = current_sign_links[i]
            sign_name = link.text

            print(
                f"  -> Elaborazione occorrenze per: '{sign_name}' (Link {i+1} di {len(sign_links)})"
            )

            # 1. Clicca sul link per andare alla pagina delle occorrenze
            link.click()

            try:
                # 2. Una volta sulla pagina dell'occorrenza, pulisci il carrello
                print("--- Pulizia del carrello ---")
                try:
                    clear_cart_button = wait.until(
                        EC.element_to_be_clickable(
                            (
                                By.XPATH,
                                "/html/body/div[2]/table[2]/tbody/tr[4]/td/input[2]",
                            )
                        )
                    )
                    clear_cart_button.click()
                    print("Pulsante 'clear collection' cliccato.")

                    # Gestisci l'alert di conferma
                    try:
                        WebDriverWait(driver, 3).until(EC.alert_is_present())
                        alert = driver.switch_to.alert
                        alert.accept()
                        print("Alert di conferma gestito.")
                    except TimeoutException:
                        print("Nessun alert di conferma trovato, si prosegue.")
                    time.sleep(2)

                except (TimeoutException, NoSuchElementException):
                    print(
                        "Pulsante 'clear collection' non trovato o non cliccabile. Forse il carrello era già vuoto."
                    )

                # 3. Aggiungi tutte le occorrenze al carrello
                occ_page = 1
                while True:
                    print(
                        f"     Elaborazione pagina occorrenze {occ_page} per '{sign_name}'"
                    )
                    wait.until(
                        EC.presence_of_element_located(
                            (By.XPATH, "//*[@id='main']/form/table")
                        )
                    )

                    checkboxes = driver.find_elements(
                        By.XPATH, "//input[@type='checkbox']"
                    )
                    print(f"     Trovate {len(checkboxes)} checkbox da selezionare.")
                    for checkbox in checkboxes:
                        if not checkbox.is_selected():
                            checkbox.click()
                            time.sleep(0.2)

                    add_to_cart_button = wait.until(
                        EC.element_to_be_clickable(
                            (By.XPATH, "//*[@id='download_collection']")
                        )
                    )
                    add_to_cart_button.click()
                    print(
                        f"     Occorrenze dalla pagina {occ_page} aggiunte al carrello."
                    )

                    try:
                        occ_page += 1
                        next_occ_link = driver.find_element(
                            By.XPATH, f"//a[text()='{occ_page}']"
                        )
                        next_occ_link.click()
                    except NoSuchElementException:
                        print("     Finite le pagine di occorrenze per questo segno.")
                        break

                # 4. Vai al carrello e scarica
                print(f"--- Navigazione al carrello per scaricare '{sign_name}' ---")
                driver.get(CART_URL)
                time.sleep(
                    2
                )  # Aggiungi un piccolo ritardo per il caricamento della pagina

                try:
                    print("Navigazione alla pagina del carrello...")
                    # È buona norma attendere un elemento specifico della pagina del carrello
                    # per assicurarsi che sia completamente caricata.
                    wait.until(
                        EC.visibility_of_element_located(
                            (
                                By.XPATH,
                                "//th[contains(., 'Download Selected Items (by row)')]",
                            )
                        )
                    )
                    print("Pagina del carrello caricata correttamente.")

                    # --- CORREZIONE CHIAVE: XPath aggiornato ---
                    # I pulsanti sono <input type="submit">, non <button>.
                    # Questo selettore trova l'ultima cella (td) di ogni riga (tr) e cerca l'input corretto al suo interno.
                    download_buttons_xpath = (
                        "//tr/td[last()]//input[@type='submit' and @value='Download']"
                    )

                    # Attendi che almeno un pulsante di download sia visibile
                    wait.until(
                        EC.presence_of_element_located(
                            (By.XPATH, download_buttons_xpath)
                        )
                    )

                    # Trova il numero totale di pulsanti di download
                    num_download_buttons = len(
                        driver.find_elements(By.XPATH, download_buttons_xpath)
                    )

                    if num_download_buttons == 0:
                        raise TimeoutException(
                            "Nessun pulsante di download trovato nel carrello."
                        )

                    print(f"Trovati {num_download_buttons} pulsanti di download.")

                    # Itera usando un indice per evitare problemi di elementi 'stale' (StaleElementReferenceException)
                    for index in range(num_download_buttons):
                        try:
                            # Ritrova tutti i pulsanti ad ogni iterazione, poiché la pagina potrebbe
                            # ricaricarsi o cambiare dopo un'azione.
                            buttons = wait.until(
                                EC.presence_of_all_elements_located(
                                    (By.XPATH, download_buttons_xpath)
                                )
                            )

                            # Seleziona il pulsante corretto per questa iterazione
                            button_to_click = buttons[index]

                            print(
                                f"Tentativo di clic sul pulsante di download {index + 1}/{num_download_buttons}..."
                            )

                            # Scorri fino al pulsante per assicurarti che sia visibile
                            driver.execute_script(
                                "arguments[0].scrollIntoView({block: 'center'});",
                                button_to_click,
                            )
                            time.sleep(
                                1
                            )  # Piccola pausa per la stabilizzazione dello scroll

                            # --- MIGLIORAMENTO: Click più affidabile con JavaScript ---
                            # Questo metodo è spesso più robusto di un .click() standard
                            driver.execute_script(
                                "arguments[0].click();", button_to_click
                            )

                            print(f"Download {index + 1} avviato con successo.")

                            # Attendi un po' per permettere l'avvio del download prima di procedere
                            time.sleep(5)

                        except Exception as e:
                            print(
                                f"Errore durante il click sul pulsante di download {index + 1}: {e}"
                            )
                            # Potresti voler aggiungere qui una logica per gestire l'errore,
                            # ad esempio continuando con il pulsante successivo.
                            continue

                    print(
                        f"Tutti i {num_download_buttons} download sono stati avviati. Attendi 10 secondi..."
                    )
                    time.sleep(10)

                except TimeoutException:
                    print(
                        "Errore: La pagina del carrello o i pulsanti di download non sono stati trovati entro il tempo limite."
                    )
                except Exception as e:
                    print(
                        f"Si è verificato un errore imprevisto durante il processo di download: {e}"
                    )

            except (TimeoutException, NoSuchElementException) as e:
                print(f"     Errore durante il processo per '{sign_name}': {e}")

            finally:
                # 5. Torna alla pagina dei risultati per il prossimo ciclo
                print("Tornando alla pagina dei risultati...")
                driver.get(START_URL)
                # Esegui di nuovo la ricerca per tornare allo stato precedente
                print("Rieseguendo la ricerca per tornare alla lista...")
                submit_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
                )
                driver.execute_script(
                    "arguments[0].scrollIntoView(true);", submit_button
                )
                time.sleep(1)
                submit_button.click()

                # Se eravamo in una pagina > 1, dobbiamo navigare di nuovo a quella pagina
                if page_number > 1:
                    for p in range(1, page_number):
                        try:
                            next_page_link = wait.until(
                                EC.element_to_be_clickable(
                                    (By.XPATH, "//a[text()='>']")
                                )
                            )
                            print(f"Tornando alla pagina {p + 1}...")
                            next_page_link.click()
                            wait.until(
                                EC.presence_of_element_located(
                                    (By.XPATH, "//*[@id='main']/table//a")
                                )
                            )
                        except TimeoutException:
                            print(f"Timeout: Impossibile tornare alla pagina {p + 1}.")
                            break

                print(f"Tornato alla pagina dei risultati {page_number}.")
                wait.until(
                    EC.presence_of_element_located((By.XPATH, "//*[@id='main']/table"))
                )

    except TimeoutException:
        print(
            "Timeout durante l'attesa del caricamento della pagina dei risultati. Interruzione."
        )
        break

    # Cerca il link per la pagina successiva e cliccalo
    try:
        # Selettore per il link della pagina successiva (il link con il testo ">")
        next_page_link = driver.find_element(By.XPATH, "//a[text()='>']")
        print(f"--- Passando alla pagina {page_number + 1} ---")
        next_page_link.click()
        page_number += 1
    except NoSuchElementException:
        print("\\n--- Tutte le pagine sono state elaborate. ---")
        break

# La fase di download è stata spostata nel ciclo, quindi questa parte non è più necessaria.
print("Lo script terminerà tra 30 secondi.")
time.sleep(30)

driver.quit()
print("Script terminato.")
