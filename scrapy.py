from bs4 import BeautifulSoup
import requests


def scrap():

    url = "https://haveibeenpwned.com/"
    # Get data from URL
    page = requests.get(url)

    bs = BeautifulSoup(page.text, 'html.parser')
    bs

    pwns = bs.findAll('a', {'data-target':'#pwnedCompanyOverview'})
    count = bs.findAll('span', {'class':'pwnCount'})

    companiez = {}

    for pwn in pwns:
        companiez[pwn.find('i', 'pwnCompanyName').contents[0]] = pwn.find('span', {'class':'pwnCount'}).contents[0]


    return companiez
