import requests

url = "https://affinitytrades-mt5.prod.b2copy.tech/b2copy.frontend.trades.v1.position.PositionService/List"

headers = {
    'Content-Type': 'application/grpc-web-text',  # This is specific to gRPC-Web
    'X-Grpc-Web': '1',  # This header is typically required by gRPC-Web
    'Accept': 'application/grpc-web-text',
    'Authorization': 'Bearer eyJhbGciOiJFUzI1NiIsImtpZCI6ImZ3ckhPNFdGbXBZdzhEdldhVUw4Ql9WY0R3MFk2ZWJleUpuY3c4aU5pemc9In0.eyJhY2NvdW50X2lkcyI6WzEwNzYyLDEwODQ0XSwiZXhwIjoxNzM2OTQ5MzA3LCJpYXQiOjE3MzY5NDg0MDcsImlzcyI6ImFmZmluaXR5dHJhZGVzLW10NSIsIm5iZiI6MTczNjk0ODQwNywic3ViIjoiYXV0aCJ9.3Cdrl1XT_XZT_yUeBMksQZlER_TZjKC5mb-99FjybmjvaqbsydaLS-zROEGm8Ld0U0l_Af5uctT92g_z1mg-7g'
}

data = b'AAAAABIKBgiKVBoBAxIECAMQARoCCGQ='
response = requests.post(url, headers=headers, data=data)

# Check if the request was successful
if response.status_code == 200:
    print("Response:", response.text)  # Print out the response (usually base64-encoded protobuf)
else:
    print("Error:", response.status_code, response.text)
