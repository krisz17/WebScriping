# potrzebne biblioteki 
import requests
from bs4 import BeautifulSoup

#adres do strony 
URL = "https://www.interviewbit.com/python-interview-questions/"
page = requests.get(URL)

# parsuję wynik do zjadliwej formy
soup = BeautifulSoup(page.content, "html.parser")

# przejdę po wszystkich grupach pytań/odpowiedzi i przenoszę je do dwóch osobnych list
levels = ["freshers", "experienced", "python-oops", "python-pandas", 
          "python-numpy", "python-libraries","python-programs"]

answers = []
questions = []

for lev in levels:
    results = soup.find(id=lev)
    if results is None:
        continue
    # kazde pytanie/odpowiedź znajduje się w tagu 'section'
    query_elements = results.find_all("section")
    if query_elements is None:
        continue
    outp = ""
    for query_element in query_elements:
        for tag in query_element.find_all('h3'):
            if tag is None:
                continue
            outp = outp + tag.text.rstrip()
            outp = outp + " "
        questions.append(outp.rstrip())
        outp =""
        for tag in query_element.find_all('p'):
            if tag is None:
                continue
            outp = outp + str(tag.text.rstrip())
            outp = outp + " "
        answers.append(outp.rstrip())
        outp =""

for qq in questions:
    print(qq)