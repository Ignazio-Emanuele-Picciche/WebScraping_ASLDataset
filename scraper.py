# TODO: fare driver.get(CART_URL) per andare direttamente al carrello


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.service import Service as ChromeService
import time

# --- Configurazione Iniziale ---

# URL della pagina di ricerca iniziale
START_URL = "https://dai.cs.rutgers.edu/dai/s/dai"
CART_URL = "https://dai.cs.rutgers.edu/dai/s/cart?redirect=dai"

# Specifica il percorso del chromedriver.
# Questo codice presume che 'chromedriver' si trovi nella stessa cartella dello script.
# service = ChromeService(executable_path='./chromedriver') # Rimuovi o commenta questa riga

# Seleziona il tuo browser. Assicurati di avere il WebDriver corrispondente.
driver = webdriver.Chrome(executable_path='./chromedriver')
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

                # Flag per sapere se abbiamo trovato qualcosa da scaricare
                items_found = False

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
                        By.XPATH, "//input[@type='checkbox' and not(@disabled)]"
                    )
                    print(f"     Trovate {len(checkboxes)} checkbox da selezionare.")

                    # Se non ci sono checkbox, esci dal ciclo delle occorrenze
                    if not checkboxes:
                        print("     Nessuna checkbox trovata per questo segno. Passo al successivo.")
                        break # Esce dal ciclo while delle pagine di occorrenze

                    items_found = True # Abbiamo trovato qualcosa!
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
                        # Attendi che il link alla pagina successiva delle occorrenze sia cliccabile
                        next_occ_link = wait.until(
                            EC.element_to_be_clickable(
                                (By.XPATH, f"//a[text()='{occ_page}']")
                            )
                        )
                        next_occ_link.click()
                    except TimeoutException:
                        # Non ci sono più pagine di occorrenze
                        print("     Finite le pagine di occorrenze per questo segno.")
                        break

                # Se non è stato trovato nessun item, non andare al carrello.
                # Salta direttamente al blocco finally per tornare indietro.
                if not items_found:
                    print(f"--- Nessun item da scaricare per '{sign_name}'. Si torna indietro. ---")
                    # L'uso di 'continue' qui non funzionerebbe perché siamo dentro un try.
                    # Lasciamo che il codice proceda al blocco finally.
                else:
                    # 4. Vai al carrello e scarica
                    print(f"--- Navigazione al carrello per scaricare '{sign_name}' ---")
                    # Clicca sul pulsante per andare al carrello invece di usare driver.get()
                    # Questo può aiutare a mantenere lo stato della sessione.
                    go_to_cart_button = wait.until(
                        EC.element_to_be_clickable(
                            (By.XPATH, "/html/body/div[2]/table[2]/tbody/tr[4]/td/input[1]")
                        )
                    )
                    go_to_cart_button.click()

                    time.sleep(
                        2
                    )  # Aggiungi un piccolo ritardo per il caricamento della pagina
                    try:
                        # Attendi che il form del carrello specifico sia presente
                        wait.until(
                            EC.presence_of_element_located((By.NAME, "downloadcartform"))
                        )
                        print("Form del carrello (downloadcartform) trovato.")

                        # Attendi che i pulsanti di download appaiano nel form del carrello
                        download_buttons = wait.until(
                            EC.presence_of_all_elements_located(
                                (
                                    By.CSS_SELECTOR,
                                    "form[name=downloadcartform] button[name=resource_button]",
                                )
                            )
                        )

                        if not download_buttons:
                            raise TimeoutException(
                                "Nessun pulsante di download trovato nel carrello."
                            )

                        print(
                            f"Trovati {len(download_buttons)} pulsanti di download nel carrello."
                        )
                        
                        num_downloads = len(download_buttons)
                        base_selector = "form[name=downloadcartform] button[name=resource_button]"

                        # Itera su ogni pulsante usando un indice
                        for i in range(num_downloads):
                            try:
                                print(
                                    f"Tentativo di download {i + 1}/{num_downloads}..."
                                )
                                
                                # Ad ogni iterazione, ricarica la lista di tutti i pulsanti
                                # per evitare problemi di elementi "stantii" (stale)
                                all_buttons = wait.until(
                                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, base_selector))
                                )
                                
                                # Seleziona il pulsante specifico per questa iterazione
                                download_button = all_buttons[i]

                                # Scorri fino al pulsante per assicurarti che sia visibile
                                driver.execute_script(
                                    "arguments[0].scrollIntoView({block: 'center'});",
                                    download_button,
                                )
                                time.sleep(1)

                                # Clicca il pulsante
                                download_button.click()

                                print(f"Download {i + 1} avviato.")
                                # Attendi che la pagina si stabilizzi e il download parta
                                time.sleep(5) 

                            except Exception as e:
                                print(
                                    f"Errore durante il tentativo di download {i + 1}: {e}"
                                )
                                print("Provo con il prossimo pulsante...")
                                continue

                        print(
                            f"Tutti i download per '{sign_name}' sono stati avviati. Attendi 10 secondi..."
                        )
                        time.sleep(10) # Ridotto il tempo di attesa

                    except TimeoutException:
                        print(
                            f"ERRORE: Impossibile trovare pulsanti di download nel carrello per '{sign_name}'."
                        )
                        # --- DEBUGGING ---
                        screenshot_path = "cart_screenshot.png"
                        source_path = "cart_page_source.html"
                        driver.save_screenshot(screenshot_path)
                        with open(source_path, "w", encoding="utf-8") as f:
                            f.write(driver.page_source)
                        print(f"Screenshot salvato in: {screenshot_path}")
                        print(f"Codice sorgente della pagina salvato in: {source_path}")
                        # --- FINE DEBUGGING ---

            except (TimeoutException, NoSuchElementException) as e:
                print(f"     Errore durante il processo per '{sign_name}': {e}")
                # Un errore qui è considerato come una fine del processo per questo segno.
                # Il blocco finally si occuperà di tornare indietro.
                pass

            finally:
                # 5. Torna alla pagina dei risultati per la prossima iterazione del ciclo FOR
                print("Tornando alla pagina dei risultati...")
                driver.get(START_URL) # Torna alla pagina di ricerca iniziale

                try:
                    # Riesegui la ricerca per visualizzare la lista dei risultati
                    print("Rieseguendo la ricerca per tornare alla lista...")
                    submit_button = wait.until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'btn-success')]"))
                    )
                    driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
                    time.sleep(1)
                    submit_button.click()

                    # Se eravamo su una pagina > 1, naviga fino a quella pagina
                    if page_number > 1:
                        print(f"Navigando di nuovo alla pagina {page_number}...")
                        for p in range(2, page_number + 1):
                            next_p_link = wait.until(EC.element_to_be_clickable((By.XPATH, f"//a[text()='{p}']")))
                            next_p_link.click()
                            time.sleep(1) # Attendi caricamento pagina

                    # Attendi che la tabella dei risultati sia di nuovo visibile
                    wait.until(
                        EC.presence_of_element_located((By.XPATH, "//*[@id='main']/table//a"))
                    )
                    print(f"Tornato alla pagina dei risultati {page_number}.")

                except Exception as ex:
                    print(f"ERRORE CRITICO nel tornare alla pagina dei risultati: {ex}")
                    # Se questo blocco fallisce, non possiamo continuare.
                    page_number = -1 # Segnale per interrompere il ciclo while esterno

        # Se page_number è stato impostato a -1, esci anche dal ciclo while
        if page_number == -1:
            break

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
