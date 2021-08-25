import json
import base64
import requests
from collections import OrderedDict

headers = OrderedDict(
        [('Accept', 'application/json'),
            ('Content-Type', 'application/json'),
            ('Accept-Encoding', 'application/json'),
            ('charset', 'UTF-8')
         ])

def login(fwAddress: str, fwUser: str, fwPassword: str):
    # make credentials base64 encoded
    credentials = fwUser+":"+fwPassword
    credentials = bytes(credentials, 'utf-8')
    encode = base64.b64encode(credentials)
    encode = str(encode, 'utf-8')

    url = f"https://{fwAddress}/api/sonicos/auth"
    payload = ""
    headers = OrderedDict(
        [('Authorization', f'Basic {encode}'),
            ('Accept', 'application/json'),
            ('Content-Type', 'application/json'),
            ('Accept-Encoding', 'application/json'),
            ('charset', 'UTF-8')
         ])

    response = requests.request("POST", url, data=payload, headers=headers, verify=False)

    return response

def logout(fwAddress: str):
    url = f"https://{fwAddress}/api/sonicos/auth"
    payload = ""

    response = requests.request("DELETE", url, data=payload, headers=headers, verify=False)

    return response

def configMode(fwAddress: str):
    url = f"https://{fwAddress}/api/sonicos/config-mode"
    payload = ""
    response = requests.request("POST", url, headers=headers, data=payload, verify=False)

    return response

def commitChanges(fwAddress: str):
    url = f"https://{fwAddress}/api/sonicos/config/pending"
    payload = ""
    response = requests.request("POST", url, headers=headers, data=payload, verify=False)
    
    return response

def getCFSProfiles(fwAddress: str):
    url = f"https://{fwAddress}/api/sonicos/content-filter/profiles"

    response = requests.request("GET", url, headers=headers, verify=False)
    cfsProfilesList = response.json()
    cfsProfilesList = json.dumps(cfsProfilesList['content_filter'], indent=4)
    cfsProfilesList = json.loads(cfsProfilesList)

    # print(cfsProfilesList['profile'][0]['name'])
    if response.status_code == 200:
        return cfsProfilesList
    else: 
        return response

def getCFSLists(fwAddress: str):
    url = f"https://{fwAddress}/api/sonicos/content-filter/uri-list-objects"
    payload = ""
    response = requests.request("GET", url, headers=headers, data=payload, verify=False)
    if response.status_code == 200:
        cfsLists = response.json()
        cfsLists = json.dumps(cfsLists['content_filter'], indent=4)
        cfsLists = json.loads(cfsLists)
        return cfsLists
    else: 
        return response

def getSpecificCFSList(fwAddress: str, cfsListName: str):
    url = f"https://{fwAddress}/api/sonicos/content-filter/uri-list-objects/name/{cfsListName}"
    payload = ""
    response = requests.request("GET", url, headers=headers, data=payload, verify=False)
    if response.status_code == 200:
        cfsLists = response.json()
        cfsLists = json.dumps(cfsLists['content_filter'], indent=4)
        cfsLists = json.loads(cfsLists)
        return cfsLists
    else:
        return response

def insertIntoCFS(fwAddress: str, cfsName: str, uri: str):
    url = f"https://{fwAddress}/api/sonicos/content-filter/uri-list-objects"
    payload = {"content_filter": {"uri_list_object": [
        {
            "name": cfsName,
                    "uri": [{"uri": uri}]
        }
    ]}}

    response = requests.request("PUT", url, json=payload, headers=headers, verify=False)

    return response

def removeFromCFS(fwAddress: str, cfsName: str, uri: str):
    url = f"https://{fwAddress}/api/sonicos/content-filter/uri-list-objects"

    payload = {"content_filter": {"uri_list_object": [
                {
                    "name": cfsName,
                    "uri": [{"uri": uri}]
                }
            ]}}

    response = requests.request("DELETE", url, json=payload, headers=headers, verify=False)

    return response