#Importowanie biblioteki
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

# ustawiam lokalizację pliku chromedriver.exe kompaktybilnego z wersją chrome 
driver = webdriver.Chrome(executable_path=r"C:\WebDriver\bin\chromedriver.exe")

# wykonanie komendy "get", w tym wypadku analogicznie zadziałałoby requests.get()
# w ten sposób nawigujemy obiekt driver do strony wskazanej przez adres URL
driver.get('https://wroclaw.policja.gov.pl/dwr/form/159,Doba-w-liczbach.html?page=0')

# polecenie każe czekać do 10 sekund nim nie załaduje się nasz element, inaczej może wywalić błędem
wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.CLASS_NAME, "table-listing")))

# skoro już się załadowałem to możemy wyciągnąć dane z tabelki na pierwszej stronie
tabelka = driver.find_elements_by_class_name("table-listing")

# tabelka jest jednolitym tekstem wrzuconym do listy jednoelementowej
# rozdzielam tekst na wiersze gdzie separatorem jest znak nowej linii 
lines = tabelka[0].text.split('\n')


#przerzucam dane do fnalnego obiektu, pomijam pierwszy wiersz gdzie są nazwy kolumn
wynik = lines.copy()
kol_names = lines[0]

# następnie będę przechodził przez kolejne strony tabeli i powtarzał powyższy ciąg poleceń
# namierzam się na elementy listy stron tabeli (jest to obiekt typu AJAX - można pewni inaczej)
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

# mogę już rozłączyć się ze stroną, pobrałem co chciałem
driver.quit()

# następnie kilka kosmetycznych kroków: rozbicie kolumni "Poszukiwani" oddzielając nieletnich, wypełnienie NULLami

# definiuję tabelę 
import pandas as pd

#zainicjowanie obiektu DataFrame: nazwa kolumn oraz pierwszy element tabeli
df = pd.DataFrame( [[x for x in wynik[1].split(' ')]], 
                  columns = ['Data', 'Interwencje', 'Zatrzymani_na_goracym_uczynku','Poszukiwani', 'Wypadki_drogowe', 'Nietrzezwi_kierujacy'])

# zapakowanie pozostałych elementów 
for i in range(2,len(wynik)):
    df = df.append(pd.Series(wynik[i].split(' '), index=df.columns), ignore_index=True)

# wypełnienie wartości NULLowych zerami
df['Wypadki_drogowe'] = df['Wypadki_drogowe'].replace('-', '0')
df['Nietrzezwi_kierujacy'] = df['Nietrzezwi_kierujacy'].replace('-', '0')

# konwertuję typ danych na int
for kol in ['Wypadki_drogowe', 'Nietrzezwi_kierujacy', 'Interwencje', 'Zatrzymani_na_goracym_uczynku']:
    df[kol] = df[kol].astype(int)

# na koniec trzeba rozdzielić kolumnę poszukiwani na poszukiwani_total oraz poszukiwani_nieletni
tmp_df = pd.DataFrame(columns=['Poszukiwani_total', 'Poszukiwani_nieletni'])

for i in range(len(df['Poszukiwani'])):
    tmp = df['Poszukiwani'][i].split('(')
    tmp = [x.replace(')','') for x in tmp]
    # uzupełniam jeżeli nie było nieletnich poszukiwanych
    if len(tmp) < 2:
        tmp.append('0')
    tmp = [int(x) for x in tmp]
    tmp_df = tmp_df.append(pd.Series(tmp, index=tmp_df.columns), ignore_index=True)

# przenoszę kolumny z tabeli tymczasowej do docelowej
for kol in list(tmp_df.columns):
    df[kol] = tmp_df[kol]

# kasuję pierwotną kolumnę 
df.drop('Poszukiwani', axis=1, inplace=True) 

# df.head(10)