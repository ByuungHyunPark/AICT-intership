import pandas as pd
import re
import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'}


def crawliing():
    id_ = 0  # 기사별 고유id
    articleInfo = []  # dataframe 만들기 위한 List
    errCount = 0  # 에러 수 체크

    # 100회연속으로 error URL이 나타나면 종료 => 모든 데이터 받아온 상황
    while (errCount <= 100):

        url = 'https://www.reportrash.com/?content=news/detail&id={}'.format(id_)
        print(url, ' : ', errCount)
        req = requests.get(url, headers=headers)
        html = req.text
        soup = BeautifulSoup(html, 'html.parser')

        if soup.select('body')[0].text.strip() == '에러입니다.':
            errCount += 1
            id_ += 1
            continue

        errCount = 0  # 에러발생 안하면 , 카운트 초기화
        soup.select('#reporter-span')[0].text

        # 기사 정보
        title = soup.select('#title-span')[0].text  # 기사제목
        title = title.strip()

        # 기사 제목에 불필요한 미디어 이름 포함 된 경우 존재하는데 , 네이버뉴스에 merge P.K값으로 사용하기 위해 제거
        if ' | 연합뉴스' in title:
            title = title[:-len(' | 연합뉴스')]

        elif ' - 세계일보' in title:
            title = title[:-len(' - 세계일보')]

        elif ' - 머니투데이' in title:
            if ' - 머니투데이 뉴스' in title:
                title = title[:-len(' - 머니투데이 뉴스')]
            else:
                title = title[:-len(' - 머니투데이')]

        elif ' - 매일경제' in title:
            title = title[:-len(' - 매일경제')]

        media = soup.select('#media-span')[0].text  # 언론사
        reporter = soup.select('#reporter-span')[0].text  # 기자
        date = soup.select('#date-span')[0].text
        reportCnt = soup.select('#report-span')[0].text  # 제보 횟수
        articleUrl = soup.select('#news-link-a')[0]['href']  # 기사 url

        try:
            tag = soup.findAll("span", {'id': 'news-tags-span'})[0].text[1:].strip().split('\xa0\xa0#')
        except:
            tag = ''

        # 기사평가 데이터
        articleEvaluates = soup.find(class_='table table-mobile-view').text.strip().split('\n')

        가짜뉴스cnt = articleEvaluates[0].split(' : ')[1]
        악의적헤드cnt = articleEvaluates[1].split(' : ')[1]
        사실왜곡cnt = articleEvaluates[2].split(' : ')[1]
        통계왜곡cnt = articleEvaluates[3].split(' : ')[1]
        잘못된인용cnt = articleEvaluates[4].split(' : ')[1]
        오보cnt = articleEvaluates[5].split(' : ')[1]
        헛소리선동cnt = articleEvaluates[6].split(' : ')[1]
        기타cnt = articleEvaluates[7].split(' : ')[1]

        articleInfo.append([id_, title, media, reporter, date, reportCnt, articleUrl, tag,
                            가짜뉴스cnt, 악의적헤드cnt, 사실왜곡cnt, 통계왜곡cnt,
                            잘못된인용cnt, 오보cnt, 헛소리선동cnt, 기타cnt])

        id_ += 1  # 다음기사 탐색

    return pd.DataFrame(articleInfo)


#날짜데이터 정제
def refineDate(text):
    pattern = "(^[0-9]{4})년 ([0-9]{1,2})월 ([0-9]{1,2})일"

    try:
        y, m, d = map(int, re.findall(pattern, text)[0])
        return f'{y:04d}-{m:02d}-{d:02d}'
    except: #날짜 데이터가 결측치인 경우 예외처리
        return None


def clear_headline(text):
    special_symbol = re.compile('[\{\}\[\]\/?,;:|\)*~`!^\-_+<>@\#$&▲▶◆◀■【】\\\=\(\'\"]')

    # 기사 제목에서 필요없는 특수문자들을 지움
    newline_symbol_removed_text = text.replace('\\n', '').replace('\\t', '').replace('\\r', '')
    special_symbol_removed_headline = re.sub(special_symbol, '', newline_symbol_removed_text)
    return special_symbol_removed_headline


# 데이터프레임 정제
def make_refine_df(df):
    df = df.rename(columns={0: 'newsID', 1: '제목', 2: '미디어', 3: '기자', 4: '게재일', 5: '제보횟수', 6: '기사본문url', 7: '태그',
                            8: '가짜뉴스', 9: '악의적헤드라인', 10: '사실왜곡', 11: '통계왜곡',
                            12: '잘못된인용', 13: '오보', 14: '헛소리선동', 15: '기타'})

    # int형변환
    toNumList = ['가짜뉴스', '악의적헤드라인', '사실왜곡', '통계왜곡', '잘못된인용', '오보', '헛소리선동', '기타']
    df[toNumList] = df[toNumList].astype(int)

    # 날짜 변환
    df = df[df['게재일'].notna()]  # 결측치 제거
    df.reset_index(drop=True, inplace=True)
    df['게재일'] = df['게재일'].apply(lambda x: refineDate(x))
    df['게재일'] = pd.to_datetime(df['게재일'])

    # 기사제목 특수문자 제거
    df['제목'] = df['제목'].apply(lambda x: clear_headline(x))

    return df


if __name__ == '__main__':
    crawledDF = crawliing()
    articleDF = make_refine_df(crawledDF)
    articleDF.to_csv('../data/reportrashArticle.csv')