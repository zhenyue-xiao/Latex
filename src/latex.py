import json
import os
import re
import requests
from urllib import request, parse
from bs4 import BeautifulSoup
from bs4.element import Tag
from pypinyin import lazy_pinyin


def get_tex_resource():
    """
    ## latex模板网站
    url_website = 'http://www.latexstudio.net/archives/category/latex-templates/'
    url_internal = 'internal-university-tex-template'
    url_foreign = 'foreign-university-tex-template'

    # JSON数据
    方法：浏览器打开网址http://www.latexstudio.net/archives/category/latex-templates
    Firefox/Chrome F12进入调试/开发模式：选择网络（Network）->XHR （可以Ctrl+R重新加载）
    选择加载的资源（拖动滚动条，选择非第一条的资源），右键复制网址/link address
    * 国内（中国内地）高校：http://www.latexstudio.net/home/more?&type=catid|10&page=0
    * 国外高校：http://www.latexstudio.net/home/more?&type=catid|11&page=0
    * 全部模板：http://www.latexstudio.net/home/more?&type=catid|5&page=0
    """

    # JSON数据返回 （国内高校）
    baseurl = 'http://www.latexstudio.net/home/more?&type=catid|%d&page=%d'
    savedir = 'data/latex-data/'
    max_count = 20
    url_cate = {'zh': 10, 'wg': 11}

    for key, value in url_cate.items():
        sub_savedir = os.path.join(savedir, key)
        if not os.path.exists(sub_savedir): os.makedirs(sub_savedir)
        result_file = os.path.join(sub_savedir, ('all-list-of-%s.txt' % key))
        f = open(result_file, 'w', encoding='utf-8')
        for i in range(max_count):
            url = baseurl % (value, i)
            print(key, url)

            response = request.urlopen(url)
            text = response.read()
            data = json.loads(text)

            entry_list = data['result']['list']
            if len(entry_list) == 0: break

            json_file = os.path.join(sub_savedir, ('%d.json' % i))
            with open(json_file, 'w', encoding='utf-8') as fw:
                fw.write(json.dumps(data, ensure_ascii=False))

            for entry in entry_list:
                postname = entry['post_name'].strip()
                if len(postname) > 0 and postname.find('%') >= 0:
                    postname = parse.unquote(postname)
                pageurl = entry['url_show'].strip()
                links = _get_link_list(pageurl)

                d = {}
                d['title'] = entry['title'].strip()
                d['postname'] = postname
                d['date'] = entry['inputtime'].strip()
                d['url'] = pageurl
                d['source'] = entry['source'].strip()
                d['text'] = entry['hometext'].strip()
                d['links'] = links
                f.write(json.dumps(d, ensure_ascii=False) + '\n')


def _get_link_list(url):
    # print('\t'+url)
    response = requests.get(url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, "html.parser")
    body = soup.find(id="artibody")
    # hrefs = body.find_all('a')
    downs = body.select('h2')  # <h2>下载区</h2>
    down = None
    for d in downs:
        if d.text.find('下载区') >= 0:
            down = d
            break

    if down is None:
        hrefs = body.find_all('a')
    else:
        hrefs = down.find_next_siblings('a')
        if hrefs is None or len(hrefs) == 0:
            hrefs2 = []
            tags = down.find_next_siblings()
            for tag in tags:
                if type(tag) is not Tag: continue
                if tag.name == 'a':
                    hrefs2.append(tag)
                else:
                    hrefs2.extend(tag.find_all('a'))
            hrefs = hrefs2
    images_postfix = ['png', 'gif', 'jpg', 'jpeg']
    link_list = []
    for href in hrefs:
        if not href.has_attr('href'): continue
        link = href.get('href').strip()
        if link.lower().endswith('.png'): continue
        link_list.append(link)
    return link_list


def sort_link_github(cate='zh'):
    basedir = 'data/latex-data/'
    src_file = basedir + ('%s/all-list-of-%s.txt' % (cate, cate))
    savefile = basedir + 'templates-%s.json' % cate
    university_dict = {}

    with open(src_file, encoding='utf-8') as f:
        for line in f:
            data = json.loads(line)
            title = data['title']
            name = _get_name(title)
            if name == '': continue

            links = data['links']
            lks = set()
            for link in links:
                gh_link = _get_github_repo(link)
                if len(gh_link) > 0:
                    lks.add(gh_link)
            lks = list(lks)
            if len(lks) == 0: continue

            if name not in university_dict:
                university_dict[name] = {}

            template_dict = university_dict[name]
            if name in template_dict:
                template_dict[title].extend(lks)
            else:
                template_dict[title] = lks

    university_list = sorted(university_dict.items(), key=lambda item: lazy_pinyin(item[0]))
    with open(savefile, 'w', encoding='utf-8') as fw:
        for key, value in university_list:
            entry = {'name': key, 'resource': value}
            fw.write(json.dumps(entry, ensure_ascii=False) + '\n')


def _get_name(text, pattern=r'\S+(?:大学|学院|分校)'):
    results = re.findall(pattern, text.strip())
    if len(results) == 0:
        return ''
    name = results[0]

    # 异常
    # 2017年xx大学
    name = re.sub('\d+年?', '', name)

    # 嗨！thesis！哈尔滨工业大学毕业论文LaTeX模板
    bads = ['！', '用于', '的']
    for b in bads:
        if name.find(b) >= 0: name = name[name.rfind(b) + len(b):]

    # xx大学xx学院
    if re.match(r'\S+大学\S+学院', text):
        name = name[:name.rfind('大学') + 2]

    return name


def _get_github_repo(url_link, domain='github.com'):
    from urllib.parse import urlsplit, urljoin
    repo_link = ''
    parts = urlsplit(url_link)

    netloc = parts.netloc
    if netloc.find(domain) < 0: return repo_link
    path = parts.path
    if path.startswith('/'): path = path[1:]
    pparts = path.split('/')
    if len(pparts) < 2: return repo_link
    user = pparts[0]
    repo = pparts[1]
    if repo.endswith('.git'): repo = repo[:repo.find('.git')]
    base = 'https://' + domain
    repo_link = urljoin(base, '/'.join([user, repo]))
    return repo_link


if __name__ == '__main__':
    get_tex_resource()
    for cate in ['zh', 'wg']:
        sort_link_github(cate)
