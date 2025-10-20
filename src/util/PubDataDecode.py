import base64
import json

def decode(data):
    decodedBytes = base64.b64decode(data["message"]['data'])
    decodedStr = decodedBytes.decode() 
    jsonData=json.loads(decodedStr)
    return jsonData