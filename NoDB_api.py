"""
Set of apis to read the derails of DB.
"""

import BS_get_and_decode_webpage
import common_code

def getEPSG_NoDB(stockSymbol):
    print ("processing stock...", stockSymbol)
    BS_class = BS_get_and_decode_webpage.getData_bussinesStd(stockSymbol)
    report = BS_class.quaterlyUpdate(None)
    if report == False:
        print (stockSymbol + ' error fetching data')
    print ('Quaterly EPS Data: ' + report['reportType'])
    print("                      %15s%15s%15s%15s" % (report['Q1Name'], report['Q2Name'],
                                                      report['Q3Name'], report['Q4Name']))
    print("Current Year   :      %15s%15s%15s%15s" % (report['EPS_Q1'], report['EPS_Q2'],
                                                    report['EPS_Q3'], report['EPS_Q4'],))
    
    print("Previous Year  :      %15s%15s%15s%15s" % (report['EPS_Q1YoY'], report['EPS_Q2YoY'],
                                                     report['EPS_Q3YoY'], report['EPS_Q4YoY']))

    print("Change percent :      %15d%15d%15d%15d" % (report['EPSQ1Change'], report['EPSQ2Change'],
                                                      report['EPSQ3Change'], report['EPSQ4Change']))
                                                                                                          
    onGoingAnnualEPS = float(report['EPS_Q1']) + float(report['EPS_Q2']) +\
                           float(report['EPS_Q3']) +  float(report['EPS_Q4'])
    print("On going Annual EPS: %0.2f" % (onGoingAnnualEPS))
    report.clear()
    
    report = BS_class.yearlyUpdate(None)
    if report == False:
        print (stockSymbol + ' error fetching data')
            
    print ('Annual EPS Data: '+ report['reportType']);

    print("                      %15s%15s%15s%15s" % (report['Y1Name'], report['Y2Name'],
                                                      report['Y3Name'], report['Y4Name']))
                                               
    print("EPS Data       :      %15s%15s%15s%15s" % (report['Y1EPS'], report['Y2EPS'],
                                                      report['Y3EPS'], report['Y4EPS']))
    print("Change percent :      %15d%15d%15d" %(report['EPSY1Change'], report['EPSY2Change'],
                                                 report['EPSY3Change']))
    
    report.clear()


def getRatios(stockSymbol):
    cf = BS_json_extract.compFormat_bussinesStd(stockSymbol)
    cf.get_compFormat()
    if cf.result == 'NODATA':
        print ('No Data for: ' + stockSymbol)
        del cf
        return False

    report = BS_get_and_decode_webpage.getData_bussinesStd(cf.result, stockSymbol)
    if report.getRatios() == False:
        print (stockSymbol + ' error fetching data')
        del cf
    #del cf, report

def getAllNoDB(stockSymbol):
    print("=============================")
    getEPSG_NoDB(stockSymbol)
    print("=============================")
    getRatios_NoDB(stockSymbol)
    print("=============================")