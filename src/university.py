import math
import pandas as pd


def fix_data_format():
    datadir = 'data/高校名单/'
    fname = datadir + '教育部全国普通高等学校名单(2017年6月).xls'
    savefile = datadir + 'university-list.csv'
    xf = pd.ExcelFile(fname)
    sheet = xf.sheet_names[0]
    df = xf.parse(sheet)

    data_list = []
    for i in range(3, len(df)):
        data = df.iloc[i]
        if type(data[0]) is not int:
            print(data[0])
            continue
        entry = [str(di) for di in data[1:-1]]
        entry.append('' if type(data[-1]) is not str and math.isnan(data[-1]) else data[-1])
        entry = [di.strip().replace('\n', '') for di in entry]
        data_list.append(entry)

    captions = [di for di in df.iloc[1][1:]]
    print('total:', len(data_list))
    print(captions)
    print(data_list[0])
    get_translates_data(savefile, captions, data_list)


def save_raw_data(savefile, captions, data_list):
    df2 = pd.DataFrame(data_list, columns=captions)
    df2.to_csv(savefile, index=False)


def get_translates_data(savefile, captions, data_list):
    import json
    import time
    from translate import get_translate_baidu, get_translate_youdao
    captions2 = captions + ['en-name(baidu)', 'en-name(youdao)']
    data_list2 = []

    current = 0
    ind = 0
    temp_savefile = 'data-%d.txt' % current
    fw = open(temp_savefile, 'w', encoding='utf-8')
    for entry in data_list:
        ind += 1
        if current > 0 and ind <= current: continue
        word = entry[0]
        en_name1 = ''
        en_name2 = ''
        try:
            en_name1 = get_translate_baidu(word).strip()
        except:
            pass
        try:
            en_name2 = get_translate_youdao(word).strip()
            if en_name2.endswith(','): en_name2 = en_name2[:-1]
        except:
            pass

        print('%d\t%s: %s; %s' % (ind, word, en_name1, en_name2))
        entry2 = entry + [en_name1, en_name2]
        # fw.write(','.join(entry2) + '\n')
        fw.write(json.dumps(entry2, ensure_ascii=False) + '\n')
        fw.flush()
        data_list2.append(entry2)

        # if ind % 500 == 0:
        #     time.sleep(5)

    # save result
    df2 = pd.DataFrame(data_list2, columns=captions2)
    df2.to_csv(savefile, index=False)


if __name__ == '__main__':
    fix_data_format()
