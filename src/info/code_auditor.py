import requests
import re
from html.parser import HTMLParser
# The URL to which you are sending the POST request

class TelegramHTMLParser(HTMLParser):
    """
    Custom HTMLParser that converts HTML to Telegram compatible HTML.
    """
    def __init__(self):
        super().__init__()
        self.result = ""
    
    def handle_starttag(self, tag, attrs):
        if tag.lower() == "h2":
            self.result += "<code>"
        elif tag.lower() == "p":
            self.result += ""
        # Other tags like <a> with href attribute can also be handled here
    
    def handle_endtag(self, tag):
        if tag.lower() == "h2":
            self.result += "</code>\n"
        elif tag.lower() == "p":
            self.result += ""
        # Close other tags as needed
    
    def handle_data(self, data):
        self.result += data
    
    def handle_entityref(self, name):
        self.result += f"&{name};"
    
    def handle_charref(self, name):
        self.result += f"&#{name};"
    
    def get_telegram_html(self):
        return self.result.strip()

def convert_html_to_telegram(html_string):
    # Create parser instance
    parser = TelegramHTMLParser()
    
    # Feed the HTML content
    parser.feed(html_string)
    
    # Get the result
    return parser.get_telegram_html()

def code_auditor(usercode):
    # print(usercode)
    data = {
        "userCode": usercode
    }
    headers = {
        'Content-Type': 'application/json'
    }
    url = 'https://api.encrypt.tools/codeaudit'

    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        res = response.json()
        html_string = res["response"]
        if "<body>" in html_string:
            pattern = r'<body>(.*?)</body>'

            # Find all matches using re.findall()
            matches = re.findall(pattern, html_string, re.DOTALL)
            text = matches[0]
        else:
            text = html_string
        telegram_html = convert_html_to_telegram(text)
        result_text = []
        if len(telegram_html) > 4000:
            para = telegram_html.split("<code>")
            for i in range(len(para)):
                mes = ""
                flag = True
                while flag:
                    if len(mes) + len(para[i]) + 6 < 4000:
                        mes += f'<code>{para[i]}'
                        if (i + 1) < len(para):
                            i += 1
                        else:
                            flag = False
                    else:
                        flag = False
                result_text.append(mes)
        else:
            result_text.append(telegram_html)
        return result_text
    else:
        return False