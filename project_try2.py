import technical as th
import tool
import ffn
from flask import Flask
import numpy as np
import pandas as pd
import pandas_datareader.data as web
import requests
from datetime import datetime
import pickle
import talib
from talib import MA_Type
import requests
import io

app = Flask(__name__)

@app.route('/')
def index():
    message = """<font face="微軟正黑體">
    <FONT SIZE=6 COLOR=#008A00><B>歡迎使用我們的網站!以下是我們的架構說明：</B></FONT><br/>
    <FONT SIZE=5>我們提供兩個步驟，分別是<B>選股(基本面指標或自己選定)</B>與<B>回測(技術面指標)</B></FONT><br/>
    <br/>
    <FONT SIZE=5><U><B>Step1.選股</B></U></FONT><br/>
    1-1 我們有提供兩個基本面指標供篩選股票，請選擇一項<br/>
    /ROE_strategy ==> <B>ROE</B>選股<br/>
    /EPS_strategy ==> <B>EPS</B>選股<br/>
    /Dob_strategy ==> <B>ROE&EPS</B>選股<br/>
    <br/>
    1-2 我想要自己key特定股票代碼<br/>
    請直接從下列五個技術指標策略中，選一項吧~<br/>
    /BBands_strategy ==> <B>布林通道</B>策略，以股價跌破通道下方線買進，突破通道上方線賣出<br/>
    /RSI_strategy ==> <B>RSI</B>策略，以當日RSI值跌破RSI低點買進，突破RSI高點賣出<br/>
    /MA_strategy ==> <B>均線</B>策略，當今日股價突破短期均線，且短期均線突破長均線時買進；當股價跌破短期均線且短均線跌破長均線時賣出<br/>
    /KD_strategy ==> <B>KD值</B>策略，K值由下穿越D值且D值大於某值代表行情看好，買進；K值由上穿越D值且D值小於某值代表行情看壞，賣出<br/>
    /william_strategy ==> <B>威廉指標</B>(以正數表示)，一般來說低於20%的水平會視為超買（Overbought）的訊號，而大於80%以下則被視為超賣（Oversold）訊號<br/>
    </font>"""
    return message

@app.route('/KD_strategy')
def KD():
    message = """<font face="微軟正黑體">
    <FONT SIZE=5 COLOR=#0000B2><B>KD值策略輸入格式:股票代碼+起始日期,結束日期+買進D值+賣出D值 </B></FONT> <br/>
    注意:年度請從1993年開始<br/>
    <br/>
    <B>單支股票</B>範例：台積電,從2016年9月1號開始到2017年1月10號，當K由下穿越D且D值大於<B>60</B>時買進，K由上穿越D且D小於<B>40</B>時賣出<br/>
    輸入：/KD_strategy/<B>2330.tw</B>+2016-09-01,2017-01-10<B>+60+40</B><br/>
    <B>多支股票</B>範例：台積電、鴻海、大立光,從2016年9月1號開始到2017年1月10號，當K由下穿越D且D值大於<B>60</B>時買進，K由上穿越D且D小於<B>40</B>時賣出<br/>
    輸入：/KD_strategy/<B>2330.tw,2317.tw,3008.tw</B>+2016-09-01,2017-01-10<B>+60+40</B><br/>
    </font>"""
    return message

@app.route('/william_strategy')
def william():
    message = """<font face="微軟正黑體">
    <FONT SIZE=5 COLOR=#0000B2><B>威廉指標測策略輸入格式:股票代碼+日期+買進W值+賣出W值 </B> </FONT><br/>
    注意:年度請從1993年開始<br/>
    <br/>
    威廉指標，在應用W值時，一般來說是依據以下原則：<br/>
    1.在最近5日內W值達大於80%時，市場處於超賣狀況（在相對的時間窗口），股價隨時可能出現見底。<br/>
    因此80的水平橫線稱為之買進線，投資者在此可以在此伺機買入，相反，當W值達到低於20時，市場處於超買狀況，走勢可能即將見頂，20的橫線被稱為賣出線。<br/>
    2.當最進5日內W由下方的超賣區向上爬而穿過中軸50時，表示開始轉勢，由弱變強，相反由超買區向下跌落，跌破50中軸線後，可確認強市轉弱，是賣出的訊號。<br/>
    <br/>
    <B>單支股票</B>範例：台積電,從2016年9月1號開始到2017年1月10號，當W值突破<B>80</B>時買進，跌破<B>20</B>時賣出<br/>
    輸入：/william_strategy/<B>2330.tw</B>+2016-09-01,2017-01-10+5<B>+80+20</B><br/>
    <B>多支股票</B>範例：台積電、鴻海、大立光,從2016年9月1號開始到2017年1月10號，當W值突破<B>80</B>時買進，跌破<B>20</B>時賣出<br/>
    輸入：/william_strategy/<B>2330.tw,2317.tw,3008.tw</B>+2016-09-01,2017-01-10+5<B>+80+20</B><br/>
    </font>"""
    return message

@app.route('/RSI_strategy')
def RSI():
    message = """ <font face="微軟正黑體">
    <FONT SIZE=5 COLOR=#0000B2><B>RSI策略輸入格式：股票代碼+起始日期,結束日期+RSI低點值+RSI高點值 </B></FONT> <br/>
    注意:年度請從1993年開始<br/>
    <br/>
    <B>單支股票</B>範例：台積電,從2016年9月1號開始到2017年1月10號，當RSI跌破<B>20</B>時買進，大於<B>80</B>時賣出<br/>
    輸入：/RSI_strategy/<B>2330.tw</B>+2016-09-01,2017-01-10<B>+20+80</B> <br/>
    <B>多支股票</B>範例：台積電、鴻海、大立光,從2016年9月1號開始到2017年1月10號，當RSI跌破<B>20</B>時買進，大於<B>80</B>時賣出<br/>
    輸入：/RSI_strategy/<B>2330.tw,2317.tw,3008.tw</B>+2016-09-01,2017-01-10<B>+20+80</B> <br/>
    </font>"""
    return message

@app.route('/MA_strategy')
def MA():
    message = """<font face="微軟正黑體">
    <FONT SIZE=5 COLOR=#0000B2><B>均線策略輸入格式：股票代碼+起始日期,結束日期+短期MA+長期MA </B></FONT> <br/>
    注意:年度請從1993年開始<br/>
    <br/>
    <B>單支股票</B>範例：台積電,從2016年9月1號開始到2017年1月10號，當股價突破<B>5MA</B>且5MA突破<B>30MA</B>時買進，跌破時賣出<br/>
    輸入：/MA_strategy/<B>2330.tw</B>+2016-09-01,2017-01-10<B>+5+30</B><br/>
    <B>多支股票</B>範例：台積電、鴻海、大立光,從2016年9月1號開始到2017年1月10號，當股價突破<B>5MA</B>且5MA突破<B>30MA</B>時買進，跌破時賣出<br/>
    輸入：/MA_strategy/<B>2330.tw,2317.tw,3008.tw</B>+2016-09-01,2017-01-10<B>+5+30</B><br/>
    </font>"""
    return message

@app.route('/BBands_strategy')
def BBands():
    message = """ <font face="微軟正黑體">
    <FONT SIZE=5 COLOR=#0000B2><B>布林通道策略輸入格式：股票代碼+起始日期,結束日期+平均日數+標準差間距 </B> </FONT> <br/>
    注意:年度請從1993年開始<br/>
    <br/>
    <B>單支股票</B>範例：台積電,從2016年9月1號開始到2017年1月10號，以<B>MA10</B>(平均10天)為中間基準，抓上下<B>3</B>個標準差的距離<br/>
    輸入：/BBands_strategy/<B>2330.tw</B>+2016-09-01,2017-01-10<B>+10+3</B> <br/>
    <B>多支股票</B>範例：台積電、鴻海、大立光,從2016年9月1號開始到2017年1月10號，以<B>MA10</B>(平均10天)為中間基準，抓上下<B>3</B>個標準差的距離<br/>
    輸入：/BBands_strategy/<B>2330.tw,2317.tw,3008.tw</B>+2016-09-01,2017-01-10,2017-01-10<B>+10+3</B> <br/>
    </font>"""
    return message

@app.route('/BBands_strategy/<string:symbol>')
def BBands_strategy(symbol):
    varname = symbol
    stock = varname.split('+')[0]
    stock = stock.split(',')
    date = varname.split('+')[1]
    startdate = date.split(',')[0]
    enddate = date.split(',')[1]
    timeperiod = int(varname.split('+')[2])
    std = int(varname.split('+')[3])
    results = []
    erstock = []
    erresult = []
    for n in range(0, len(stock)):
        try:
            df = web.DataReader(stock[n], 'yahoo', startdate, enddate)
            df = df.dropna()
            df = th.BBands_way(df,timeperiod,std)
            try:
                if np.all(df['signals']==0):
                    print("Stock:", stock[n], "策略沒有出現買賣訊號。")
                    continue
                SharpeRatio, maxdd, maxddd, finalRet = th.indicators(df)
                days = (df.index[-1] - df.index[0]).days
                results.append((SharpeRatio, maxdd, maxddd, finalRet, days, df[df['signals'] > 0]['signals'].sum(), stock[n]))
            except Exception as e:
                print("Error occurs at stock:", stock[n], "==>", e.args)
        except Exception as e_2:
            erstock = stock[n]+"下載股價資料出錯"
            erresult.append(erstock)
    results_df = pd.DataFrame(results, columns=['sharpe','MaxDrawDown','MaxDrawDownDuration','returns(%)',
                                            'days', 'entries','stock'])
    erresult2 = str(erresult)
    text1 = """<font face="微軟正黑體">
    <br/><br/><B>回測結果如上，歡迎回首頁重新選擇^^</B>
    </font>"""

    return results_df.to_html()+erresult2 + text1

@app.route('/KD_strategy/<string:symbol>') #2330.tw+2016-05-01+40+60
def KD_strategy(symbol):
    varname = symbol
    stock = varname.split('+')[0]
    stock = stock.split(',')
    date = varname.split('+')[1]
    startdate = date.split(',')[0]
    enddate = date.split(',')[1]
    upbreak = int(varname.split('+')[2])
    downbreak = int(varname.split('+')[3])
    results = []
    erstock = []
    erresult = []
    for n in range(0, len(stock)):
        try:
            df = web.DataReader(stock[n], 'yahoo', startdate, enddate)
            df = df.dropna()
            df = th.KD_way(df,upbreak,downbreak)
            try:
                if np.all(df['signals']==0):
                    print("Stock:", stock[n], "策略沒有出現買賣訊號。")
                    continue
                SharpeRatio, maxdd, maxddd, finalRet = th.indicators(df)
                days = (df.index[-1] - df.index[0]).days
                results.append((SharpeRatio, maxdd, maxddd, finalRet, days, df[df['signals'] > 0]['signals'].sum(), stock[n]))
            except Exception as e:
                print("Error occurs at stock:", stock[n], "==>", e.args)
        except Exception as e_2:
            erstock = stock[n]+"下載股價資料出錯"
            erresult.append(erstock)
    results_df = pd.DataFrame(results, columns=['sharpe','MaxDrawDown','MaxDrawDownDuration','returns(%)',
                                            'days', 'entries','stock'])
    erresult2 = str(erresult)
    text1 = """<font face="微軟正黑體">
    <br/><br/><B>回測結果如上，歡迎回首頁重新選擇^^</B>
    </font>"""

    return results_df.to_html()+erresult2 + text1

@app.route('/william_strategy/<string:symbol>') #2330.tw+2016-05-01+80+20
def william_strategy(symbol):
    varname = symbol
    stock = varname.split('+')[0]
    stock = stock.split(',')
    date = varname.split('+')[1]
    startdate = date.split(',')[0]
    enddate = date.split(',')[1]
    timeperiod = int(varname.split('+')[2])
    oversold = int(varname.split('+')[3])
    overbuy = int(varname.split("+")[4])
    results = []
    erstock = []
    erresult = []
    for n in range(0, len(stock)):
        try:
            df = web.DataReader(stock[n], 'yahoo', startdate, enddate)
            df = df.dropna()
            df = th.william_way(df,timeperiod,oversold,overbuy)
            try:
                if np.all(df['signals']==0):
                    print("Stock:", stock[n], "策略沒有出現買賣訊號。")
                    continue
                SharpeRatio, maxdd, maxddd, finalRet = th.indicators(df)
                days = (df.index[-1] - df.index[0]).days
                results.append((SharpeRatio, maxdd, maxddd, finalRet, days, df[df['signals'] > 0]['signals'].sum(), stock[n]))
            except Exception as e:
                print("Error occurs at stock:", stock[n], "==>", e.args)
        except Exception as e_2:
            erstock = stock[n]+"下載股價資料出錯"
            erresult.append(erstock)
    results_df = pd.DataFrame(results, columns=['sharpe','MaxDrawDown','MaxDrawDownDuration','returns(%)',
                                            'days', 'entries','stock'])
    erresult2 = str(erresult)
    text1 = """<font face="微軟正黑體">
    <br/><br/><B>回測結果如上，歡迎回首頁重新選擇^^</B>
    </font>"""

    return results_df.to_html()+erresult2 + text1

@app.route('/RSI_strategy/<string:symbol>')
def RSI_strategy(symbol):
    varname = symbol
    stock = varname.split('+')[0]
    stock = stock.split(',')
    date = varname.split('+')[1]
    startdate = date.split(',')[0]
    #if (datetime.strptime(startdate,'%Y-%m-%d').year < 1993):
    #    startdate = "1993-01-01"
    enddate = date.split(',')[1]
    LRSI = int(varname.split('+')[2])
    HRSI = int(varname.split('+')[3])
    results = []
    erstock = []
    erresult = []
    for n in range(0, len(stock)):
        try:
            df = web.DataReader(stock[n], 'yahoo', startdate, enddate)
            df = df.dropna()
            df = th.RSI_way(df,LRSI,HRSI)
            try:
                if np.all(df['signals']==0):
                    print("Stock:", stock[n], "策略沒有出現買賣訊號。")
                    continue
                SharpeRatio, maxdd, maxddd, finalRet = th.indicators(df)
                days = (df.index[-1] - df.index[0]).days
                results.append((SharpeRatio, maxdd, maxddd, finalRet, days, df[df['signals'] > 0]['signals'].sum(), stock[n]))
            except Exception as e:
                print("Error occurs at stock:", stock[n], "==>", e.args)
        except Exception as e_2:
            erstock = stock[n]+"下載股價資料出錯"
            erresult.append(erstock)
    results_df = pd.DataFrame(results, columns=['sharpe','MaxDrawDown','MaxDrawDownDuration','returns(%)',
                                            'days', 'entries','stock'])
    erresult2 = str(erresult)
    text1 = """<font face="微軟正黑體">
    <br/><br/><B>回測結果如上，歡迎回首頁重新選擇^^</B>
    </font>"""

    return results_df.to_html()+erresult2 + text1

@app.route('/MA_strategy/<string:symbol>')
def MA_strategy(symbol):
    varname = symbol
    stock = varname.split('+')[0]
    stock = stock.split(',')
    date = varname.split('+')[1]
    startdate = date.split(',')[0]
    enddate = date.split(',')[1]
    SMA = int(varname.split('+')[2])
    LMA = int(varname.split('+')[3])
    results = []
    erstock = []
    erresult = []
    for n in range(0, len(stock)):
        try:
            df = web.DataReader(stock[n], 'yahoo', startdate, enddate)
            df = df.dropna()
            df = th.MA_way(df,SMA,LMA)
            try:
                if np.all(df['signals']==0):
                    print("Stock:", stock[n], "策略沒有出現買賣訊號。")
                    continue
                SharpeRatio, maxdd, maxddd, finalRet = th.indicators(df)
                days = (df.index[-1] - df.index[0]).days
                results.append((SharpeRatio, maxdd, maxddd, finalRet, days, df[df['signals'] > 0]['signals'].sum(), stock[n]))
            except Exception as e:
                print("Error occurs at stock:", stock[n], "==>", e.args)
        except Exception as e_2:
            erstock = stock[n]+"下載股價資料出錯"
            erresult.append(erstock)
    results_df = pd.DataFrame(results, columns=['sharpe','MaxDrawDown','MaxDrawDownDuration','returns(%)',
                                            'days', 'entries','stock'])
    erresult2 = str(erresult)
    text1 = """<font face="微軟正黑體">
    <br/><br/><B>回測結果如上，歡迎回首頁重新選擇^^</B>
    </font>"""

    return results_df.to_html()+erresult2 + text1

@app.route('/ROE_strategy')
def ROE_strategy():
    message = """<font face="微軟正黑體">
    <FONT SIZE=5><B>以連續n年ROE大於特定值作為基準，選出排名前段的股票</B></FONT><br/>
    注意:年度請挑2000-2016內任意年<br/>
    <br/>
    範例：選出2014年到2016年ROE大於2.5%的公司<br/>
    輸入：/ROE_strategy/2014,2016,2.5/companyROE<br/>
    </font>"""
    return message

@app.route('/ROE_strategy/<string:symbol>/companyROE')
def companyROE(symbol):
    varname = symbol
    startdate = varname.split(',')[0]
    enddate = varname.split(',')[1]
    standard = float(varname.split(',')[2])
    startdate = datetime.strptime(startdate,'%Y').year
    enddate = datetime.strptime(enddate,'%Y').year
    df = tool.ROEyaers3(startdate,enddate,standard)
    #aa = type(df)
    #df2 = df[['company']].to_string(header=False, index=False).replace('\n','.tw,')+".tw"
    message = """<font face="微軟正黑體">
    <FONT SIZE=5><U><B>Step2.回測</B></U></FONT><br/>
    回測方式：布林通道策略、RSI策略、均線策略、KD值策略、威廉指標策略<br/>
    請選擇回測方式、時間區間與前n名股票<br/>
    注意:回測時間最早只能從1993年開始<br/>
    <br/>
    1.布林通道策略範例：從2016年9月1號開始到2017年1月10號，選ROE排名前<B>5</B>檔，以<B>10</B>(平均10天)為中間基準，抓上下<B>3</B>個標準差的距離<br/>
      輸入：/ROE_strategy/2014,2016,2.5/companyROE/ROE_BBands/2016-09-01,2017-01-10<B>+5+10+3</B><br/>
      <br/>
    2.RSI策略範例：從2016年9月1號開始到2017年1月10號，選ROE排名前<B>5</B>檔，當RSI跌破<B>20</B>時買進，大於<B>80</B>時賣出<br/>
      輸入：/ROE_strategy/2014,2016,2.5/companyROE/ROE_RSI/2016-09-01,2017-01-10<B>+5+20+80</B><br/>
      <br/>
    3.均線策略範例：從2016年9月1號開始到2017年1月10號，選ROE排名前<B>5</B>檔，當股價突破<B>7</B>MA且7MA突破<B>35</B>MA時買進，跌破時賣出<br/>
      輸入：/ROE_strategy/2014,2016,2.5/companyROE/ROE_MA/2016-09-01,2017-01-10<B>+5+7+35</B><br/>
      <br/>
    4.KD策略範例：從2016年9月1號開始到2017年1月10號，選ROE排名前<B>5</B>檔，當K由下穿越D且D值大於<B>60</B>時買進，K由上穿越D且D小於<B>40</B>時賣出<br/>
      輸入：/ROE_strategy/2014,2016,2.5/companyROE/ROE_KD/2016-09-01,2017-01-10<B>+5+60+40</B><br/>
      <br/>
    5.威廉指標範例：從2016年9月1號開始到2017年1月10號，選ROE排名前<B>5</B>檔，當最近<B>7</B>日內W值突破<B>80</B>時買進，跌破<B>20</B>時賣出<br/>
      輸入：/ROE_strategy/2014,2016,2.5/companyROE/ROE_william/2016-09-01,2017-01-10<B>+5+7+80+20</B><br/>
    <br/><br/>
    <FONT SIZE=5><U><B>ROE選股結果，依最新年份之ROE大到小排序</B></U></FONT><br/>
    </font>"""
    #if aa == str:
        #df3 = df
    #else:
        #df3 = df.to_html() + message
    df3 = message + df.to_html()
    return df3

@app.route('/ROE_strategy/<string:symbol>/companyROE/ROE_BBands/<string:test>')
def ROE_BBands(symbol,test):
    varname = symbol
    startdate = varname.split(',')[0]
    enddate = varname.split(',')[1]
    standard = float(varname.split(',')[2])
    startdate = datetime.strptime(startdate,'%Y').year
    enddate = datetime.strptime(enddate,'%Y').year
    df = tool.ROEyaers3(startdate,enddate,standard)
    df2 = df[['company']].to_string(header=False, index=False).replace('\n',',')
    varname2 = test
    testday = varname2.split('+')[0]
    test_star = testday.split(',')[0]
    test_end = testday.split(',')[1]
    stocknom = int(varname2.split('+')[1])
    timeperiod = int(varname2.split('+')[2])
    std = int(varname2.split('+')[3])
    stock = df2.split(',')[0:stocknom]
    results = []
    erstock = []
    erresult = []
    for n in range(0, len(stock)):
        try:
            df = web.DataReader(stock[n], 'yahoo', test_star, test_end)
            df = df.dropna()
            df = th.BBands_way(df,timeperiod,std)
            try:
                if np.all(df['signals']==0):
                    print("Stock:", stock[n], "策略沒有出現買賣訊號。")
                    continue
                SharpeRatio, maxdd, maxddd, finalRet = th.indicators(df)
                days = (df.index[-1] - df.index[0]).days
                results.append((SharpeRatio, maxdd, maxddd, finalRet, days, df[df['signals'] > 0]['signals'].sum(), stock[n]))
            except Exception as e:
                print("Error occurs at stock:", stock[n], "==>", e.args)
        except Exception as e_2:
            erstock = stock[n]+"下載股價資料出錯"
            erresult.append(erstock)
    results_df = pd.DataFrame(results, columns=['sharpe','MaxDrawDown','MaxDrawDownDuration','returns(%)',
                                            'days', 'entries','stock'])
    erresult2 = str(erresult)
    text1 = """<font face="微軟正黑體">
    <br/><br/><B>回測結果如上，歡迎回首頁重新選擇^^</B>
    </font>"""

    return results_df.to_html()+erresult2 + text1

@app.route('/ROE_strategy/<string:symbol>/companyROE/ROE_KD/<string:test>')
def ROE_KD(symbol,test):
    varname = symbol
    startdate = varname.split(',')[0]
    enddate = varname.split(',')[1]
    standard = float(varname.split(',')[2])
    startdate = datetime.strptime(startdate,'%Y').year
    enddate = datetime.strptime(enddate,'%Y').year
    df = tool.ROEyaers3(startdate,enddate,standard)
    df2 = df[['company']].to_string(header=False, index=False).replace('\n',',')
    varname2 = test
    testday = varname2.split('+')[0]
    test_star = testday.split(',')[0]
    test_end = testday.split(',')[1]
    stocknom = int(varname2.split('+')[1])
    upbreak = int(varname2.split('+')[2])
    downbreak = int(varname2.split('+')[3])
    stock = df2.split(',')[0:stocknom]
    results = []
    erstock = []
    erresult = []
    for n in range(0, len(stock)):
        try:
            df = web.DataReader(stock[n], 'yahoo', test_star, test_end)
            df = df.dropna()
            df = th.KD_way(df,upbreak,downbreak)
            try:
                if np.all(df['signals']==0):
                    print("Stock:", stock[n], "策略沒有出現買賣訊號。")
                    continue
                SharpeRatio, maxdd, maxddd, finalRet = th.indicators(df)
                days = (df.index[-1] - df.index[0]).days
                results.append((SharpeRatio, maxdd, maxddd, finalRet, days, df[df['signals'] > 0]['signals'].sum(), stock[n]))
            except Exception as e:
                print("Error occurs at stock:", stock[n], "==>", e.args)
        except Exception as e_2:
            erstock = stock[n]+"下載股價資料出錯"
            erresult.append(erstock)
    results_df = pd.DataFrame(results, columns=['sharpe','MaxDrawDown','MaxDrawDownDuration','returns(%)',
                                            'days', 'entries','stock'])
    erresult2 = str(erresult)
    text1 = """<font face="微軟正黑體">
    <br/><br/><B>回測結果如上，歡迎回首頁重新選擇^^</B>
    </font>"""

    return results_df.to_html()+erresult2 + text1

@app.route('/ROE_strategy/<string:symbol>/companyROE/ROE_william/<string:test>')
def ROE_william(symbol,test):
    varname = symbol
    startdate = varname.split(',')[0]
    enddate = varname.split(',')[1]
    standard = float(varname.split(',')[2])
    startdate = datetime.strptime(startdate,'%Y').year
    enddate = datetime.strptime(enddate,'%Y').year
    df = tool.ROEyaers3(startdate,enddate,standard)
    df2 = df[['company']].to_string(header=False, index=False).replace('\n',',')
    varname2 = test
    testday = varname2.split('+')[0]
    test_star = testday.split(',')[0]
    test_end = testday.split(',')[1]
    stocknom = int(varname2.split('+')[1])
    timeperiod = int(varname2.split('+')[2])
    oversold = int(varname2.split('+')[3])
    overbuy = int(varname2.split("+")[4])
    stock = df2.split(',')[0:stocknom]
    results = []
    erstock = []
    erresult = []
    for n in range(0, len(stock)):
        try:
            df = web.DataReader(stock[n], 'yahoo', test_star, test_end)
            df = df.dropna()
            df = th.william_way(df,upbreak,downbreak)
            try:
                if np.all(df['signals']==0):
                    print("Stock:", stock[n], "策略沒有出現買賣訊號。")
                    continue
                SharpeRatio, maxdd, maxddd, finalRet = th.indicators(df)
                days = (df.index[-1] - df.index[0]).days
                results.append((SharpeRatio, maxdd, maxddd, finalRet, days, df[df['signals'] > 0]['signals'].sum(), stock[n]))
            except Exception as e:
                print("Error occurs at stock:", stock[n], "==>", e.args)
        except Exception as e_2:
            erstock = stock[n]+"下載股價資料出錯"
            erresult.append(erstock)
    results_df = pd.DataFrame(results, columns=['sharpe','MaxDrawDown','MaxDrawDownDuration','returns(%)',
                                            'days', 'entries','stock'])
    erresult2 = str(erresult)
    text1 = """<font face="微軟正黑體">
    <br/><br/><B>回測結果如上，歡迎回首頁重新選擇^^</B>
    </font>"""

    return results_df.to_html()+erresult2 + text1

@app.route('/ROE_strategy/<string:symbol>/companyROE/ROE_RSI/<string:test>')
def ROE_RSI(symbol,test):
    varname = symbol
    startdate = varname.split(',')[0]
    enddate = varname.split(',')[1]
    standard = float(varname.split(',')[2])
    startdate = datetime.strptime(startdate,'%Y').year
    enddate = datetime.strptime(enddate,'%Y').year
    df = tool.ROEyaers3(startdate,enddate,standard)
    df2 = df[['company']].to_string(header=False, index=False).replace('\n',',')
    varname2 = test
    testday = varname2.split('+')[0]
    test_star = testday.split(',')[0]
    test_end = testday.split(',')[1]
    stocknom = int(varname2.split('+')[1])
    LRSI = int(varname2.split('+')[2])
    HRSI = int(varname2.split('+')[3])
    stock = df2.split(',')[0:stocknom]
    results = []
    erstock = []
    erresult = []
    for n in range(0, len(stock)):
        try:
            df = web.DataReader(stock[n], 'yahoo', test_star, test_end)
            df = df.dropna()
            df = th.RSI_way(df,upbreak,downbreak)
            try:
                if np.all(df['signals']==0):
                    print("Stock:", stock[n], "策略沒有出現買賣訊號。")
                    continue
                SharpeRatio, maxdd, maxddd, finalRet = th.indicators(df)
                days = (df.index[-1] - df.index[0]).days
                results.append((SharpeRatio, maxdd, maxddd, finalRet, days, df[df['signals'] > 0]['signals'].sum(), stock[n]))
            except Exception as e:
                print("Error occurs at stock:", stock[n], "==>", e.args)
        except Exception as e_2:
            erstock = stock[n]+"下載股價資料出錯"
            erresult.append(erstock)
    results_df = pd.DataFrame(results, columns=['sharpe','MaxDrawDown','MaxDrawDownDuration','returns(%)',
                                            'days', 'entries','stock'])
    erresult2 = str(erresult)
    text1 = """<font face="微軟正黑體">
    <br/><br/><B>回測結果如上，歡迎回首頁重新選擇^^</B>
    </font>"""

    return results_df.to_html()+erresult2 + text1

@app.route('/ROE_strategy/<string:symbol>/companyROE/ROE_MA/<string:test>')
def ROE_MA(symbol,test):
    varname = symbol
    startdate = varname.split(',')[0]
    enddate = varname.split(',')[1]
    standard = float(varname.split(',')[2])
    startdate = datetime.strptime(startdate,'%Y').year
    enddate = datetime.strptime(enddate,'%Y').year
    df = tool.ROEyaers3(startdate,enddate,standard)
    df2 = df[['company']].to_string(header=False, index=False).replace('\n',',')
    varname2 = test
    testday = varname2.split('+')[0]
    test_star = testday.split(',')[0]
    test_end = testday.split(',')[1]
    stocknom = int(varname2.split('+')[1])
    SMA = int(varname2.split('+')[2])
    LMA = int(varname2.split('+')[3])
    stock = df2.split(',')[0:stocknom]
    results = []
    erstock = []
    erresult = []
    for n in range(0, len(stock)):
        try:
            df = web.DataReader(stock[n], 'yahoo', test_star, test_end)
            df = df.dropna()
            df = th.MA_way(df,upbreak,downbreak)
            try:
                if np.all(df['signals']==0):
                    print("Stock:", stock[n], "策略沒有出現買賣訊號。")
                    continue
                SharpeRatio, maxdd, maxddd, finalRet = th.indicators(df)
                days = (df.index[-1] - df.index[0]).days
                results.append((SharpeRatio, maxdd, maxddd, finalRet, days, df[df['signals'] > 0]['signals'].sum(), stock[n]))
            except Exception as e:
                print("Error occurs at stock:", stock[n], "==>", e.args)
        except Exception as e_2:
            erstock = stock[n]+"下載股價資料出錯"
            erresult.append(erstock)
    results_df = pd.DataFrame(results, columns=['sharpe','MaxDrawDown','MaxDrawDownDuration','returns(%)',
                                            'days', 'entries','stock'])
    erresult2 = str(erresult)
    text1 = """<font face="微軟正黑體">
    <br/><br/><B>回測結果如上，歡迎回首頁重新選擇^^</B>
    </font>"""

    return results_df.to_html()+erresult2 + text1

@app.route('/EPS_strategy')
def EPS_strategy():
    message = """<font face="微軟正黑體">
    <FONT SIZE=5><B>以連續n年EPS大於特定值作為基準，選出排名前段的股票</B></FONT><br/>
    注意:年度請挑2000-2016內任意年<br/>
    <br/>
    範例：選出2014年到2016年EPS大於2.5的公司<br/>
    輸入：/EPS_strategy/2014,2016,2.5/companyEPS<br/>
    </font>"""
    return message

@app.route('/EPS_strategy/<string:symbol>/companyEPS')
def companyEPS(symbol):
    varname = symbol
    startdate = varname.split(',')[0]
    enddate = varname.split(',')[1]
    standard = float(varname.split(',')[2])
    startdate = datetime.strptime(startdate,'%Y').year
    enddate = datetime.strptime(enddate,'%Y').year
    df = tool.EPSyaers3(startdate,enddate,standard)
    #df2 = df[['company']].to_string(header=False, index=False).replace('\n','.tw,')+".tw"
    #aa = type(df)
    message = """<font face="微軟正黑體">
    <FONT SIZE=5><U><B>Step2.回測</FONT></U></B><br/>
    回測方式：布林通道策略、RSI策略、均線策略、KD值策略、威廉指標策略<br/>
    請選擇回測方式、時間區間與前n名股票<br/>
    注意:回測時間最早只能從1993年開始<br/>
    <br/>
    1.布林通道策略範例：從2016年9月1號開始到2017年1月10號，選EPS排名前<B>5</B>檔，以<B>10</B>(平均10天)為中間基準，抓上下<B>3</B>個標準差的距離<br/>
      輸入：/EPS_strategy/2014,2016,2.5/companyEPS/EPS_BBands/2016-09-01,2017-01-10<B>+5+10+3</B><br/>
      <br/>
    2.RSI策略範例：從2016年9月1號開始到2017年1月10號，選EPS排名前<B>5</B>檔，當RSI跌破<B>20</B>時買進，大於<B>80</B>時賣出<br/>
      輸入：/EPS_strategy/2014,2016,2.5/companyEPS/EPS_RSI/2016-09-01,2017-01-10<B>+5+20+80</B><br/>
      <br/>
    3.均線策略範例：從2016年9月1號開始到2017年1月10號，選EPS排名前<B>5</B>檔，當股價突破<B>7</B>MA且7MA突破<B>35</B>MA時買進，跌破時賣出<br/>
      輸入：/EPS_strategy/2014,2016,2.5/companyEPS/EPS_MA/2016-09-01,2017-01-10<B>+5+7+35</B><br/>
      <br/>
    4.KD策略範例：從2016年9月1號開始到2017年1月10號，選EPS排名前<B>5</B>檔，當K由下穿越D且D值大於<B>60</B>時買進，K由上穿越D且D小於<B>40</B>時賣出<br/>
      輸入：/EPS_strategy/2014,2016,2.5/companyEPS/EPS_KD/2016-09-01,2017-01-10<B>+5+60+40</B><br/>
      <br/>
    5.威廉指標範例：從2016年9月1號開始到2017年1月10號，選EPS排名前<B>5</B>檔，當最近<B>7</B>日內W值突破<B>80</B>時買進，跌破<B>20</B>時賣出<br/>
      輸入：/EPS_strategy/2014,2016,2.5/companyEPS/EPS_william/2016-09-01,2017-01-10<B>+5+7+80+20</B><br/>
    <br/><br/>
    <FONT SIZE=5><U><B>EPS選股結果，依最新年份之EPS大到小排序</FONT></U></B>
    </font>"""
    #if aa == str:
        #df3 = df
    #else:
        #df3 = df.to_html() + message
    df3 = message + df.to_html()
    return df3

@app.route('/EPS_strategy/<string:symbol>/companyEPS/EPS_BBands/<string:test>')
def EPS_BBands(symbol,test):
    varname = symbol
    startdate = varname.split(',')[0]
    enddate = varname.split(',')[1]
    standard = float(varname.split(',')[2])
    startdate = datetime.strptime(startdate,'%Y').year
    enddate = datetime.strptime(enddate,'%Y').year
    df = tool.EPSyaers3(startdate,enddate,standard)
    df2 = df[['company']].to_string(header=False, index=False).replace('\n',',')
    varname2 = test
    testday = varname2.split('+')[0]
    test_star = testday.split(',')[0]
    test_end = testday.split(',')[1]
    stocknom = int(varname2.split('+')[1])
    timeperiod = int(varname2.split('+')[2])
    std = int(varname2.split('+')[3])
    stock = df2.split(',')[0:stocknom]
    results = []
    erstock = []
    erresult = []
    for n in range(0, len(stock)):
        try:
            df = web.DataReader(stock[n], 'yahoo', test_star, test_end)
            df = df.dropna()
            df = th.BBands_way(df,timeperiod,std)
            try:
                if np.all(df['signals']==0):
                    print("Stock:", stock[n], "策略沒有出現買賣訊號。")
                    continue
                SharpeRatio, maxdd, maxddd, finalRet = th.indicators(df)
                days = (df.index[-1] - df.index[0]).days
                results.append((SharpeRatio, maxdd, maxddd, finalRet, days, df[df['signals'] > 0]['signals'].sum(), stock[n]))
            except Exception as e:
                print("Error occurs at stock:", stock[n], "==>", e.args)
        except Exception as e_2:
            erstock = stock[n]+"下載股價資料出錯"
            erresult.append(erstock)
    results_df = pd.DataFrame(results, columns=['sharpe','MaxDrawDown','MaxDrawDownDuration','returns(%)',
                                            'days', 'entries','stock'])
    erresult2 = str(erresult)
    text1 = """<font face="微軟正黑體">
    <br/><br/><B>回測結果如上，歡迎回首頁重新選擇^^</B>
    </font>"""

    return results_df.to_html()+erresult2 + text1

@app.route('/EPS_strategy/<string:symbol>/companyEPS/EPS_KD/<string:test>')
def EPS_KD(symbol,test):
    varname = symbol
    startdate = varname.split(',')[0]
    enddate = varname.split(',')[1]
    standard = float(varname.split(',')[2])
    startdate = datetime.strptime(startdate,'%Y').year
    enddate = datetime.strptime(enddate,'%Y').year
    df = tool.EPSyaers3(startdate,enddate,standard)
    df2 = df[['company']].to_string(header=False, index=False).replace('\n',',')
    varname2 = test
    testday = varname2.split('+')[0]
    test_star = testday.split(',')[0]
    test_end = testday.split(',')[1]
    stocknom = int(varname2.split('+')[1])
    upbreak = int(varname2.split('+')[2])
    downbreak = int(varname2.split('+')[3])
    stock = df2.split(',')[0:stocknom]
    results = []
    erstock = []
    erresult = []
    for n in range(0, len(stock)):
        try:
            df = web.DataReader(stock[n], 'yahoo', test_star, test_end)
            df = df.dropna()
            df = th.KD_way(df,upbreak,downbreak)
            try:
                if np.all(df['signals']==0):
                    print("Stock:", stock[n], "策略沒有出現買賣訊號。")
                    continue
                SharpeRatio, maxdd, maxddd, finalRet = th.indicators(df)
                days = (df.index[-1] - df.index[0]).days
                results.append((SharpeRatio, maxdd, maxddd, finalRet, days, df[df['signals'] > 0]['signals'].sum(), stock[n]))
            except Exception as e:
                print("Error occurs at stock:", stock[n], "==>", e.args)
        except Exception as e_2:
            erstock = stock[n]+"下載股價資料出錯"
            erresult.append(erstock)
    results_df = pd.DataFrame(results, columns=['sharpe','MaxDrawDown','MaxDrawDownDuration','returns(%)',
                                            'days', 'entries','stock'])
    erresult2 = str(erresult)
    text1 = """<font face="微軟正黑體">
    <br/><br/><B>回測結果如上，歡迎回首頁重新選擇^^</B>
    </font>"""

    return results_df.to_html()+erresult2 + text1

@app.route('/EPS_strategy/<string:symbol>/companyEPS/EPS_william/<string:test>')
def EPS_william(symbol,test):
    varname = symbol
    startdate = varname.split(',')[0]
    enddate = varname.split(',')[1]
    standard = float(varname.split(',')[2])
    startdate = datetime.strptime(startdate,'%Y').year
    enddate = datetime.strptime(enddate,'%Y').year
    df = tool.EPSyaers3(startdate,enddate,standard)
    df2 = df[['company']].to_string(header=False, index=False).replace('\n',',')
    varname2 = test
    testday = varname2.split('+')[0]
    test_star = testday.split(',')[0]
    test_end = testday.split(',')[1]
    stocknom = int(varname2.split('+')[1])
    timeperiod = int(varname2.split('+')[2])
    oversold = int(varname2.split('+')[3])
    overbuy = int(varname2.split("+")[4])
    stock = df2.split(',')[0:stocknom]
    results = []
    erstock = []
    erresult = []
    for n in range(0, len(stock)):
        try:
            df = web.DataReader(stock[n], 'yahoo', test_star, test_end)
            df = df.dropna()
            df = th.william_way(df,upbreak,downbreak)
            try:
                if np.all(df['signals']==0):
                    print("Stock:", stock[n], "策略沒有出現買賣訊號。")
                    continue
                SharpeRatio, maxdd, maxddd, finalRet = th.indicators(df)
                days = (df.index[-1] - df.index[0]).days
                results.append((SharpeRatio, maxdd, maxddd, finalRet, days, df[df['signals'] > 0]['signals'].sum(), stock[n]))
            except Exception as e:
                print("Error occurs at stock:", stock[n], "==>", e.args)
        except Exception as e_2:
            erstock = stock[n]+"下載股價資料出錯"
            erresult.append(erstock)
    results_df = pd.DataFrame(results, columns=['sharpe','MaxDrawDown','MaxDrawDownDuration','returns(%)',
                                            'days', 'entries','stock'])
    erresult2 = str(erresult)
    text1 = """<font face="微軟正黑體">
    <br/><br/><B>回測結果如上，歡迎回首頁重新選擇^^</B>
    </font>"""

    return results_df.to_html()+erresult2 + text1

@app.route('/EPS_strategy/<string:symbol>/companyEPS/EPS_RSI/<string:test>')
def EPS_RSI(symbol,test):
    varname = symbol
    startdate = varname.split(',')[0]
    enddate = varname.split(',')[1]
    standard = float(varname.split(',')[2])
    startdate = datetime.strptime(startdate,'%Y').year
    enddate = datetime.strptime(enddate,'%Y').year
    df = tool.EPSyaers3(startdate,enddate,standard)
    df2 = df[['company']].to_string(header=False, index=False).replace('\n',',')
    varname2 = test
    testday = varname2.split('+')[0]
    test_star = testday.split(',')[0]
    test_end = testday.split(',')[1]
    stocknom = int(varname2.split('+')[1])
    LRSI = int(varname2.split('+')[2])
    HRSI = int(varname2.split('+')[3])
    stock = df2.split(',')[0:stocknom]
    results = []
    erstock = []
    erresult = []
    for n in range(0, len(stock)):
        try:
            df = web.DataReader(stock[n], 'yahoo', test_star, test_end)
            df = df.dropna()
            df = th.RSI_way(df,upbreak,downbreak)
            try:
                if np.all(df['signals']==0):
                    print("Stock:", stock[n], "策略沒有出現買賣訊號。")
                    continue
                SharpeRatio, maxdd, maxddd, finalRet = th.indicators(df)
                days = (df.index[-1] - df.index[0]).days
                results.append((SharpeRatio, maxdd, maxddd, finalRet, days, df[df['signals'] > 0]['signals'].sum(), stock[n]))
            except Exception as e:
                print("Error occurs at stock:", stock[n], "==>", e.args)
        except Exception as e_2:
            erstock = stock[n]+"下載股價資料出錯"
            erresult.append(erstock)
    results_df = pd.DataFrame(results, columns=['sharpe','MaxDrawDown','MaxDrawDownDuration','returns(%)',
                                            'days', 'entries','stock'])
    erresult2 = str(erresult)
    text1 = """<font face="微軟正黑體">
    <br/><br/><B>回測結果如上，歡迎回首頁重新選擇^^</B>
    </font>"""

    return results_df.to_html()+erresult2 + text1

@app.route('/EPS_strategy/<string:symbol>/companyEPS/EPS_MA/<string:test>')
def EPS_MA(symbol,test):
    varname = symbol
    startdate = varname.split(',')[0]
    enddate = varname.split(',')[1]
    standard = float(varname.split(',')[2])
    startdate = datetime.strptime(startdate,'%Y').year
    enddate = datetime.strptime(enddate,'%Y').year
    df = tool.EPSyaers3(startdate,enddate,standard)
    df2 = df[['company']].to_string(header=False, index=False).replace('\n',',')
    varname2 = test
    testday = varname2.split('+')[0]
    test_star = testday.split(',')[0]
    test_end = testday.split(',')[1]
    stocknom = int(varname2.split('+')[1])
    SMA = int(varname2.split('+')[2])
    LMA = int(varname2.split('+')[3])
    stock = df2.split(',')[0:stocknom]
    results = []
    erstock = []
    erresult = []
    for n in range(0, len(stock)):
        try:
            df = web.DataReader(stock[n], 'yahoo', test_star, test_end)
            df = df.dropna()
            df = th.MA_way(df,upbreak,downbreak)
            try:
                if np.all(df['signals']==0):
                    print("Stock:", stock[n], "策略沒有出現買賣訊號。")
                    continue
                SharpeRatio, maxdd, maxddd, finalRet = th.indicators(df)
                days = (df.index[-1] - df.index[0]).days
                results.append((SharpeRatio, maxdd, maxddd, finalRet, days, df[df['signals'] > 0]['signals'].sum(), stock[n]))
            except Exception as e:
                print("Error occurs at stock:", stock[n], "==>", e.args)
        except Exception as e_2:
            erstock = stock[n]+"下載股價資料出錯"
            erresult.append(erstock)
    results_df = pd.DataFrame(results, columns=['sharpe','MaxDrawDown','MaxDrawDownDuration','returns(%)',
                                            'days', 'entries','stock'])
    erresult2 = str(erresult)
    text1 = """<font face="微軟正黑體">
    <br/><br/><B>回測結果如上，歡迎回首頁重新選擇^^</B>
    </font>"""

    return results_df.to_html()+erresult2 + text1

@app.route('/Dob_strategy')
def Dob_strategy():
    message = """<font face="微軟正黑體">
    <FONT SIZE=5><B>以連續n年ROE與EPS大於特定值作為基準，選出排名前段的股票</B></FONT><br/>
    注意:年度請挑2000-2016內任意年<br/>
    <br/>
    範例1：選出2014年到2016年<FONT COLOR=#B87800>ROE大於2.5%</FONT>且<FONT COLOR=#00B8B8>EPS大於10</FONT>的公司，並以<FONT COLOR=#008F00>ROE</FONT>排序<br/>
    輸入：/Dob_strategy/2014,2016,<FONT COLOR=#B87800>2.5</FONT>,<FONT COLOR=#00B8B8>10</FONT>,<FONT COLOR=#008F00>ROE</FONT>/companyDob<br/>
    範例2：選出2014年到2016年<FONT COLOR=#B87800>ROE大於2.5%</FONT>且<FONT COLOR=#00B8B8>EPS大於10</FONT>的公司，並以<FONT COLOR=#008F00>EPS</FONT>排序<br/>
    輸入：/Dob_strategy/2014,2016,<FONT COLOR=#B87800>2.5</FONT>,<FONT COLOR=#00B8B8>10</FONT>,<FONT COLOR=#008F00>EPS</FONT>/companyDob<br/>
    </font>"""
    return message

@app.route('/Dob_strategy/<string:symbol>/companyDob')
def companyDob(symbol):
    varname = symbol
    startdate = varname.split(',')[0]
    enddate = varname.split(',')[1]
    ROEstandard = float(varname.split(',')[2])
    EPSstandard = float(varname.split(',')[3])
    sortway = varname.split(',')[4]
    startdate = datetime.strptime(startdate,'%Y').year
    enddate = datetime.strptime(enddate,'%Y').year
    df = tool.Dobyaers3(startdate,enddate,ROEstandard,EPSstandard)
    if sortway == "ROE":
        df = df.sort_values(by = str(enddate)+"ROE", ascending = False)
    else:
        df = df.sort_values(by = str(enddate)+"EPS", ascending = False)
    #df2 = df[['company']].to_string(header=False, index=False).replace('\n','.tw,')+".tw"
    #aa = type(df)
    message = """<font face="微軟正黑體">
    <FONT SIZE=5><U><B>Step2.回測</FONT></U></B><br/>
    回測方式：布林通道策略、RSI策略、均線策略、KD值策略、威廉指標策略<br/>
    請選擇回測方式、時間區間與前n名股票<br/>
    注意:回測時間最早只能從1993年開始<br/>
    <br/>
    1.布林通道策略範例：從2016年9月1號開始到2017年1月10號，以ROE(EPS)排序後選排名前<B>5</B>檔，以<B>MA10</B>(平均10天)為中間基準，抓上下<B>3</B>個標準差的距離<br/>
    輸入：/Dob_strategy/2014,2016,2.5,10,ROE(EPS)/companyDob/Dob_BBands/2016-09-01,2017-01-10<B>+5+10+3</B><br/>
    <br/>
    2.RSI策略範例：從2016年9月1號開始到2017年1月10號，以ROE(EPS)排序後選排名前<B>5</B>檔，當RSI跌破<B>20</B>時買進，大於<B>80</B>時賣出<br/>
    輸入：/Dob_strategy/2014,2016,2.5,10,ROE(EPS)/companyDob/Dob_RSI/2016-09-01,2017-01-10<B>+5+20+80</B><br/>
    <br/>
    3.均線策略範例：從2016年9月1號開始到2017年1月10號，以ROE(EPS)排序後選排名前<B>5</B>檔，當股價突破<B>7MA</B>且7MA突破<B>35MA</B>時買進，跌破時賣出<br/>
    輸入：/Dob_strategy/2014,2016,2.5,10,ROE(EPS)/companyDob/Dob_MA/2016-09-01,2017-01-10<B>+5+7+35</B><br/>
    <br/>
    4.威廉指標範例：從2016年9月1號開始到2017年1月10號，以ROE(EPS)排序後選排名前<B>5</B>檔，當最近<B>7</B>日內W值突破<B>80</B>時買進，跌破<B>20</B>時賣出<br/>
    輸入：/Dob_strategy/2014,2016,2.5,10,ROE(EPS)/companyDob/Dob_william/2016-09-01,2017-01-10<B>+5+7+80+20</B><br/>
    <br/>
    5.KD策略範例：從2016年9月1號開始到2017年1月10號，以ROE(EPS)排序後選排名前<B>5</B>檔，當K由下穿越D且D值大於<B>60</B>時買進，K由上穿越D且D小於<B>40</B>時賣出<br/>
    輸入：/Dob_strategy/2014,2016,2.5,10,ROE(EPS)/companyDob/Dob_KD/2016-09-01,2017-01-10<B>+5+60+40</B><br/>
    <br/><br/>
    <FONT SIZE=5><U><B>ROE&EPS選股結果，依大到小排序</FONT></U></B>
    </font>"""
    #if aa == str:
        #df3 = df
    #else:
        #df3 = df.to_html() + message
    df3 = message + df.to_html()
    return df3

@app.route('/Dob_strategy/<string:symbol>/companyDob/Dob_BBands/<string:test>')
def Dob_BBands(symbol,test):
    varname = symbol
    startdate = varname.split(',')[0]
    enddate = varname.split(',')[1]
    ROEstandard = float(varname.split(',')[2])
    EPSstandard = float(varname.split(',')[3])
    sortway = varname.split(',')[4]
    startdate = datetime.strptime(startdate,'%Y').year
    enddate = datetime.strptime(enddate,'%Y').year
    df = tool.Dobyaers3(startdate,enddate,ROEstandard,EPSstandard)
    if sortway == "ROE":
        df = df.sort_values(by = str(enddate)+"ROE", ascending = False)
    else:
        df = df.sort_values(by = str(enddate)+"EPS", ascending = False)
    dd2 = df[['company']].to_string(header=False, index=False).replace('\n',',')
    varname2 = test
    testday = varname2.split('+')[0]
    test_star = testday.split(',')[0]
    test_end = testday.split(',')[1]
    stocknom = int(varname2.split('+')[1])
    timeperiod = int(varname2.split('+')[2])
    std = int(varname2.split('+')[3])
    stock = dd2.split(',')[0:stocknom]
    results = []
    erstock = []
    erresult = []
    for n in range(0, len(stock)):
        try:
            df = web.DataReader(stock[n], 'yahoo', test_star, test_end)
            df = df.dropna()
            df = th.BBands_way(df,timeperiod,std)
            try:
                if np.all(df['signals']==0):
                    print("Stock:", stock[n], "策略沒有出現買賣訊號。")
                    continue
                SharpeRatio, maxdd, maxddd, finalRet = th.indicators(df)
                days = (df.index[-1] - df.index[0]).days
                results.append((SharpeRatio, maxdd, maxddd, finalRet, days, df[df['signals'] > 0]['signals'].sum(), stock[n]))
            except Exception as e:
                print("Error occurs at stock:", stock[n], "==>", e.args)
        except Exception as e_2:
            erstock = stock[n]+"下載股價資料出錯"
            erresult.append(erstock)
    results_df = pd.DataFrame(results, columns=['sharpe','MaxDrawDown','MaxDrawDownDuration','returns(%)',
                                            'days', 'entries','stock'])
    erresult2 = str(erresult)
    text1 = """<font face="微軟正黑體">
    <br/><br/><B>回測結果如上，歡迎回首頁重新選擇^^</B>
    </font>"""

    return results_df.to_html()+erresult2 + text1

@app.route('/Dob_strategy/<string:symbol>/companyDob/Dob_KD/<string:test>')
def Dob_KD(symbol,test):
    varname = symbol
    startdate = varname.split(',')[0]
    enddate = varname.split(',')[1]
    ROEstandard = float(varname.split(',')[2])
    EPSstandard = float(varname.split(',')[3])
    sortway = varname.split(',')[4]
    startdate = datetime.strptime(startdate,'%Y').year
    enddate = datetime.strptime(enddate,'%Y').year
    df = tool.Dobyaers3(startdate,enddate,ROEstandard,EPSstandard)
    if sortway == "ROE":
        df = df.sort_values(by = str(enddate)+"ROE", ascending = False)
    else:
        df = df.sort_values(by = str(enddate)+"EPS", ascending = False)
    dd2 = df[['company']].to_string(header=False, index=False).replace('\n',',')
    varname2 = test
    testday = varname2.split('+')[0]
    test_star = testday.split(',')[0]
    test_end = testday.split(',')[1]
    stocknom = int(varname2.split('+')[1])
    upbreak = int(varname2.split('+')[2])
    downbreak = int(varname2.split('+')[3])
    stock = dd2.split(',')[0:stocknom]
    results = []
    erstock = []
    erresult = []
    for n in range(0, len(stock)):
        try:
            df = web.DataReader(stock[n], 'yahoo', test_star, test_end)
            df = df.dropna()
            df = th.KD_way(df,upbreak,downbreak)
            try:
                if np.all(df['signals']==0):
                    print("Stock:", stock[n], "策略沒有出現買賣訊號。")
                    continue
                SharpeRatio, maxdd, maxddd, finalRet = th.indicators(df)
                days = (df.index[-1] - df.index[0]).days
                results.append((SharpeRatio, maxdd, maxddd, finalRet, days, df[df['signals'] > 0]['signals'].sum(), stock[n]))
            except Exception as e:
                print("Error occurs at stock:", stock[n], "==>", e.args)
        except Exception as e_2:
            erstock = stock[n]+"下載股價資料出錯"
            erresult.append(erstock)
    results_df = pd.DataFrame(results, columns=['sharpe','MaxDrawDown','MaxDrawDownDuration','returns(%)',
                                            'days', 'entries','stock'])
    erresult2 = str(erresult)
    text1 = """<font face="微軟正黑體">
    <br/><br/><B>回測結果如上，歡迎回首頁重新選擇^^</B>
    </font>"""

    return results_df.to_html()+erresult2 + text1

@app.route('/Dob_strategy/<string:symbol>/companyDob/Dob_william/<string:test>')
def Dob_william(symbol,test):
    varname = symbol
    startdate = varname.split(',')[0]
    enddate = varname.split(',')[1]
    ROEstandard = float(varname.split(',')[2])
    EPSstandard = float(varname.split(',')[3])
    sortway = varname.split(',')[4]
    startdate = datetime.strptime(startdate,'%Y').year
    enddate = datetime.strptime(enddate,'%Y').year
    df = tool.Dobyaers3(startdate,enddate,ROEstandard,EPSstandard)
    if sortway == "ROE":
        df = df.sort_values(by = str(enddate)+"ROE", ascending = False)
    else:
        df = df.sort_values(by = str(enddate)+"EPS", ascending = False)
    dd2 = df[['company']].to_string(header=False, index=False).replace('\n',',')
    varname2 = test
    testday = varname2.split('+')[0]
    test_star = testday.split(',')[0]
    test_end = testday.split(',')[1]
    stocknom = int(varname2.split('+')[1])
    timeperiod = int(varname2.split('+')[2])
    oversold = int(varname2.split('+')[3])
    overbuy = int(varname2.split("+")[4])
    stock = dd2.split(',')[0:stocknom]
    results = []
    erstock = []
    erresult = []
    for n in range(0, len(stock)):
        try:
            df = web.DataReader(stock[n], 'yahoo', test_star, test_end)
            df = df.dropna()
            df = th.william_way(df,upbreak,downbreak)
            try:
                if np.all(df['signals']==0):
                    print("Stock:", stock[n], "策略沒有出現買賣訊號。")
                    continue
                SharpeRatio, maxdd, maxddd, finalRet = th.indicators(df)
                days = (df.index[-1] - df.index[0]).days
                results.append((SharpeRatio, maxdd, maxddd, finalRet, days, df[df['signals'] > 0]['signals'].sum(), stock[n]))
            except Exception as e:
                print("Error occurs at stock:", stock[n], "==>", e.args)
        except Exception as e_2:
            erstock = stock[n]+"下載股價資料出錯"
            erresult.append(erstock)
    results_df = pd.DataFrame(results, columns=['sharpe','MaxDrawDown','MaxDrawDownDuration','returns(%)',
                                            'days', 'entries','stock'])
    erresult2 = str(erresult)
    text1 = """<font face="微軟正黑體">
    <br/><br/><B>回測結果如上，歡迎回首頁重新選擇^^</B>
    </font>"""

    return results_df.to_html()+erresult2 + text1

@app.route('/Dob_strategy/<string:symbol>/companyDob/Dob_RSI/<string:test>')
def Dob_RSI(symbol,test):
    varname = symbol
    startdate = varname.split(',')[0]
    enddate = varname.split(',')[1]
    ROEstandard = float(varname.split(',')[2])
    EPSstandard = float(varname.split(',')[3])
    sortway = varname.split(',')[4]
    startdate = datetime.strptime(startdate,'%Y').year
    enddate = datetime.strptime(enddate,'%Y').year
    df = tool.Dobyaers3(startdate,enddate,ROEstandard,EPSstandard)
    if sortway == "ROE":
        df = df.sort_values(by = str(enddate)+"ROE", ascending = False)
    else:
        df = df.sort_values(by = str(enddate)+"EPS", ascending = False)
    dd2 = df[['company']].to_string(header=False, index=False).replace('\n',',')
    varname2 = test
    testday = varname2.split('+')[0]
    test_star = testday.split(',')[0]
    test_end = testday.split(',')[1]
    stocknom = int(varname2.split('+')[1])
    LRSI = int(varname2.split('+')[2])
    HRSI = int(varname2.split('+')[3])
    stock = dd2.split(',')[0:stocknom]
    results = []
    erstock = []
    erresult = []
    for n in range(0, len(stock)):
        try:
            df = web.DataReader(stock[n], 'yahoo', test_star, test_end)
            df = df.dropna()
            df = th.RSI_way(df,upbreak,downbreak)
            try:
                if np.all(df['signals']==0):
                    print("Stock:", stock[n], "策略沒有出現買賣訊號。")
                    continue
                SharpeRatio, maxdd, maxddd, finalRet = th.indicators(df)
                days = (df.index[-1] - df.index[0]).days
                results.append((SharpeRatio, maxdd, maxddd, finalRet, days, df[df['signals'] > 0]['signals'].sum(), stock[n]))
            except Exception as e:
                print("Error occurs at stock:", stock[n], "==>", e.args)
        except Exception as e_2:
            erstock = stock[n]+"下載股價資料出錯"
            erresult.append(erstock)
    results_df = pd.DataFrame(results, columns=['sharpe','MaxDrawDown','MaxDrawDownDuration','returns(%)',
                                            'days', 'entries','stock'])
    erresult2 = str(erresult)
    text1 = """<font face="微軟正黑體">
    <br/><br/><B>回測結果如上，歡迎回首頁重新選擇^^</B>
    </font>"""

    return results_df.to_html()+erresult2 + text1

@app.route('/Dob_strategy/<string:symbol>/companyDob/Dob_MA/<string:test>')
def Dob_MA(symbol,test):
    varname = symbol
    startdate = varname.split(',')[0]
    enddate = varname.split(',')[1]
    ROEstandard = float(varname.split(',')[2])
    EPSstandard = float(varname.split(',')[3])
    sortway = varname.split(',')[4]
    startdate = datetime.strptime(startdate,'%Y').year
    enddate = datetime.strptime(enddate,'%Y').year
    df = tool.Dobyaers3(startdate,enddate,ROEstandard,EPSstandard)
    if sortway == "ROE":
        df = df.sort_values(by = str(enddate)+"ROE", ascending = False)
    else:
        df = df.sort_values(by = str(enddate)+"EPS", ascending = False)
    dd2 = df[['company']].to_string(header=False, index=False).replace('\n',',')
    varname2 = test
    testday = varname2.split('+')[0]
    test_star = testday.split(',')[0]
    test_end = testday.split(',')[1]
    stocknom = int(varname2.split('+')[1])
    SMA = int(varname2.split('+')[2])
    LMA = int(varname2.split('+')[3])
    stock = dd2.split(',')[0:stocknom]
    results = []
    erstock = []
    erresult = []
    for n in range(0, len(stock)):
        try:
            df = web.DataReader(stock[n], 'yahoo', test_star, test_end)
            df = df.dropna()
            df = th.MA_way(df,upbreak,downbreak)
            try:
                if np.all(df['signals']==0):
                    print("Stock:", stock[n], "策略沒有出現買賣訊號。")
                    continue
                SharpeRatio, maxdd, maxddd, finalRet = th.indicators(df)
                days = (df.index[-1] - df.index[0]).days
                results.append((SharpeRatio, maxdd, maxddd, finalRet, days, df[df['signals'] > 0]['signals'].sum(), stock[n]))
            except Exception as e:
                print("Error occurs at stock:", stock[n], "==>", e.args)
        except Exception as e_2:
            erstock = stock[n]+"下載股價資料出錯"
            erresult.append(erstock)
    results_df = pd.DataFrame(results, columns=['sharpe','MaxDrawDown','MaxDrawDownDuration','returns(%)',
                                            'days', 'entries','stock'])
    erresult2 = str(erresult)
    text1 = """<font face="微軟正黑體">
    <br/><br/><B>回測結果如上，歡迎回首頁重新選擇^^</B>
    </font>"""

    return results_df.to_html()+erresult2 + text1

if __name__=="__main__":
    app.run()
