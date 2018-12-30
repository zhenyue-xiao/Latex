import json
from urllib import parse, request

# 中文翻译成英文
api_baidu = 'https://fanyi.baidu.com/transapi?from=zh&to=en&query='
# 语义类型：auto, zh, en, zht(繁体中文)

api_youdao = "http://fanyi.youdao.com/translate?&doctype=json&type=AUTO&i="
# type类型：ZH_CN2EN（中文->英文）

# google翻译
'''
# pip install googletrans
from googletrans import Translator
translator = Translator(service_urls=['translate.google.cn'])
dst_text = translator.translate(src_text,src='zh-cn',dest='en').text
'''


def get_response(base_url, word):
    url = base_url + parse.quote(word)
    response = request.urlopen(url)
    text = response.read()
    data = json.loads(text)
    return data


def get_translate_baidu(word):
    base_url = api_baidu
    result = get_response(base_url, word)
    dst = result['data'][0]['dst']
    return dst


def get_translate_youdao(word):
    base_url = api_youdao
    result = get_response(base_url, word)
    dst = result['translateResult'][0][0]['tgt']
    return dst
