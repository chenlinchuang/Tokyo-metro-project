import googlemaps
from gmplot import gmplot
import time
import os
from selenium import webdriver
from platform import system
#current path
if system() == 'Windows':
    current_path = os.getcwd() + '\\'
else:
    current_path = os.getcwd() + '/'

def removetags(a):
    while '<' in a:
        left = int(a.index('<'))
        right = int(a.index('>'))
        a = a[0:left] +a[right+1:len(a)]
        try:
            a.index('>') == None
        except:
            break
    return a
def nearest_stations(start, google_key):
    gmaps = googlemaps.Client(key = google_key)
    start_latlon = gmaps.geocode(start)
    try:
        start_lat, start_lon = start_latlon[0]['geometry']['location']['lat'], start_latlon[0]['geometry']['location']['lng']
    except IndexError:
        return None, None
    if 35.2<start_lat<36.0 and 138.2<start_lon<140.5:
        loc = start_lat, start_lon
        n = 1
        counter = 0
        stands = []
        while counter == 0:
            radius = 1000*n
            radar_results = gmaps.places_nearby(location = loc, radius = radius, open_now = False,  type = 'subway_station',language = 'ja')
            if len(radar_results['results'])>0:
                for i in radar_results['results']:
                    stands.append(i['name'])
                counter += 1
            else:
                pass
            n += 1
        #print(radar_results)
        tot_direction = list()
        total = list()
        for stand in stands:
            time = 0
            dis=0
            end = stand
            instructions = []
            end_latlon = gmaps.geocode(end)
            end_lat, end_lon = end_latlon[0]['geometry']['location']['lat'], end_latlon[0]['geometry']['location']['lng']
            directions = gmaps.directions(start,end, mode = 'walking', language = 'zh-TW')
            #print(directions)
            for i in directions[0]['legs'][0]['steps']:
                temp = i['html_instructions']+'走'+i['distance']['text']+'約'+i['duration']['text']
                instructions.append(removetags(temp))
                time += int(i['duration']['text'][0])
                dis += float(i['distance']['text'][:-3])
            total.append((start,end,time))
            #print('from {} to {} about {} minutes {}'.format(start,end,time, dis))
            #print(instructions)
            tot_direction.append(instructions)
            min_time = float('inf')
            min_index = 0
            for i, j in enumerate(total):
                if j[2] <= min_time:
                    min_time = j[2]
                    min_index = i
        return total[min_index], tot_direction[min_index]
    else:
        return None,None

def station_to_end(station,end, google_key):
    gmaps = googlemaps.Client(key = google_key)
    all_instructions = []
    t = 0
    end_latlon = gmaps.geocode(end)
    end_lat, end_lon = end_latlon[0]['geometry']['location']['lat'], end_latlon[0]['geometry']['location']['lng']
    directions = gmaps.directions(station,end, mode = 'walking', language = 'zh-TW')
    instructions = []
    for i in directions[0]['legs'][0]['steps']:
        temp = i['html_instructions']+'走'+i['distance']['text']+'約'+i['duration']['text']
        instructions.append(removetags(temp))
        t += int(i['duration']['text'][0])
    title = 'from {} to {} about {} minutes'.format(station,end,t)
    all_instructions.extend(instructions)
    return all_instructions

def plot(start, end, google_key):
    gmaps = googlemaps.Client(key = google_key)
    start_latlon = gmaps.geocode(start)
    start_lat, start_lon = start_latlon[0]['geometry']['location']['lat'], start_latlon[0]['geometry']['location']['lng']
    end_latlon = gmaps.geocode(end)
    end_lat, end_lon = end_latlon[0]['geometry']['location']['lat'], end_latlon[0]['geometry']['location']['lng']


    directions = gmaps.directions(start,end, mode = 'walking')
    steps = []
    latlons = []
    steps.append(directions[0]['legs'][0]['steps'][0]['start_location'])
    for i in directions[0]['legs'][0]['steps']:
        steps.append(i['end_location'])
    for i in steps:
        temp = []
        temp.append(i['lat'])
        temp.append(i['lng'])
        latlons.append(tuple(temp))

    # latlon:list of lat,lon datas of passing points

    #   Plot map
    gmap = gmplot.GoogleMapPlotter(start_lat,start_lon, 15, apikey= google_key)
    top_attraction_lats, top_attraction_lons = zip(*latlons)
    gmap.plot(top_attraction_lats, top_attraction_lons, 'cornflowerblue', edge_width = 8)
    # Marker
    gmap.marker(start_lat, start_lon, 'green')
    gmap.marker(end_lat, end_lon, 'red')
    # Draw
    gmap.draw("test_map.html")

    file_name = 'file:///'+ os.getcwd() + '/test_map.html'
    driverpath=current_path +'geckodriver.exe'
    browser = webdriver.Firefox(executable_path = driverpath)
    browser.set_window_position(0,0)
    time.sleep(5)
    browser.get(file_name) 

if __name__ == '__main__':
    #print(nearest_stations('紐約'))
    #print(plot('浅草駅','淺草寺'))
    #print(os.getcwd())
    #print(station_to_end('淺草站', '淺草寺'))
    "print(gmaps.directions('羽田機場','西馬込駅', mode = 'walking', language = 'ja'))"