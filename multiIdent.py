from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image
import pytesseract
import os, time


def task(img):
    image = Image.open(img)
    content = pytesseract.image_to_string(image, lang='chi_sim')  # 解析图片
    if '变 更 或 表 充 证 明 ' not in content:
        corp_name = content[content.find('作 权 人 '):][7:content[content.find('作 权 人 '):].find('\n')]
        if len(corp_name.replace(' ', '').replace('\n', '')) == 0:
            try:
                corp_name = str(content)[str(content).find('证 书 号'):].split('\n')[5] \
                    if str(content)[str(content).find('证 书 号'):].split('\n')[5] \
                    else str(content)[str(content).find('证 书 号'):].split('\n')[6]
            except Exception:
                pass
        if corp_name == '著 作 权 人 :':
            corp_name = str(content)[str(content).find('证 书 号'):].split('\n')[36]
        if len(corp_name.replace(' ', '')) == 0:
            try:
                corp_name = str(content).split('\n')[str(content).split('\n').index('VL.0') + 2]
            except Exception:
                try:
                    corp_name = str(content).split('\n')[str(content).split('\n').index('V1.0') + 2]
                except Exception:
                    pass
    else:
        corp_name = content[content.find('变 更 后 内 容 :'):][11:content[content.find('变 更 后 内 容 :'):].find('\n')]
        corp_name = corp_name.replace(' ', '')
    corp_name = corp_name.replace(' ', '')
    corp_name = corp_name.split('\n')[0]
    if len(corp_name) == 0:
        corp_name = 'UnKnow'
    corp_name = corp_name.replace(';', '_')
    corp_name = corp_name.replace(':', '_')
    corp_name = corp_name.replace(',', '_')
    corp_name = corp_name.replace('|', '')
    return str(img), str(os.path.abspath(os.path.join(path, corp_name + '.jpg')))


if __name__ == '__main__':
    max_workers = 10
    executor = ThreadPoolExecutor(max_workers=max_workers)
    path = r'C:\Users\成少阳\Desktop\新建文件夹\5-14'
    name_mapping = []
    for root, dirs, files in os.walk(path):
        for i in range(0, len(files) // max_workers + 1):
            tasks = []
            for file in files[i*max_workers: (i+1)*max_workers]:
                img = os.path.abspath(os.path.join(path, file))
                print('ident {}'.format(img))
                t = executor.submit(task, img)
                tasks.append(t)
            for res in as_completed(tasks):
                img_, new_img = res.result()
                print('get ident result for {}'.format(img_))
                name_mapping.append((img_, new_img))

    print('ident end.')
    time.sleep(3)
    print('start rename process ...')

    new_names = {}
    for name_map in name_mapping:
        if name_map[1] not in new_names.keys():
            new_name = name_map[1]
            new_names[name_map[1]] = 1
        else:
            new_name = name_map[1].split('.jpg')[0] + '_' + str(new_names[name_map[1]] + 1)
            # new_name = new_name.replace('.', '_')
            new_name += '.jpg'
            new_names[name_map[1]] += 1
        os.rename(name_map[0], new_name)
        print('renamed {} to {}'.format(name_map[0], new_name))