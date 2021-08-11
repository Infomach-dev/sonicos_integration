import json
import requests
from collections import OrderedDict

from requests.api import head

headers = OrderedDict(
        [('Accept', 'application/json'),
            ('Content-Type', 'application/json'),
            ('Accept-Encoding', 'application/json'),
            ('charset', 'UTF-8')
         ])

def login(sonicIP: str):
    url = f"https://{sonicIP}/api/sonicos/auth"
    payload = ""
    headers = OrderedDict(
        [('Authorization', 'Basic YWRtaW46cGFzc3dvcmQ='),
            ('Accept', 'application/json'),
            ('Content-Type', 'application/json'),
            ('Accept-Encoding', 'application/json'),
            ('charset', 'UTF-8')
         ])

    response = requests.request("POST", url, data=payload, headers=headers, verify=False)

    return response.status_code

def logout(sonicIP: str):
    url = f"https://{sonicIP}/api/sonicos/auth"
    payload = ""

    response = requests.request("DELETE", url, data=payload, headers=headers, verify=False)

    return response.status_code

def configMode(sonicIP: str):
    url = f"https://{sonicIP}/api/sonicos/config-mode"
    payload = ""
    response = requests.request("POST", url, headers=headers, data=payload, verify=False)

    return response.status_code

def commitChanges(sonicIP: str):
    url = f"https://{sonicIP}/api/sonicos/config/pending"
    payload = ""
    response = requests.request("POST", url, headers=headers, data=payload, verify=False)
    
    return response.status_code

def getCFSProfiles(sonicIP: str):
    url = f"https://{sonicIP}/api/sonicos/content-filter/profiles"

    response = requests.request("GET", url, headers=headers, verify=False)
    cfsProfilesList = response.json()
    cfsProfilesList = json.dumps(cfsProfilesList['content_filter'], indent=4)
    cfsProfilesList = json.loads(cfsProfilesList)

    # print(cfsProfilesList['profile'][0]['name'])
    if response.status_code == 200:
        return cfsProfilesList
    else: 
        return response.status_code

def getCFSLists(sonicIP: str):
    url = f"https://{sonicIP}/api/sonicos/content-filter/uri-list-objects"
    payload = ""
    response = requests.request("GET", url, headers=headers, data=payload, verify=False)
    if response.status_code == 200:
        cfsLists = response.json()
        cfsLists = json.dumps(cfsLists['content_filter'], indent=4)
        cfsLists = json.loads(cfsLists)
        return cfsLists
    else: 
        return response.status_code

def insertIntoCFS(sonicIP: str, cfsName: str, uri: str):
    url = f"https://{sonicIP}/api/sonicos/content-filter/uri-list-objects"
    payload = {"content_filter": {"uri_list_object": [
        {
            "name": cfsName,
                    "uri": [{"uri": uri}]
        }
    ]}}

    response = requests.request("PUT", url, json=payload, headers=headers, verify=False)

    return response.status_code