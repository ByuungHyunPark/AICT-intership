from selenium import webdriver
import pandas as pd
import numpy as np
from tqdm.notebook import tqdm
import lxml.html
import requests
import time
from bs4 import BeautifulSoup
import re

etryDF = pd.DataFrame()
err_count = 10


#데이터 수집만을 위해 진행되므로 while 아닌, for문으로 진행
for pageNo in tqdm(range(1, 2483)):

    URLs = 'https://ksp.etri.re.kr/ksp/user/read?size=1&sort=korNm&direction=ASC&page={}'.format(pageNo)
    page_list = []

    driver.get(URLs);
    time.sleep(0.02)  #

    html = driver.page_source  # driver가 html을 가져오고
    soup = BeautifulSoup(html, 'html.parser')  # BeautifulSoup으로 parsing

    name = soup.select(
        'body > div.sub_wrap > div > div.sub_contents > div.researcher_view_wrap > div.researcher_info > div.r_name > strong')[
        0].text
    group = soup.select(
        'body > div.sub_wrap > div > div.sub_contents > div.researcher_view_wrap > div.researcher_info > div.basic_info > dl > dd')[
        0].text

    try:
        keywrd = [i.text for i in soup.select('#user-tag-cloud')[0].find_all('text')]
    except:
        try:
            keywrd = soup.select(
                'body > div.sub_wrap > div > div.sub_contents > div.researcher_view_wrap > div.researcher_info > div.basic_info > dl')[
                2].select('dd')[1].select('td')[0].text.strip().replace('\n\t\t\t\t\t\t\t\t\t\t\t', ', ')
        except:
            pass

    try:
        tel = soup.select(
            'body > div.sub_wrap > div > div.sub_contents > div.researcher_view_wrap > div.researcher_info > div.basic_info > dl > dd > span.icon-call-end')[
            0].text
    except:
        pass
    mail = soup.select(
        'body > div.sub_wrap > div > div.sub_contents > div.researcher_view_wrap > div.researcher_info > div.basic_info > dl > dd > span.icon-envelope-open')[
        0].text

    page_list.append([name, group, keywrd, tel, mail])
    snu_col_df = pd.DataFrame(page_list)

    etryDF = etryDF.append(snu_col_df, ignore_index=True)

    print(URLs + ' : Crawling 완료')

etryDF.columns = ['name', '부서', '전문분야 및 keywrd', '번호', 'email']
# etryDF['정보 출처'] = 'ETRI'


# save
etryDF.to_csv('ETRI_Crawling_real.csv', encoding='utf-8-sig')