"""
Set of apis to read the derails of DB.
"""

import BS_get_and_decode_webpage

def getEPSG_NoDB(stockSymbol):
    print ("processing stock...", stockSymbol)
    BS_class = BS_get_and_decode_webpage.getData_bussinesStd(stockSymbol)
    report = BS_class.fetchQtrlyEPS(updateDB=False)
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
    
    report = BS_class.fetchYearlyEPS(updateDB=False)
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
    del BS_class

def getPH_NoDB(stockSymbol):
    BS = BS_get_and_decode_webpage.getData_bussinesStd(stockSymbol)
    BS.getPromotorHoldings()
    
    print("in percent                %s\t%s\t%s\t%s\t%s" % (BS.result_dict['PHQuater1'], BS.result_dict['PHQuater2'],\
                            BS.result_dict['PHQuater3'], BS.result_dict['PHQuater4'], BS.result_dict['PHQuater5'] ))

    print("Tot PH                  : %s\t\t%s\t\t%s\t\t%s\t\t%s" % (BS.result_dict['totalPromoterQ1'], BS.result_dict['totalPromoterQ2'],\
                BS.result_dict['totalPromoterQ3'], BS.result_dict['totalPromoterQ4'] ,BS.result_dict['totalPromoterQ5']))
    print("Tot Institutions        : %s\t\t%s\t\t%s\t\t%s\t\t%s" % (BS.result_dict['totalInstitQ1'], BS.result_dict['totalInstitQ2'],\
            BS.result_dict['totalInstitQ3'], BS.result_dict['totalInstitQ4'], BS.result_dict['totalInstitQ5']))
    print("Financial Institutions  : %s\t\t%s\t\t%s\t\t%s\t\t%s\n" % (BS.result_dict['FinInstitQ1'],  BS.result_dict['FinInstitQ2'],
            BS.result_dict['FinInstitQ3'], BS.result_dict['FinInstitQ4'], BS.result_dict['FinInstitQ4']))
    print("FII                     : %s\t\t%s\t\t%s\t\t%s\t\t%s" % (BS.result_dict['FIIQ1'], BS.result_dict['FIIQ2'],\
            BS.result_dict['FIIQ3'], BS.result_dict['FIIQ4'],BS.result_dict['FIIQ5']))
    print("Mutal Funds             : %s\t\t%s\t\t%s\t\t%s\t\t%s" % (BS.result_dict['MFQ1'], BS.result_dict['MFQ2'],\
            BS.result_dict['MFQ3'], BS.result_dict['MFQ4'], BS.result_dict['MFQ5']))
    del BS

def getRatios_NoDB(stockSymbol):
    BS = BS_get_and_decode_webpage.getData_bussinesStd(stockSymbol)
    if BS.getRatios() == False:
        print (stockSymbol + ' error fetching ratios')
        del BS
    
    print("Ratios                \t%s\t%s\t%s" % (BS.result_dict['RatioYearName1'], BS.result_dict['RatioYearName2'], BS.result_dict['RatioYearName3']))
    print("Return On Net Worth : \t%s\t%s\t%s" % (BS.result_dict['RONWyear1'], BS.result_dict['RONWyear2'], BS.result_dict['RONWyear3']))
    print("Interest Coverage   : \t%s\t%s\t%s" % (BS.result_dict['ICyear1'], BS.result_dict['ICyear2'], BS.result_dict['ICyear3'] ))
    print("Debt-Equity         : \t%s\t%s\t%s" % (BS.result_dict['DEyear1'], BS.result_dict['DEyear2'], BS.result_dict['DEyear3']))
    del BS

def getCashFlow_NoDB(stockSymbol):
    BS = BS_get_and_decode_webpage.getData_bussinesStd(stockSymbol)
    if BS.getCashFlowData() == False:
        print (stockSymbol + ' error fetching cash flow')
        del BS
        
    print ('Cash Flow from Operations: ' )
    print("Year:     %15s\t%15s\t%15s" % (BS.result_dict['CFYearName1'], BS.result_dict['CFYearName2'], BS.result_dict['CFYearName3']))
    print("in Crs:   %15s\t%15s\t%15s" % (BS.result_dict['CFYear1'], BS.result_dict['CFYear2'], BS.result_dict['CFYear3']))
  
def getAllNoDB(stockSymbol):
    print("=============================")
    getEPSG_NoDB(stockSymbol)
    print("=============================")
    getPH_NoDB(stockSymbol)
    print("=============================")
    getRatios_NoDB(stockSymbol)
    print("=============================")
    getCashFlow_NoDB(stockSymbol)
    print("=============================")