import re
import logging
import iso4217parse
import argparse
from typing import Collection
from requests import Session
from bs4 import BeautifulSoup as bs


def writeLoger(error_str):  
  logger.error(error_str)
  
def login_page():
  
  with Session() as s:
    site = s.get(url_login)
    bs_content = bs(site.content, "html.parser")
    login_data = vars(args)
    s.post(url_login,login_data)

  # Account page
  home_page = s.get("%s/account"%url_base)
  soup = bs(home_page.content, 'lxml')
  erro_login = soup.find_all('span', class_="helper-text")
  if len(erro_login) > 0:    
    raise Exception(erro_login[0].attrs['data-error'])
  return s

def get_all_data(s):
  home_page = s.get("%s/account"%url_base)
  soup = bs(home_page.content, 'lxml')
  accounts = 0
  accounts_data = []
  pattern_money = '(\\d*\\.?\\d*)' 
  
  collection = soup.find_all('ul', class_="collection")
  children = collection[0].contents
  # print(collection[0].contents)
  for child in children:
    if child.name:      
      accounts+=1      
      p_content = child.find('p')
      money = p_content.span.string.strip()      
      balance = re.findall(pattern_money, money)[1].strip()
      
      # Get Statament Page
      statament_page = s.get(url_base+'/'+child.find('a').attrs['href'])
      soup_sts = bs(statament_page.content, 'lxml')

      # Get data table      
      gdp_table = soup_sts.find("table", class_ = "striped")
      
      # Encabezado
      for th in gdp_table.thead.find_all('tr'):        
        headings = [x.string.replace('\n', ' ').strip() for x in th.find_all('th')]
      
      # Cuerpo de la tablaa
      table_data = []
      for tr in gdp_table.tbody.find_all("tr"): 
        t_row = {}        
        for td, th in zip(tr.find_all("td"), headings):
          th = th.lower()
          td_str = td.string.replace('\n', '').strip()
          if th == "amount" or th == "balance":
            td_str = re.findall(pattern_money, td_str)[1]
            # Search attr class res-text to negative value
            if td.attrs:
              if 'red-text' in td.attrs['class']:
                td_str = "-"+td_str
          t_row[th] = td_str
        table_data.append(t_row)

      # Customer Data
      customer_data =[]
      customer_page = s.get(url_base+'/customer')
      soup_cust = bs(customer_page.content, 'lxml')
      collection = soup_cust.find_all("ul", class_ = "collection")      
      
      # Get Customer data 
      for ul in collection:
      
        list_li = ul.find_all('li')
        customer_data.append({
          'name' : list_li[0].string,
          'participation' : 'Titular',
          'doc' : args.username,
          'address' : list_li[3].string,
          'emails' : list_li[2].string,
          'phones' : list_li[1].string,
        })

      # Add all information
      accounts_data.append(
        {
          'accounts_data':{
            'name': child.find('span').string.strip(),
            'number':p_content.contents[0].string.strip(),
            'currency': iso4217parse.parse(money)[0].name.strip(),
            'balance': balance
          },
          'customer_count': len(customer_data),
          'customer_data': customer_data,
          'statements_count': len(table_data),
          'statements_data': table_data,
        }
      )
  # print("Accounts (%i)" % len(accounts_data))
  return accounts_data

def print_console(data):
  print("Accounts ( %s )" % len(data))
  for res in data:
    print('\tAcount Data')
    print('\t\tName: %s'%res['accounts_data']['name'])
    print('\t\tNumber: %s'%res['accounts_data']['number'])
    print('\t\tCurrency: %s'%res['accounts_data']['currency'])
    print('\t\tBalance: %s'%res['accounts_data']['balance'])
    print('\tTotal Customers %s'%res['customer_count'])
    for customer in res['customer_data']:
      print('\t\tCustomer Data:')
      print('\t\t\tName: %s'%customer['name'])
      print('\t\t\tParticipation: %s'%customer['participation'])
      print('\t\t\tDoc: %s'%customer['doc'])
      print('\t\t\tAddress: %s'%customer['address'])
      print('\t\t\tEmails: %s'%customer['emails'])
      print('\t\t\tPhone: %s'%customer['phones'])
    print('\tStatements ( %s )'%res['statements_count'])
    print('\t\tDate\t\t|Amount\t|Balance|Concept')
    for state in res['statements_data']:
      print("\t\t%s\t|%s\t|%s\t|%s" % (state["date"], state["amount"], state["balance"], state["statement"]))

if __name__ == '__main__':
  
  logging.basicConfig(filename="scrapy.log", format='%(asctime)s %(message)s', filemode='w') 
  logger=logging.getLogger()
  logger.setLevel(logging.DEBUG)
  url_base = "https://test.unnax.com"
  url_login = "%s/login"% url_base
  
  parser = argparse.ArgumentParser(description='Process web scraping to test.unnax.com')
  parser.add_argument(
    '--username',
    type=str,
    help='username to loging page'
  )
  parser.add_argument(
    '--password',
    type=str,
    help='password to loging page'
  )

  args = parser.parse_args()

  try:
    session  = login_page()
    data_finaly = get_all_data(session)
    print_console(data_finaly)   

  except Exception as e:
    print(e)    
    writeLoger(e)