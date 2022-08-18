import requests
import json
location = "New York City"
key = '5OTCFG7QiSwCNWkMe19O_SYi-N2AU9Ca06KNVg-9Not3PUma_UZsPxn7WeCVo4Jm5AUA5Ot3WTGFRdgYGR002ybvEMHun7vKPVkeLZlxswvmbJ1WWO9SGK71IE7SYnYx'

def get_businesses(location, api_key,categories):
    headers = {'Authorization': 'Bearer %s' % api_key}
    url = 'https://api.yelp.com/v3/businesses/search'

    data = []
    for offset in range(0, 1000, 50):
        params = {
            'limit': 50, 
            'location': location,
            'categories':categories,
            # 'location': location.replace(' ', '+'),
            'term': 'restaurants',
            'offset': offset
        }

        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data += response.json()['businesses']
        elif response.status_code == 400:
            print('400 Bad Request')
            break
        


    return data
resturtant=["indpak"]
with open("indpak.json", "w") as f_out:
    for item in resturtant:
        result = get_businesses(location,key,item)
        counter = 0
        for i in result:
            counter+=1
            jsonString = json.dumps(i)
            f_out.write(jsonString)
            f_out.write("\n")
        print(item,counter)