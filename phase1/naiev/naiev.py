import requests
from bs4 import BeautifulSoup
import time 

# function to match the target with the text of the html
def find_tgt(tgt, content):
  content = content.get_text()
  # content = content.strip(' ')
  if tgt in content:
    return True
    # return 'Tgt found'
  return False
  # return 'Tgt not found'

def get_sublink(soup,src):
  sub = soup.find_all('a')
  links = []
  for link in sub :
    sub_link = link.get('href')
    if sub_link is not None and sub_link.startswith('http'):
      if sub_link not in links and sub_link != src and sub_link != src +'/':
        links.append(sub_link)
  return links

def driver(src, visisted, target , sub_links):
  for sub_link in sub_links:
    if sub_link not in visisted:
      visisted.append(sub_link)
      visisted.append(sub_link +'/')
      response = requests.get(sub_link)
      html_content = response.content
      soup = BeautifulSoup(html_content, 'html.parser')
      if find_tgt(target, soup):
        print('\nTgt found at ', sub_link, ' and the depth is ', len(visisted))
        return True
      else:
        print('.',end=' ')
        sub_links = get_sublink(soup, src)
        found = driver(src, visisted, target , sub_links)
        if found :
          return True
        else :
          return False

#def main():
src = 'https://www.cs.ku.edu.kw'
target ='Abeer Alsafran, Abdulwahab Alobaid'
visited = []
stime = time.time()
# make first get request
response = requests.get(src)
# Add src to visited array
visited.append(src)
visited.append(src+'/')

# Get the content
html_content = response.content
# Soup is the whole content
soup = BeautifulSoup(html_content, 'html.parser')
# Find the target
if find_tgt(target, soup):
  print('Tgt found')
else:
  print('Searching', end=' ')
  sub_links = get_sublink(soup, src)
  driver(src, visited, target , sub_links)
etime = time.time()

totaltime = etime - stime
print(f"Total time: {totaltime} sec")


'''
if __name__ == "__main__":
    main()
'''


