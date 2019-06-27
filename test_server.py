import random,requests,json,string


def change_password(port):
    url = "http://elastic:changeme@34.239.98.76:{}/_xpack/security/user/elastic/_password".format(port)
    securePassword = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(8))
    passwordChange = {
        "password": securePassword
    }
    headers = {
        "Content-Type": "application/json"
    }
    result = requests.post(url,json.dumps(passwordChange), headers=headers)
    print(result.status_code,result.text)
    return securePassword

change_password(9201)