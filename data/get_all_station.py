import os
def all_station():
    data = dict()
    station_dict = dict()
    
    with open(os.getcwd() +'\\my_lines.csv','r') as fin:
        for line in fin:
            line.strip()
            temp = line.split(';')
            data[temp[0]] = [float(x) for x in temp[3:]]
            station_nodes=list()
            station_dict[temp[0]] = list()
            for i in range(int(temp[1]),int(temp[2])+1):
                station_nodes.append('%s%02d' % (temp[0], i))
            station_dict[temp[0]].extend(station_nodes)
    return station_dict
def station_ravel():
    station = list()
    with open(os.getcwd() +'\\my_lines.csv','r') as fin:
        for line in fin:
            line.strip()
            temp = line.split(';')
            for i in range(int(temp[1]),int(temp[2])+1):
                station.append('%s%02d' % (temp[0], i))
    return station
import requests

def check_internet():
    url='http://www.google.com/'
    timeout=5
    try:
        _ = requests.get(url, timeout=timeout)
        return True
    except requests.ConnectionError:
        print("No Internet")
    return False

if __name__=='__main__':
    print(check_internet())
    print(len(station_ravel()))
