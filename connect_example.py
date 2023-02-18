#Importowanie biblioteki
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#import pandas as pd


# ustawiam lokalizację pliku chromedriver.exe kompaktybilnego z wersją chrome 
driver = webdriver.Chrome(executable_path=r"C:\WebDriver\bin\chromedriver.exe")


# wykonanie komendy "get", w tym wypadku analogicznie zadziałałoby requests.get()
# w ten sposób nawigujemy obiekt driver do strony wskazanej przez adres URL
driver.get('https://wroclaw.policja.gov.pl/dwr/form/159,Doba-w-liczbach.html?page=0')

# polecenie każe czekać do 10 sekund nim nie załaduje się nasz element, inaczej może wywalić błędem
wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.CLASS_NAME, "table-listing")))

# wait for the list to load
wait = WebDriverWait(driver, 10)
wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "table-listing")))

# skoro już się załadowałem to możemy wyciągnąć dane z tabelki na pierwszej stronie
tabelka = driver.find_elements_by_class_name("table-listing")

# rozdzielam tekst na wiersze gdzie separatorem jest znak nowej linii 
lines = tabelka[0].text.split('\n')

#przerzucam dane do fnalnego obiektu, pomijam pierwszy wiersz gdzie są nazwy kolumn
wynik = lines.copy()[1:]


# następnie będę przechodził przez kolejne strony tabeli i powtarzał powyższy ciąg poleceń

# namierzam się na element listy 
lista = driver.find_elements_by_id("meni_strony")

# wyszukuję maksymalną wartość na liście określającą ile raszy musze wykonać polecenie (3 element od końca)
koniec = int(lista[0].text.split('\n')[-3])

# jest jakaś blokada na stronie uniemożliwiająca odputanie więcej niż 9x, po tym czasie należy przeładować stronkę
for x in range(1, koniec):
    #pętla w pętli: niestety coś blokuje co jakiś czas połączenie, rozłączenie i ponowne połączenie pomaga
    if x % 6 == 0:
        driver.quit()
        driver = webdriver.Chrome(executable_path=r"C:\WebDriver\bin\chromedriver.exe")
    driver.get('https://wroclaw.policja.gov.pl/dwr/form/159,Doba-w-liczbach.html?page='+str(x))
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "table-listing")))
    tabelka = driver.find_elements_by_class_name("table-listing")
    lines = tabelka[0].text.split('\n')
    wynik.extend(lines[1:]) # polecenie append dodałoby całą listę jako jeden obiekt


driver.quit()

# wynik jest obecnie listą z wektorami 

