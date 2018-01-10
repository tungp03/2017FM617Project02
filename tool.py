import requests
from io import StringIO
import pandas as pd
from pandas import Series, DataFrame
import numpy as np

def financial_statement(year, type='營益分析彙總表'):
    if year >= 1000:
        year -= 1911

    if type == '綜合損益彙總表':
        url = 'http://mops.twse.com.tw/mops/web/ajax_t163sb04'
    elif type == '資產負債彙總表':
        url = 'http://mops.twse.com.tw/mops/web/ajax_t163sb05'
    elif type == '營益分析彙總表':
        url = 'http://mops.twse.com.tw/mops/web/ajax_t163sb06'
    else:
        print('type does not match')
    r = requests.post(url, {
        'encodeURIComponent':1,
        'step':1,
        'firstin':1,
        'off':1,
        'TYPEK':'sii',
        'year':year,
        'season':4,
    })

    r.encoding = 'utf8'
    dfs = pd.read_html(r.text)


    for i, df in enumerate(dfs):
        df.columns = df.iloc[0]
        dfs[i] = df.iloc[1:]

    df = pd.concat(dfs).applymap(lambda x: x if x != '--' else np.nan)
    df = df[df['公司代號'] != '公司代號']
    df = df[~df['公司代號'].isnull()]
    df = df.sort_values(by=['公司代號'])#按公司代號进行排序
    newindex = pd.Series(range(0,len(df)))
    df.index = newindex#重命名行名
    return df

def ROEcount(year):
    if (year>=2013)&(year<=2016) :
        #print('EPS年度 %s :'% (year))
        cc =  financial_statement(year, type='資產負債彙總表')
        equity = cc[['公司代號','權益總額']].dropna().rename(columns={'公司代號':'company','權益總額':'Totale'})
        equity2 = cc[['公司代號','權益合計']].dropna().rename(columns={'公司代號':'company','權益合計':'Totale'})
        equity3 = pd.merge(equity,equity2,how='outer').sort_values(by=['company'])

        dd =  financial_statement(year, type='營益分析彙總表')
        ee = dd[['公司代號','營業收入(百萬元)','稅後純益率(%)(稅後純益)/(營業收入)']]
        ee = ee.rename(columns={'公司代號':'company','營業收入(百萬元)':'EBIT','稅後純益率(%)(稅後純益)/(營業收入)':'NOPAT'})
        ee['EBIT'] = ee['EBIT'].astype(str).astype(float)
        ee['NOPAT'] = ee['NOPAT'].astype(str).astype(float)
        ee['NOPAT2'] = ee['EBIT'] * ee['NOPAT']

        ROE = pd.merge(ee,equity3,how='left')
        ROE['Totale'] = ROE['Totale'].astype(str).astype(float)
        ROE['ROE'] = (ROE['NOPAT2']/ROE['Totale'])*100
        ROE = ROE[['company','ROE']].rename(columns={'ROE':'ROE%'})
    elif (year<2013) :
        print("請從2013年開始")
    elif (year>2016) :
        print("頂多只能到2016年")

    return ROE

# 起始年，結束年，ROE標準
def ROEyaers(startYear,endYear,ROEstandard):
    if (startYear>=2013)&(endYear<=2016) :
        ToROE = ROEcount(startYear).rename(columns={'ROE%':startYear})
        ToROE = ToROE[ToROE.iloc[:,1]>ROEstandard]
        for i in range(startYear+1,endYear+1):
            ROE1 = ROEcount(i).rename(columns={'ROE%':i})
            ROE1 = ROE1[ROE1.iloc[:,1]>ROEstandard]
            ToROE = pd.merge(ToROE,ROE1,how='left').dropna() #因此寫法，會導致n年內選股相同
        ToROE = ToROE.sort_values(by = endYear, ascending = False)

    elif (startYear<2013) :
        #ToROE = "請返回上一頁，並從2013年開始"
        print("請從2013年開始")
    elif (endYear>2016) :
        #ToROE = "請返回上一頁，頂多只能到2016年"
        print("頂多只能到2016年")

    return ToROE

def EPScount(year):
    if (year>=2013)&(year<=2016) :
        #print('EPS年度 %s :'% (year))
        aa = financial_statement(year,type='綜合損益彙總表')
        EPS = aa[['公司代號','基本每股盈餘（元）']].rename(columns={'公司代號':'company','基本每股盈餘（元）':'EPS'})
        EPS['EPS'] = EPS['EPS'].astype(str).astype(float)
    elif (year<2013) :
        print("請從2013年開始")
    elif (year>2016) :
        print("頂多只能到2016年")

    return EPS

# 起始年，結束年，EPS標準
def EPSyaers(startYear,endYear,EPSstandard):
    if (startYear>=2013)&(endYear<=2016) :
        ToEPS = EPScount(startYear).rename(columns={'EPS':str(startYear)+"EPS"})
        ToEPS = ToEPS[ToEPS.iloc[:,1]>EPSstandard]
        for i in range(startYear+1,endYear+1):
            EPS1 = EPScount(i).rename(columns={'EPS':str(i)+"EPS"})
            EPS1 = EPS1[EPS1.iloc[:,1]>EPSstandard]
            ToEPS = pd.merge(ToEPS,EPS1,how='left').dropna() #因此寫法，會導致n年內選股相同
        ToEPS = ToEPS.sort_values(by = str(endYear)+"EPS", ascending = False)
    elif (startYear<2013) :
        print("請從2013年開始")
        #ToROE = "請返回上一頁，並從2013年開始"
    elif (endYear>2016) :
        print("頂多只能到2016年")
        #ToROE = "請返回上一頁，頂多只能到2016年"
    return ToEPS

def ROEcount2(year,ROEstandard):
    if (year>=2013)&(year<=2016) :
        cc =  financial_statement(year,type='資產負債彙總表')
        equity = cc[['公司代號','權益總額']].dropna().rename(columns={'公司代號':'company','權益總額':'Totale'})
        equity2 = cc[['公司代號','權益合計']].dropna().rename(columns={'公司代號':'company','權益合計':'Totale'})
        equity3 = pd.merge(equity,equity2,how='outer').sort_values(by=['company'])

        dd =  financial_statement(year,type='營益分析彙總表')
        ee = dd[['公司代號','營業收入(百萬元)','稅後純益率(%)(稅後純益)/(營業收入)']]
        ee = ee.rename(columns={'公司代號':'company','營業收入(百萬元)':'EBIT','稅後純益率(%)(稅後純益)/(營業收入)':'NOPAT'})
        ee['EBIT'] = ee['EBIT'].astype(str).astype(float)
        ee['NOPAT'] = ee['NOPAT'].astype(str).astype(float)
        ee['NOPAT2'] = ee['EBIT'] * ee['NOPAT']

        ROE = pd.merge(ee,equity3,how='left')
        ROE['Totale'] = ROE['Totale'].astype(str).astype(float)
        ROE['ROE'] = (ROE['NOPAT2']/ROE['Totale'])*100
        ROE = ROE[['company','ROE']].rename(columns={'ROE':'ROE%'})
        ROE = ROE[ROE.iloc[:,1]>ROEstandard].sort_values(by = ['ROE%'], ascending = False)
    elif (year<2013) :
        ROE = "請返回上一頁，並從2013年開始"
    elif (year>2016) :
        ROE = "請返回上一頁，頂多只能到2016年"
    return ROE

def EPScount2(year,EPSstandard):
    if (year>=2013)&(year<=2016) :
        #print('EPS年度 %s :'% (year))
        aa = financial_statement(year,type='綜合損益彙總表')
        EPS = aa[['公司代號','基本每股盈餘（元）']].rename(columns={'公司代號':'company','基本每股盈餘（元）':'EPS'})
        EPS['EPS'] = EPS['EPS'].astype(str).astype(float)
        EPS = EPS[EPS.iloc[:,1]>EPSstandard].sort_values(by = ['EPS'], ascending = False)
    elif (year<2013) :
        EPS = "請返回上一頁，並從2013年開始"
    elif (year>2016) :
        EPS = "請返回上一頁，頂多只能到2016年"
    return EPS

def ROEyaers3(startYear,endYear,ROEstandard):
    if (startYear>=2000)&(endYear<=2016) :
        f = pd.read_csv('basic.csv')
        f['Date'] = f['Date'].astype('int')
        f['ROE(%)'] = f['ROE(%)'].astype(str).astype('float')
        f['EPS'] = f['EPS'].astype(str).astype('float')
        f['company'] = f['company'].astype('str')+".tw"
        f = f[['company','Date','ROE(%)']]
        ToROE = f[f['Date'].isin([startYear])].dropna()
        ToROE = ToROE[['company','ROE(%)']].rename(columns={'ROE(%)':str(startYear)+"ROE"})
        ToROE = ToROE[ToROE.iloc[:,1]>ROEstandard]
        for i in range(startYear,endYear+1):
            ROE = f[f['Date'].isin([i])]
            ROE = ROE[['company','ROE(%)']].rename(columns={'ROE(%)':str(i)+"ROE"})
            ROE = ROE[ROE.iloc[:,1]>ROEstandard]
            ToROE = pd.merge(ToROE,ROE,how='left').dropna()
    elif (startYear<2000) :
        print("請從2013年開始")
    elif (endYear>2016) :
        print("頂多只能到2016年")

    ToROE = ToROE.sort_values(by = str(endYear)+"ROE", ascending = False)

    return ToROE

def EPSyaers3(startYear,endYear,EPSstandard):
    if (startYear>=2000)&(endYear<=2016) :
        f = pd.read_csv('basic.csv')
        f['Date'] = f['Date'].astype('int')
        f['ROE(%)'] = f['ROE(%)'].astype(str).astype('float')
        f['EPS'] = f['EPS'].astype(str).astype('float')
        f['company'] = f['company'].astype('str')+".tw"
        f = f[['company','Date','EPS']]
        ToEPS = f[f['Date'].isin([startYear])].dropna()
        ToEPS = ToEPS[['company','EPS']].rename(columns={'EPS':str(startYear)+"EPS"})
        ToEPS = ToEPS[ToEPS.iloc[:,1]>EPSstandard]
        for i in range(startYear,endYear+1):
            EPS = f[f['Date'].isin([i])]
            EPS = EPS[['company','EPS']].rename(columns={'EPS':str(i)+"EPS"})
            EPS = EPS[EPS.iloc[:,1]>EPSstandard]
            ToEPS = pd.merge(ToEPS,EPS,how='left').dropna()
    elif (startYear<2000) :
        print("請從2013年開始")
    elif (endYear>2016) :
        print("頂多只能到2016年")

    ToEPS = ToEPS.sort_values(by = str(endYear)+"EPS", ascending = False)

    return ToEPS

def Dobyaers3(startYear,endYear,ROEstandard,EPSstandard):
    if (startYear>=2000)&(endYear<=2016) :
        f = pd.read_csv('basic.csv')
        f['Date'] = f['Date'].astype('int')
        f['ROE(%)'] = f['ROE(%)'].astype(str).astype('float')
        f['EPS'] = f['EPS'].astype(str).astype('float')
        f['company'] = f['company'].astype('str')+".tw"
        Total = f[f['Date'].isin([startYear])].dropna()
        Total = Total[['company','ROE(%)','EPS']]
        Total = Total.rename(columns={'ROE(%)':str(startYear)+"ROE",'EPS':str(startYear)+"EPS"})
        Total = Total[Total.iloc[:,1]>ROEstandard]
        Total = Total[Total.iloc[:,2]>EPSstandard]
        for i in range(startYear,endYear+1):
            Tot = f[f['Date'].isin([i])]
            Tot = Tot[['company','ROE(%)','EPS']]
            Tot = Tot.rename(columns={'ROE(%)':str(i)+"ROE",'EPS':str(i)+"EPS"})
            Tot = Tot[Tot.iloc[:,1]>ROEstandard]
            Tot = Tot[Tot.iloc[:,2]>EPSstandard]
            Total = pd.merge(Total,Tot,how='left').dropna()
    elif (startYear<2000) :
        print("請從2013年開始")
    elif (endYear>2016) :
        print("頂多只能到2016年")

    return Total
