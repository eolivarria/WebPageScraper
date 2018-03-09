# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import csv
import re

url = 'https://etu.univ-lyon1.fr/activites/associations-etudiantes/liste-des-associations-etudiantes-744467.kjsp'
surl = 'https://etu.univ-lyon1.fr'
csv_name = 'univ-lyon1'

soup = BeautifulSoup(requests.get(url).content, 'html.parser')
content_body = soup.find('div', class_="ligne ligne_4").find_all('li')

def emailFmt( ce ):
   # change format from javascript

   ce = ce[ce.index('(') + 1:ce.index(')') - 1].replace('\'', '').split(',')

   return ce[0] + '@' + ce[len(ce) - 1] + ';'

with open(csv_name+'.csv', 'w') as csvfile:
    fieldnames = ['name', 'url', '_type', 'contact.country',
                  'contact.name', 'contact.email', 'contact.phone', 'contact.address',
                  'contact.website', 'social','description']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for div in content_body:
        for a in div.find_all('a', href=True):
            name = ''
            web_page = ''
            _type = 'Society'
            contact_country = 'FR'
            contact_name = ''
            contact_email = ''
            contact_phone = ''
            contact_address = ''
            contact_website = ''
            contact_social = ''
            description = ''

            name = a.get_text()
            if 'ngagement citoyen' not in name and 'Zup de co' not in name:
                web_page = a['href']
                print(name+': '+web_page)
                soup = BeautifulSoup(requests.get(web_page).content, 'html.parser')
                content_body = soup.find('main', id="page")
                count = 0
                dd = content_body.find_all('dd')
                for dt in content_body.find_all('dt'):
                    if 'Coordonn' in dt.get_text():
                        contact_address = dd[count].get_text()
                        contact_address = re.sub('\s+', ' ', contact_address).strip()
                        print('address: ' + contact_address)
                    elif 'Site web' in dt.get_text():
                        if 'facebook' in dd[count].get_text():
                            contact_social += dd[count].get_text()
                        else:
                            contact_website += dd[count].get_text() + ';'
                    elif 'M' in dt.get_text()[0]:
                        contact_email = re.sub('\s+', ' ', dd[count].get_text()).strip().replace(' [ at ] ', '@') + ';'
                    count += 1

                count = 0
                contenu = content_body.find_all('div', class_="motif__contenu")
                for titre in content_body.find_all('div', class_="motif__titre"):
                    titre = titre.get_text()
                    if 'Activit' in titre:
                        description = contenu[count].get_text()
                        description = re.sub('\s+', ' ', description).strip()

                        cs = contenu[count].find_all('a')
                        if cs:
                            for a in cs:
                                if '@' in a['href']:
                                    contact_email += a['href'].replace('http://', '') + ';'
                                elif 'javascript' in a['href']:
                                    contact_email += emailFmt(a['href'])
                                elif 'facebook' in a['href'] or 'twitter' in a['href']:
                                    contact_social += a['href'] + ';'
                                else:
                                    if a['href'] not in contact_website:
                                        contact_website += a['href'] + ';'

                            contact_social = contact_social[:len(contact_social)-1]
                            print('contact social: ' + contact_social)
                        else:
                            contact_social = ''
                    elif 'sidence' in titre:
                        contact = contenu[count]

                        if contact.find('a'):
                            if '@' not in contact.find('a').get_text():
                                contact_name = contact.find('a').get_text()


                                if 'javascript' in contenu[count].find('a')['href']:
                                    contact_email += emailFmt(contenu[count].find('a')['href'])
                                else:
                                    contact_email += contenu[count].find('a')['href'] +';'

                        elif len(contact.get_text()) > 1:
                            contact_name = contact.get_text()
                        else:
                            contact_email = ''

                        contact_phone = re.findall(
                            "(\d{2}[' '\.\s]??\d{2}[' '\.\s]??\d{2}[' '\.\s]??\d{2}[' '\.\s]??\d{2})",contact.get_text())
                        if contact_phone:
                            contact_phone = str(contact_phone[0])
                        else:
                            contact_phone = ''
                    count += 1

                if len(contact_email) > 0:
                    contact_email = contact_email[:len(contact_email) - 1]
                    print('contact email: ' + contact_email)
                else:
                    contact_email = ''

                if len(contact_name) > 0:
                    if ' et ' in contact_name:
                        contact_name = contact_name.replace(' et ',';')
                    if ':' in contact_name:
                        contact_name = contact_name[:contact_name.index(':')-len('Téléphone du président ')]
                    print('contact name: ' + contact_name)
                if len(contact_website) > 0:
                    contact_website = contact_website[:len(contact_website)-1]
                writer.writerow({
                    'name': name,
                    'url': web_page,
                    '_type': _type,
                    'contact.country': contact_country,
                    'contact.name': contact_name,
                    'contact.email': contact_email,
                    'contact.phone': contact_phone,
                    'contact.address': contact_address,
                    'contact.website': contact_website,
                    'social': contact_social,
                    'description': description})