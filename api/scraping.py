import re
import iso4217parse
# from typing import Collection
from requests import Session
from bs4 import BeautifulSoup as bs


class ScrapingUnnax():
  URL_BASE_SCR = 'https://test.unnax.com'
  def __init__(self, username, password):
    self.username = username
    self.password = password

  def login_page(self):
    
    with Session() as s:
      url_login = "%s/login"% self.URL_BASE_SCR
      site = s.get(url_login)
      bs_content = bs(site.content, "html.parser")
      login_data = {'username': self.username, 'password': self.password}
      s.post(url_login,login_data)

    # Account page
    home_page = s.get("%s/account"%self.URL_BASE_SCR)
    soup = bs(home_page.content, 'lxml')
    erro_login = soup.find_all('span', class_="helper-text")
    if len(erro_login) > 0:    
      raise ValueError(erro_login[0].attrs['data-error'])
    return s

  def get_all_data(self, s):
    home_page = s.get("%s/account"%self.URL_BASE_SCR)
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
        statament_page = s.get(self.URL_BASE_SCR+'/'+child.find('a').attrs['href'])
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
        customer_page = s.get(self.URL_BASE_SCR+'/customer')
        soup_cust = bs(customer_page.content, 'lxml')
        collection = soup_cust.find_all("ul", class_ = "collection")      
        
        # Get Customer data 
        for ul in collection:
        
          list_li = ul.find_all('li')
          customer_data.append({
            'name' : list_li[0].string,
            'participation' : 'Titular',
            'doc' : self.username,
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