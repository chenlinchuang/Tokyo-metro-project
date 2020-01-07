import requests
from bs4 import BeautifulSoup
#get station link and station name on wikipedia
#line: A I S E G M H T C Y Z N F Mb

URL_list = ['https://zh.wikipedia.org/wiki/%E6%B7%BA%E8%8D%89%E7%B7%9A',
            'https://zh.wikipedia.org/wiki/%E4%B8%89%E7%94%B0%E7%B7%9A_(%E9%83%BD%E7%87%9F%E5%9C%B0%E4%B8%8B%E9%90%B5)',
            'https://zh.wikipedia.org/wiki/%E6%96%B0%E5%AE%BF%E7%B7%9A_(%E9%83%BD%E7%87%9F%E5%9C%B0%E4%B8%8B%E9%90%B5)',
            'https://zh.wikipedia.org/wiki/%E5%A4%A7%E6%B1%9F%E6%88%B6%E7%B7%9A',
            'https://zh.wikipedia.org/wiki/%E9%8A%80%E5%BA%A7%E7%B7%9A',
            'https://zh.wikipedia.org/wiki/%E4%B8%B8%E4%B9%8B%E5%85%A7%E7%B7%9A',
            'https://zh.wikipedia.org/wiki/%E6%97%A5%E6%AF%94%E8%B0%B7%E7%B7%9A',
            'https://zh.wikipedia.org/wiki/%E6%9D%B1%E8%A5%BF%E7%B7%9A_(%E6%9D%B1%E4%BA%AC%E5%9C%B0%E4%B8%8B%E9%90%B5)',
            'https://zh.wikipedia.org/wiki/%E5%8D%83%E4%BB%A3%E7%94%B0%E7%B7%9A',
            'https://zh.wikipedia.org/wiki/%E6%9C%89%E6%A8%82%E7%94%BA%E7%B7%9A',
            'https://zh.wikipedia.org/wiki/%E5%8D%8A%E8%97%8F%E9%96%80%E7%B7%9A',
            'https://zh.wikipedia.org/wiki/%E5%8D%97%E5%8C%97%E7%B7%9A_(%E6%9D%B1%E4%BA%AC%E5%9C%B0%E4%B8%8B%E9%90%B5)',
            'https://zh.wikipedia.org/wiki/%E5%89%AF%E9%83%BD%E5%BF%83%E7%B7%9A'
            ]
def cut_string(s):
    if s == None:
        raise AttributeError
    if '-' in s:
        ind = s.index('-')
        result = s[:ind] + s[ind+1:]
    elif '（' in s:
        ind = s.index('（')
        result = s[:ind] + '駅'
    elif '〈' in s:
        ind = s.index('〈')
        result = s[:ind] + '駅'
    else:
        result = s + '駅'
    return result
link_dict = dict()
fin = open('station_link.txt','w', encoding='utf8')
for i in range(len(URL_list)):
    res = requests.get(URL_list[i]).text
    soup = BeautifulSoup(res,'lxml')
    for items in soup.find('table', class_='wikitable').find_all('tr')[1::]:
        #print(len(items))
        if len(items) <=8:
            continue
        data = items.find_all(['td','th'])
        #print(data[1].find('a'))
        try:
            fin.write(cut_string(data[0].text.strip()) + ','+ 'https://zh.wikipedia.org'+data[1].find('a').get('href')+',' +cut_string(data[2].find('span').text.strip())+'\n' )

        except AttributeError:
            try:
                fin.write(cut_string(data[0].text.strip()) +',' + 'https://zh.wikipedia.org'+data[2].find('a').get('href')+',' + cut_string(data[3].find('span').text.strip())+'\n')

            except AttributeError:
                print(data[0].text.strip())
                fin.write(cut_string(data[0].text.strip()) + ',' + 'None' + ',' + 'None\n')
fin.close()
        #print(len(link_dict))
        #print(data[2].text.strip())
        #print(data[1])
        #print(data[1].get('href'))
        #print(data[3:-1])

#print(soup.find('table', class_='wikitable').find_all('tr')[1::][0])
#print(link_dict['M'])