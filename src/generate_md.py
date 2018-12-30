import json
import os
import re
from urllib.parse import urlsplit

from pypinyin import lazy_pinyin

from github import get_data

"""
owner = github_infos['owner']['login']
repo_name = github_infos['name']
full_name = github_infos['full_name']
desp = github_infos['description']
url = github_infos['html_url']
create = github_infos['created_at']
update = github_infos['pushed_at']
stars = github_infos['stargazers_count']
watchers:['watchers_count']
forks:['forks_count']
"""


def gen_md(cate='zh'):
    basedir = 'data/latex-data/'
    src_file = basedir + 'templates-%s.json' % cate
    repo_file = os.path.join(basedir, 'github-repo.json')
    save_file = os.path.join(basedir, 'latex-templates-repo-%s.md' % cate)

    repo_list = {}
    university_dict = {}
    with open(src_file, encoding='utf-8') as f:
        for line in f:
            data = json.loads(line)
            repo_names = set()
            for desp, urls in data['resource'].items():
                for url in urls:
                    repo_name = urlsplit(url).path
                    if repo_name.startswith('/'): repo_name = repo_name[1:]
                    repo_list[repo_name] = desp
                    repo_names.add(repo_name)
            university_dict[data['name']] = repo_names

    github_repos_info = {}
    with open(repo_file, encoding='utf-8') as f:
        for line in f:
            data = json.loads(line)
            repo_name = data['full_name']
            desp = '' if repo_name not in repo_list else repo_list[repo_name]
            repo = _get_info(data, desp)
            github_repos_info[repo_name] = repo
            if 'old_full_name' in data:
                github_repos_info[data['old_full_name']] = repo

    with open(save_file, 'w', encoding='utf-8') as fw:
        fw.write('## %s高校LaTeX论文模板\n\n' % ('中国' if cate == 'zh' else '其他地区'))
        uni_names = list(university_dict.keys())
        uni_names.sort(key=lambda w: lazy_pinyin(w))
        for uni_name in uni_names:
            repo_names = university_dict[uni_name]
            repo_infos = []
            for repo_name in repo_names:
                if repo_name in github_repos_info:
                    repo_infos.append(github_repos_info[repo_name])

            if len(repo_infos) == 0: continue

            repo_infos.sort(key=lambda entry: entry['star'], reverse=True)
            fw.write('* %s\n' % uni_name)
            for repo in repo_infos:
                info = repo['info']
                fw.write('  * ' + info + '\n')
            fw.write('\n')


def _get_info(github_infos, title):
    owner = github_infos['owner']['login']
    repo_name = github_infos['name']
    full_name = github_infos['full_name']
    desp = github_infos['description']
    if desp is None or len(desp.strip()) == 0:
        desp = title
    desp = desp.replace('#', ' ')
    re.sub('\s+', ' ', desp)
    desp = desp.strip()

    url = github_infos['html_url']
    create = github_infos['created_at']
    create = create[:create.rfind('T')]
    update = github_infos['pushed_at']
    update = update[:update.rfind('T')]

    stars = github_infos['stargazers_count']
    watchers = github_infos['watchers_count']
    forks = github_infos['forks_count']
    info = '[%s](%s) (star=%d, watch=%d, fork=%d) - `%s`, (%s~%s).' % (
        full_name, url, stars, watchers, forks, desp, create, update)

    repo = {'star': stars, 'count': stars + forks + watchers, 'info': info}
    return repo


def update(fname):
    fw = open('temp.txt', 'w', encoding='utf-8')
    with open(fname, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if len(line) == 0 or not line.startswith('http'): continue
            path = urlsplit(line).path
            code, text = get_data(path)
            if code == 200:
                data = json.loads(text)
                repo = _get_info(data, '')
                info = repo['info']

                print(info)
                fw.write("  * " + info + '\n')
                fw.flush()
    fw.close()


if __name__ == '__main__':
    # for cate in ['zh', 'wg']:
    #     gen_md(cate)
    update('repos.txt')
