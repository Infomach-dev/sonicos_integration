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
    return response

def commitChanges(sonicIP: str):
    url = f"https://{sonicIP}/api/sonicos/config/pending"
    payload = ""
    response = requests.request("POST", url, headers=headers, data=payload, verify=False)
    return response

def getCFSProfiles(sonicIP: str):
    url = f"https://{sonicIP}/api/sonicos/content-filter/profiles"

    response = requests.request("GET", url, headers=headers, verify=False)
    cfsProfilesList = response.json()
    cfsProfilesList = json.dumps(cfsProfilesList['content_filter'], indent=4)
    cfsProfilesList = json.loads(cfsProfilesList)

    # print(cfsProfilesList['profile'][0]['name'])
    return cfsProfilesList

def getCFSLists(sonicIP: str):
    url = f"https://{sonicIP}/api/sonicos/content-filter/uri-list-objects"
    payload = ""
    response = requests.request("GET", url, headers=headers, data=payload, verify=False)
    response = response.json()
    response = json.dumps(response['content_filter'], indent=4)
    response = json.loads(response)
    return response

def insertIntoCFS(sonicIP: str, cfsName: str, uri: str):
    url = f"https://{sonicIP}/api/sonicos/content-filter/uri-list-objects"
    payload = {"content_filter": {"uri_list_object": [
        {
            "name": cfsName,
                    "uri": [{"uri": uri}]
        }
    ]}}

    response = requests.request("PUT", url, json=payload, headers=headers, verify=False)
    response = response.json()
    response = json.dumps(response['status'], indent=4)
    response = json.loads(response)
    message = response['info'][0]['message']

    # translating the messages
    if (response['success'] == False):
         if (message == "Already exists."):
             translatedMessage = "Esse site já foi liberado!"
             return translatedMessage
         else: return message

    if (response['success'] == True):
        if (message == "Success."):
            translatedMessage = "Site liberado com sucesso!"
            return translatedMessage
        else: return message