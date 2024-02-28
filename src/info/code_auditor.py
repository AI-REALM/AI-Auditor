import requests
import re
# The URL to which you are sending the POST request

def code_auditor(usercode):
    data = {
        "userCode": usercode
    }
    headers = {
        'Content-Type': 'application/json'
    }
    url = 'https://api.encrypt.tools/codeaudit'

    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        html_string = response.text
        if "<body>" in html_string:
            pattern = r'<body>(.*?)</body>'

            # Find all matches using re.findall()
            matches = re.findall(pattern, html_string, re.DOTALL)
            print(html_string)
            text = matches[0]
        else:
            text = html_string
        text = text.replace("h2", "code")
        print('Success:', text)
        return text
    else:
        return False