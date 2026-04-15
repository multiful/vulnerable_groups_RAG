# Content Hash: SHA256:TBD
# Script: build_cert_domain_mapping.py
# Purpose: cert_domain_mapping.csv 재생성
#   - is_primary=True: domain_name_raw 기반 (712개)
#   - is_primary=False: keyword + top_domain fallback (578개)

import sys, csv, re, collections, os

sys.stdout.reconfigure(encoding='utf-8')

RAW_TO_DOMAIN = {
    '건설기계운전': 'domain_0013', '건설배관': 'domain_0010', '건축': 'domain_0010',
    '경영': 'domain_0017', '광해방지': 'domain_0012', '교육.자연.과학.사회과학': 'domain_0027',
    '금속.재료': 'domain_0007', '금형.공작기계': 'domain_0006', '기계장비설비.설치': 'domain_0006',
    '기계제작': 'domain_0006', '농업': 'domain_0038', '단조.주조': 'domain_0006',
    '도시.교통': 'domain_0011', '도장.도금': 'domain_0006', '디자인': 'domain_0033',
    '목재.가구.공예': 'domain_0035', '방송': 'domain_0034', '방송.무선': 'domain_0004',
    '보건.의료': 'domain_0023', '비파괴검사': 'domain_0015', '사회복지.종교': 'domain_0024',
    '생산관리': 'domain_0006', '섬유': 'domain_0032', '숙박.여행.오락.스포츠': 'domain_0029',
    '식품': 'domain_0030', '안전관리': 'domain_0012', '어업': 'domain_0038',
    '에너지.기상': 'domain_0009', '영업.판매': 'domain_0019', '용접': 'domain_0006',
    '운전.운송': 'domain_0040', '위험물': 'domain_0008', '의복': 'domain_0032',
    '이용.미용': 'domain_0031', '인쇄.사진': 'domain_0034', '임업': 'domain_0038',
    '자동차': 'domain_0013', '전기': 'domain_0005', '전자': 'domain_0005',
    '정보기술': 'domain_0002', '제과.제빵': 'domain_0030', '조경': 'domain_0011',
    '조리': 'domain_0030', '조선': 'domain_0041', '채광': 'domain_0039',
    '철도': 'domain_0040', '축산': 'domain_0038', '토목': 'domain_0011',
    '통신': 'domain_0004', '판금.제관.새시': 'domain_0006', '항공': 'domain_0042',
    '화공': 'domain_0008', '환경': 'domain_0012',
}

KEYWORD_RULES = [
    # IT/디지털
    (r'무선기사|무선통신사|전파전자통신|아마추어무선|해상무선|육상무선|항공무선통신', 'domain_0004'),
    (r'RFID|지능형홈', 'domain_0004'),
    (r'데이터거래사|데이터아키텍처|데이터분석|ADP|ADsP|DAsP|DAP|SQL|빅데이터|영상판독|영상정보', 'domain_0001'),
    (r'정보보안|보안산업기사|인터넷보안|네트워크관리|디지털포렌식|감리사|CISA|인터넷정보관리', 'domain_0003'),
    (r'게임프로그래밍|SW테스트|리눅스마스터|소프트웨어자산|스마트공장|정보처리|컴퓨터시스템|PC마스터|PC정비|ITQ|DIAT|정보기술자격|게임기획|정보시스템|IEQ|전자계산기|컴퓨터활용', 'domain_0002'),
    # 국방/특수 + 원자력 — 반드시 '조종사' 규칙보다 앞에 배치
    (r'수중무인기|수중발파|심해잠수|탄약안전|폭발물처리|함정손상|낙하산전문포장|군항공기사고|국방무인기|국방보안|국방사업', 'domain_0043'),
    (r'원자로조종|핵연료물질|방사선취급|방사성동위원소|방사선동위원소', 'domain_0009'),
    # 모빌리티/운송
    (r'선박조종사|수면비행선박|구속구조정|구명정|선박안전관리|소형선박|수상원동기|동력수상레저', 'domain_0041'),
    (r'항해사|기관사\s*[12]급|도선사|운항관리사|운항사', 'domain_0041'),
    (r'교통안전관리자.*항만', 'domain_0041'),
    (r'조종사|경량항공기|초경량비행장치|항공교통관제|항공정비사|항공영어', 'domain_0042'),
    (r'교통안전관리자.*항공', 'domain_0042'),
    (r'철도차량운전|철도교통안전|교통안전관리자.*철도', 'domain_0040'),
    (r'교통안전관리자|버스운전자', 'domain_0040'),
    # 경영/비즈니스
    (r'세무사$|세무회계|전산세무|세무\s*[123]급|회계관리|재경관리|공인회계사|AFPK|손해사정|보험계리|보험중개|건강보험사|의료보험사|신용관리|신용분석|신용상담|신용위험|국제금융역|여신심사역|외환전문역|경제이해력|TESAT|매경TEST|원가분석|보험심사|손해평가사|보상관리사|도로교통사고감정|전산회계|개인보험심사|기업보험심사', 'domain_0016'),
    (r'물류관리사|보세사|관세사|무역영어|원산지관리|검수사|검량사|스마트해상물류|유통관리사|화물운송종사', 'domain_0018'),
    (r'변리사|법무사|변호사|지식재산능력', 'domain_0022'),
    (r'행정사|공공조달|정책분석평가|해사행정', 'domain_0021'),
    (r'공인중개사|주택관리사|감정평가사|주거복지사', 'domain_0020'),
    (r'^감정사$', 'domain_0020'),
    (r'호텔경영사|호텔관리사|호텔서비스사', 'domain_0029'),
    (r'환경영향평가사', 'domain_0012'),
    (r'산업보안관리사', 'domain_0003'),
    (r'경비지도사|신변보호사', 'domain_0021'),
    (r'ERP|전자상거래|샵마스터|SMAT|CS Leaders|경영지도사|공인노무사|경영정보시각화|가맹거래사|병원행정사|한방병원행정사|문서실무사|행정관리사|기록물관리', 'domain_0017'),
    # 교육/생활서비스
    (r'관광통역안내사|국내여행안내사', 'domain_0029'),
    (r'한국어교원|한국어교육능력|FLEX|번역능력인정|통번역사|KBS한국어|국어능력인증|한국실용글쓰기|수화통역사|영어번역능력|한글속기|상공회의소한자|한자급수|한자능력|한자실력|한자어능력|한자\.한문|한국한자|워드프로세서|점역교정사', 'domain_0028'),
    (r'바리스타|소믈리에|푸드코디네이터', 'domain_0030'),
    (r'피부관리사|두피타투|SMP', 'domain_0031'),
    (r'봉제기능사', 'domain_0032'),
    (r'비서\s*[123]급', 'domain_0017'),
    (r'직업능력개발훈련교사|평생교육사|청소년지도사|문화예술교육사|보건교육사|어린이영어지도사|유아영어지도사|정사서|산림교육전문가|유아숲지도사|환경교육사|소방안전교육사|목재교육전문가|한국사능력검정|가정생활교육사|논술지도사|독서지도사|실천예절지도사|문화유산교육전문가|문예창작사|문화선교사', 'domain_0027'),
    # 보건/복지
    (r'안경사|보건의료정보관리|영양사|위생사|응급구조사|의무기록사|방사선사|임상병리사|작업치료사|의료기기RA|언어재활사|의지보조기|보조공학사|산업보건지도사|안마사|병원코디네이터', 'domain_0023'),
    (r'사회복지사|정신건강사회복지|장애인재활상담사|청소년상담사|가족상담사|아동상담사|미술심리상담|미술치료사|가정복지사|건강가정사|원예치료사|요양보호사|장례지도사|레크리에이션지도자|아동미술지도사|언어치료사', 'domain_0024'),
    (r'생활스포츠지도사|장애인스포츠지도사|전문스포츠지도사|노인스포츠지도사|유소년스포츠지도사|재활승마지도사|건강운동관리사|생활체육지도사|경주심판|유아체육지도자|스포츠마사지|수상구조사|인명구조사|수상인명구조|심폐소생술|생활건강관리사|브레인트레이너|보행지도사', 'domain_0025'),
    (r'반려동물|반려견|애견미용', 'domain_0026'),
    # 엔지니어링/산업기술
    (r'소방시설관리사|소방안전관리자|화재조사관|방재안전관리사|방재전문인력|기업재난관리사', 'domain_0014'),
    (r'산업안전지도사|연구실안전관리사|정수시설운영관리|환경측정분석사', 'domain_0012'),
    (r'자동차운전전문강사|자동차운전면허|자동차운전기능검정|자동차진단평가사|이륜자동차정비', 'domain_0013'),
    (r'방사선취급|방사성동위원소|방사선동위원소|원자로조종|핵연료물질', 'domain_0009'),
    (r'목구조시공|목구조관리|건축물에너지평가|건축사$|실내디자이너|열쇠관리사|시스템에어컨', 'domain_0010'),
    (r'전자부품장착기능사|반도체설계', 'domain_0005'),
    (r'정밀화학기사|바이오공정기능사|맞춤형화장품조제|조향사', 'domain_0008'),
    (r'아스팔트피니셔|조경수조성관리', 'domain_0011'),
    (r'냉매취급관리사', 'domain_0006'),
    # 크리에이티브/미디어
    (r'국가유산수리|박물관및미술관준학예사', 'domain_0037'),
    (r'무대예술전문인', 'domain_0036'),
    (r'서비스.*디자인기사|게임그래픽전문가|GTQ|멀티미디어전문가|옥외광고사', 'domain_0033'),
    (r'주얼리마스터|종이접기', 'domain_0035'),
    # 1차산업/자원
    (r'수목치료|나무의사|산림치유|분재관리', 'domain_0038'),
    (r'수산질병|수산물품질', 'domain_0038'),
    (r'농산물|스마트농업|치유농업|농어촌개발|말조련사|장제사|가축인공수정|경매사', 'domain_0038'),
]

TOP_FALLBACK = {
    'IT/디지털': 'domain_0002',
    '엔지니어링/산업기술': 'domain_0006',
    '경영/비즈니스': 'domain_0017',
    '보건/복지': 'domain_0023',
    '교육/생활서비스': 'domain_0027',
    '크리에이티브/미디어': 'domain_0034',
    '1차산업/자원': 'domain_0038',
    '모빌리티/운송': 'domain_0040',
    '국방/특수': 'domain_0043',
}


def find_fallback_domain(cert_name, top_domain):
    for pattern, domain_id in KEYWORD_RULES:
        if re.search(pattern, cert_name, re.IGNORECASE):
            return domain_id, 'keyword'
    return TOP_FALLBACK.get(top_domain), 'top_domain_fallback'


def main():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cert_path = os.path.join(base, 'data', 'processed', 'master', 'cert_master.csv')
    out_path = os.path.join(base, 'data', 'canonical', 'relations', 'cert_domain_mapping.csv')

    with open(cert_path, encoding='utf-8-sig') as f:
        cert_rows = list(csv.DictReader(f))

    all_rows = []
    idx = 1
    stats = collections.Counter()

    for r in cert_rows:
        raw = r['domain_name_raw'].strip()
        cert_id = r['cert_id']
        cert_name = r['cert_name']
        top_domain = r['top_domain']

        if raw and raw in RAW_TO_DOMAIN:
            all_rows.append({
                'relation_id': f'cdm_{idx:05d}',
                'cert_id': cert_id,
                'domain_sub_label_id': RAW_TO_DOMAIN[raw],
                'is_primary': 'True',
                'is_active': 'True',
            })
            idx += 1
            stats['primary'] += 1
        else:
            domain_id, method = find_fallback_domain(cert_name, top_domain)
            if domain_id:
                all_rows.append({
                    'relation_id': f'cdm_{idx:05d}',
                    'cert_id': cert_id,
                    'domain_sub_label_id': domain_id,
                    'is_primary': 'False',
                    'is_active': 'True',
                })
                idx += 1
                stats[method] += 1
            else:
                stats['no_match'] += 1

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['relation_id', 'cert_id', 'domain_sub_label_id', 'is_primary', 'is_active'])
        w.writeheader()
        w.writerows(all_rows)

    print(f'cert_domain_mapping.csv 재생성 완료: {len(all_rows)}행')
    print(f'  primary (domain_name_raw): {stats["primary"]}행')
    print(f'  fallback keyword:          {stats["keyword"]}행')
    print(f'  fallback top_domain:       {stats["top_domain_fallback"]}행')
    if stats['no_match']:
        print(f'  no_match:                  {stats["no_match"]}개')
    print(f'  커버: {len(all_rows)}/{len(cert_rows)} ({100*len(all_rows)/len(cert_rows):.1f}%)')


if __name__ == '__main__':
    main()
