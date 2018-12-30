import json
import os
import requests
from urllib.parse import urlsplit


url = 'https://github.com/Ming-Zhang-XJTU/XJTU-Thesis-Template'
info = ['create', 'update', 'star', 'watch', 'fork', 'issue', 'contributor', 'commits', 'releases']
base_api = 'https://api.github.com/repos/'


def get_github_info(cate='zh'):
    basedir = 'data/latex-data/'
    src_file = basedir + 'templates-%s.json' % cate
    save_file = os.path.join(basedir, 'github-repo.json')
    save_file_404 = os.path.join(basedir, 'github-404.txt')
    if not os.path.exists(basedir):
        print('no dir: %s' % basedir)
        exit(-1)

    repo_name_list = []
    with open(src_file, encoding='utf-8') as f:
        for line in f:
            data = json.loads(line)
            res = data['resource']
            for k, links in res.items():
                for repo_name in links:
                    repo_name = urlsplit(repo_name).path
                    if repo_name.startswith('/'): repo_name = repo_name[1:]
                    repo_name_list.append(repo_name)

    repo_name_list = list(set(repo_name_list))
    print('links', len(repo_name_list))

    repo_name_got = []
    if os.path.exists(save_file):
        with open(save_file, encoding='utf-8') as f:
            for line in f:
                data = json.loads(line)
                repo_name = data['full_name']
                repo_name_got.append(repo_name)
                if 'old_full_name' in data:
                    repo_name_got.append(data['old_full_name'])
    print('got repos: %d' % len(repo_name_got))

    repo_404_list = []
    if os.path.exists(save_file_404):
        with open(save_file_404, encoding='utf-8') as f:
            for line in f:
                text = line.strip()
                if len(text) == 0: continue
                repo_404_list.append(text)
    print('404 repos: %d' % len(repo_404_list))

    fw_repo = open(save_file, 'a', encoding='utf-8')
    fw_404 = open(save_file_404, 'a', encoding='utf-8')
    for repo_name in repo_name_list:
        # 部分仓库被重命名了
        if repo_name in repo_name_got or repo_name in repo_404_list: continue

        url = base_api + repo_name
        response = requests.get(url)
        code = response.status_code

        if code == 200:
            print(url)
            response.encoding = 'utf-8'
            data = json.loads(response.text)
            name = data['full_name']
            if name != repo_name:
                data['old_full_name'] = repo_name
            fw_repo.write(json.dumps(data, ensure_ascii=False) + '\n')
            fw_repo.flush()
        elif code == 404:
            print(404, url)
            fw_404.write(repo_name + '\n')
            fw_404.flush()
            continue

        if code == 403:  # while : sleep
            print(403, url)
            break
            # time.sleep(60)
            # response = requests.get(url)
            # code = response.status_code

    fw_repo.close()
    fw_404.close()


if __name__ == '__main__':
    cate = 'zh'
    get_github_info(cate)
