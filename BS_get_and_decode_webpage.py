import re
from urllib.request import urlopen
import sqlite3
import common_code
import time
import BS_json_extract

def myUrlopen(link):
    try:
        source = urlopen(link).read()
        common_code.webPageAcessed +=1
        if common_code.webPageAcessed % 10 == 0:
            print ('web page access count = ', common_code.webPageAcessed)
    except:
        #Sometime server might ot respond, try once again
        print ('open failed. try again after 30 seconds: ')
        time.sleep(30)
        print ('reading after 30 seconds sleep')
        source = urlopen(link).read()
        common_code.webPageAcessed +=1
    return source.decode()

def getStockLinkId(stockSymbol):
    cf = BS_json_extract.compFormat_bussinesStd(stockSymbol)
    cf.get_compFormat()
    if cf.result == 'NODATA':
        print ('No Data for: ' + stockSymbol)
        cf.result = cf.compFormatFailed(stockSymbol)
        if cf.result == False:
            del cf
            return False
    return cf

class getData_bussinesStd(object):
    def __init__(self, stockSymbol):
        cf = getStockLinkId(stockSymbol);
        if cf == False:
            return False
        self.linkId = cf.result
        self.stockSymbol = stockSymbol
        stockLinkId = cf.result
        self.sqlite_file = common_code.sqliteFile
        self.latestQtrName = common_code.current_qtr
        self.cashFlow_link = 'http://www.business-standard.com/company/'+stockLinkId+'/cash-flow/1/'
        self.result_dict = {}
        self.ratio_link = 'http://www.business-standard.com/company/'+stockLinkId+'/financials-ratios/1/'
        
        self.EPS_Quaterly_1 = {}
        self.EPS_Quaterly_1['Standalone'] = 'http://www.business-standard.com/company/'+stockLinkId+'/financials-quaterly/1/'
        self.EPS_Quaterly_1['Consolidated'] = 'http://www.business-standard.com/company/'+stockLinkId+'/financials-quaterly/1/Consolidated'
        
        self.EPS_Quaterly_2 = {}
        self.EPS_Quaterly_2['Standalone'] = 'http://www.business-standard.com/company/'+stockLinkId+'/financials-quaterly/2/'
        self.EPS_Quaterly_2['Consolidated'] = 'http://www.business-standard.com/company/'+stockLinkId+'/financials-quaterly/2/Consolidated'
        
        self.finacialOverview_link = {}
        self.finacialOverview_link['Standalone'] = 'http://www.business-standard.com/company/'+stockLinkId+'/financials-overview/'
        self.finacialOverview_link['Consolidated'] = 'http://www.business-standard.com/company/'+stockLinkId+'/financials-overview/1/Consolidated'
        
        self.finacialOverview_link1 = {}
        self.finacialOverview_link1['Standalone'] = 'http://www.business-standard.com/company/'+stockLinkId+'/financials-overview/2/'
        self.finacialOverview_link1['Consolidated'] = 'http://www.business-standard.com/company/'+stockLinkId+'/financials-overview/2/Consolidated'
        
        self.finacialPL_link = {}
        self.finacialPL_link['Standalone'] = 'http://www.business-standard.com/company/'+stockLinkId+'/financials-profit-loss/'
        self.finacialPL_link['Consolidated'] = 'http://www.business-standard.com/company/'+stockLinkId+'/financials-profit-loss/1/Consolidated'
        
        self.finacialPL_link1 = {}
        self.finacialPL_link1['Standalone'] = 'http://www.business-standard.com/company/'+stockLinkId+'/financials-profit-loss/2/'
        self.finacialPL_link1['Consolidated'] = 'http://www.business-standard.com/company/'+stockLinkId+'/financials-profit-loss/2/Consolidated'
        
        self.balance_sheet_link = {}
        self.balance_sheet_link['Standalone'] = 'http://www.business-standard.com/company/'+stockLinkId+'/financials-balance-sheet/'
        self.balance_sheet_link['Consolidated'] = 'http://www.business-standard.com/company/'+stockLinkId+'/financials-balance-sheet/1/Consolidated'
        
        self.summary_link = 'http://www.business-standard.com/company/'+stockLinkId
        # promotor holding link has only compId, no compFormat
        compId = re.findall('\d+', stockLinkId)
        self.promotorLink = 'http://www.business-standard.com/stocks/share-holding-pattern/'+str(int(compId[0]))

        """
        Lets not bombard the free websites with requestes. Sleep 1 seconds after
        each query.
        """
        common_code.mySleep(1)
        del cf
        
#    result = self.splitString(sourceCode, 'EPS (Rs)</td>', '<td class="">', '</td>', 2, 4)
    """
    Function always return expectednoItems, if there are less items than requested, function 
    fill them with zeros.
    """
    def splitString(self, source, string1, string2, string3, firstElement, expectedNoItems):
        success = 1
        #output = 'error output'
        noItemsPresent = len(source.split(string1)[1].split(string2))
        #substract one coloumn of item headers
        noItemsPresent -= 1
        noItems = min(noItemsPresent, expectedNoItems)
        output = []

        """
        Fill zeros to avoid errors during unpack
        """        
        for counter in range(0, expectedNoItems):
            output.append(0)
            
        try:
            for counter in range(firstElement, noItemsPresent + 1):
                #print 'output[] =', counter, counter-firstElement
                if (counter - firstElement) >= expectedNoItems :
                    break
                output[counter-firstElement] = (source.split(string1)[1].split(string2)[counter].split(string3)[0])
                        
        except:
            print ("exception in splitString when looking for", string1)
            success = 0
            output[0] = 'error output'
            
        return {'success':success, 'output':output, 'itemsReturned':noItems }

    def yearlyUpdate(self, updateDB=1):
        
        """
        We need matching data. ie. if quaterly data is standalone, we dont need to try consolidated here
        """
        if self.qtr_reportType == 'Consolidated':
            """
            This try-except loop is to figure out the reportType(conslidate/standalone)
            """
            try:
                reportType = 'Consolidated'
                self.balanceSheet_source = myUrlopen(self.balance_sheet_link[reportType])                        
                """
                We can't use splitString. We have to get exception here to switch to standalone
                """
                currentLiabilites = self.balanceSheet_source.split('Current Liabilities</td>')[1].split('<td class="">')[1].split('</td>')[0]            
            except:
                print ("exception in consolidated")
                reportType = 'Standalone'
                self.balanceSheet_source = myUrlopen(self.balance_sheet_link[reportType])
                currentLiabilites = self.balanceSheet_source.split('Current Liabilities</td>')[1].split('<td class="">')[1].split('</td>')[0]
        else:
            print ("we directly moving to standalone in yearly")
            reportType = 'Standalone'
            self.balanceSheet_source = myUrlopen(self.balance_sheet_link[reportType])
            currentLiabilites = self.balanceSheet_source.split('Current Liabilities</td>')[1].split('<td class="">')[1].split('</td>')[0]
            
        print ("report type: ", reportType)
        """
        Some stocks Anuual EPS is listed in finacial overview link, for other
        it is listed in P&L link. To solve this we need the below try except,
        """
        try:
            self.finacialOverview_source = myUrlopen(self.finacialOverview_link[reportType])
            result = self.splitString(self.finacialOverview_source, 'Earning Per Share (Rs)</td>', '<td class="">', '</td>', 1, 3)
            Y1EPS, Y2EPS, Y3EPS = result['output']            
            
            result = self.splitString(self.finacialOverview_source, 'Particulars ', '<td class="tdh">', '</td>', 1, 3)
            Y1Name, Y2Name, Y3Name = result['output']
            
            self.finacialOverview_source1 = myUrlopen(self.finacialOverview_link1[reportType])
            result = self.splitString(self.finacialOverview_source1, 'Earning Per Share (Rs)</td>', '<td class="">', '</td>', 1, 1)
            Y4EPS = result['output'][0]      
            
            result = self.splitString(self.finacialOverview_source1, 'Particulars ',  '<td class="tdh">', '</td>', 1, 1)
            Y4Name = result['output'][0]
            finacialPL_src_buffered = 0
        except :
            print ('failed when spliting finacialoverview link trying finacialPL link')
            self.finacialPL_source = myUrlopen(self.finacialPL_link[reportType])
            result = self.splitString(self.finacialPL_source, '<td class="tdL" colspan="0">Earning Per Share (Rs.)</td>',
                                     '<td class="amount">', '</td>', 1, 3)
            Y1EPS, Y2EPS, Y3EPS = result['output']
            
            result = self.splitString(self.finacialPL_source, 'Figures in Rs crore</td>', '<td class="tdh">' ,'</td>', 1, 3)
            Y1Name, Y2Name, Y3Name = result['output']
            
            self.finacialPL_source1 = myUrlopen(self.finacialPL_link1[reportType])
            result = self.splitString(self.finacialPL_source1, '<td class="tdL" colspan="0">Earning Per Share (Rs.)</td>', 
                                        '<td class="amount">', '</td>', 1, 1)
            Y4EPS = result['output'][0]
            result = self.splitString(self.finacialPL_source1, 'Figures in Rs crore</td>', '<td class="tdh">', '</td>', 1, 1 )
            Y4Name = result['output'][0]                
            print ('second link succesfull')
            finacialPL_src_buffered = 1

        result = self.splitString(self.balanceSheet_source, 'Total Assets</b></td>', '<td class="">', '</td>', 1, 1 )
        totalAssets = result['output'][0]
        
        result = self.splitString(self.balanceSheet_source, 'Total Debt</td>', '<td class="">', '</td>', 1, 1)
        totalDebt = result['output'][0]
        
        """
        As per the program flow, finacialPL_src is buffered for finacial stocks.
        These finacial stocks has operating profit represented in different way. Handling this seperatly
        """
        if finacialPL_src_buffered == 0:
            self.finacialPL_source = myUrlopen(self.finacialPL_link[reportType])
            result = self.splitString(self.finacialPL_source, 'Operating Profit</b></td>', '<td class="">', '</td>', 1, 1)
            operatingProfit = result['output'][0]
        else :
            result = self.splitString(self.finacialPL_source, '<td class="tdL" colspan="0">Total</td>', '<td class="amount">', '</td>', 1, 1)
            operatingProfit = result['output'][0]
            print ("operatingProfit ", operatingProfit)
        
        result = self.splitString(self.finacialPL_source, 'Figures in Rs crore</td>', '<td class="tdh">', '</td>', 1, 1)
        currentYear = result['output'][0]
        
        self.summary_source = myUrlopen(self.summary_link)
        result = self.splitString(self.summary_source, 'Market Cap </td>', '<td class="bL1 tdR">', '</td>', 1, 1)
        marketCap = result['output'][0]
        marketCap = marketCap.replace(",", "")
        

        RoC = float(operatingProfit)/(float(totalAssets) - float(currentLiabilites))
        RoC *=100 #convert to percentage
        
        enterpriseValue = float(marketCap) + float(totalDebt)
        earningsYield = float(operatingProfit)/enterpriseValue*100
            
        print (Y1Name, Y2Name, Y3Name, Y4Name)
        print (Y1EPS, Y2EPS, Y3EPS, Y4EPS)
        """ We make all 0 denomenators to 0.1 to avoid divide by zero
        """
        Y2EPS = 0.1 if float(Y2EPS) == 0.00 else Y2EPS
        Y3EPS = 0.1 if float(Y3EPS) == 0.00 else Y3EPS
        Y4EPS = 0.1 if float(Y4EPS) == 0.00 else Y4EPS

        EPSY1Change = ((float(Y1EPS) - float(Y2EPS))/float(Y2EPS))*100
        EPSY2Change = ((float(Y2EPS) - float(Y3EPS))/float(Y3EPS))*100            
        EPSY3Change = ((float(Y3EPS) - float(Y4EPS))/float(Y4EPS))*100

        if (updateDB):
            print("updateDB...............")   
            updateStockDetails_to_Sqlite(self.sqliteFile, self.stockSymbol, False)
     
        else:
            d = dict(symbol = self.stockSymbol,
                    Y1EPS = Y1EPS, Y2EPS = Y2EPS, Y3EPS = Y3EPS, Y4EPS = Y4EPS,
                    Y1Name = Y1Name, Y2Name = Y2Name, Y3Name = Y3Name, Y4Name = Y4Name,
                    EPSY1Change = EPSY1Change, EPSY2Change = EPSY2Change, EPSY3Change = EPSY3Change,
                    operatingProfit = operatingProfit, totalAssets = totalAssets, currentLiabilites = currentLiabilites, marketCap = marketCap,
                    totalDebt = totalAssets, currentYear = currentYear, earningsYield = float("{0:.2f}".format(earningsYield)),
                    RoC = float("{0:.2f}".format(RoC)), reportType = reportType)
            return d
                
    def quaterlyUpdate(self, updateDB=1):
        try:
            """ Lets start with consolidated and fallback to standalone if not available"""
            reportType = 'Consolidated'
            self.Quaterly_1_Source = myUrlopen(self.EPS_Quaterly_1[reportType])
            """ Try to decipher the report, if there is exception we have to try standalone"""
            result = self.splitString(self.Quaterly_1_Source, 'Figures in Rs crore</td>', '<td class="tdh">', '</td>', 1, 4)
            Q1Name, Q2Name, Q3Name, Q4Name = result['output']
            """ Sometimes consolidated data is present but not updated, in such scenarios
                we have to use standalone data
            """
            if Q1Name !=common_code.current_qtr and Q1Name != common_code.previous_qtr:
                print (self.stockSymbol, " -- consolidated data is not updated. trying standalone by raising an exception")
                raise
        except Exception:
            reportType = 'Standalone'
            self.Quaterly_1_Source = myUrlopen(self.EPS_Quaterly_1[reportType])
            result = self.splitString(self.Quaterly_1_Source, 'Figures in Rs crore</td>', '<td class="tdh">', '</td>', 1, 4)
            print(result['output'])
            Q1Name, Q2Name, Q3Name, Q4Name = result['output']
            
        print ("Report Type: ", reportType)
        self.qtr_reportType = reportType
        
        """ Do not proceed if latest qtr data is not any of (current or previous qtr) """
        if Q1Name != common_code.current_qtr and Q1Name != common_code.previous_qtr:
            print("Q1Name = ", Q1Name, common_code.current_qtr, common_code.previous_qtr)
            print ("Quite old data in server ", Q1Name)
            return False

        result = self.splitString(self.Quaterly_1_Source, 'EPS (Rs)</td>', '<td class="">', '</td>', 1, 5)
        Q1, Q2, Q3, Q4, Q1YoY = result['output']
        
        self.Quaterly_2_Source = myUrlopen(self.EPS_Quaterly_2[reportType])
        result = self.splitString(self.Quaterly_2_Source, 'EPS (Rs)</td>', '<td class="">', '</td>', 1, 3)            
        Q2YoY, Q3YoY, Q4YoY = result['output']                        
 
        result = self.splitString(self.Quaterly_1_Source, 'Operating Profit</td>', '<td class="">', '</td>', 1, 4)
        EBIT_Q1, EBIT_Q2, EBIT_Q3, EBIT_Q4 = result['output']
        
        """ We make all denomiaor 0 to 0.1 to avoid divison by zero
        """
        Q1YoY = float(Q1YoY)
        Q2YoY = float(Q2YoY)
        Q3YoY = float(Q3YoY)
        Q4YoY = float(Q4YoY)

        Q1YoY = 0.1 if Q1YoY == 0.00 else Q1YoY
        Q2YoY = 0.1 if Q2YoY == 0.00 else Q2YoY
        Q3YoY = 0.1 if Q3YoY == 0.00 else Q3YoY
        Q4YoY = 0.1 if Q4YoY == 0.00 else Q4YoY
    
        EPSQ1Change = (float(Q1) - Q1YoY)/Q1YoY*100
        EPSQ2Change = (float(Q2) - Q2YoY)/Q2YoY*100
        EPSQ3Change = (float(Q3) - Q3YoY)/Q3YoY*100
        EPSQ4Change = (float(Q4) - Q4YoY)/Q4YoY*100

        if (updateDB):
            print("updateDB...............")
            updateStockDetails_to_Sqlite(self.sqliteFile, self.stockSymbol, True)            
            return True
        else:
            
            d = dict(symbol = self.stockSymbol,\
                    EPS_Q1 = Q1, EPS_Q2 = Q2, EPS_Q3 = Q3, EPS_Q4 = Q4,\
                    EPS_Q1YoY = Q1YoY, EPS_Q2YoY = Q2YoY, EPS_Q3YoY = Q3YoY, EPS_Q4YoY = Q4YoY, \
                    Q1Name = Q1Name, Q2Name = Q2Name, Q3Name = Q3Name, Q4Name = Q4Name,\
                    EPSQ1Change = EPSQ1Change, EPSQ2Change = EPSQ2Change, EPSQ3Change = EPSQ3Change, EPSQ4Change = EPSQ4Change,\
                    EBIT_Q1 = EBIT_Q1, EBIT_Q2 = EBIT_Q2, EBIT_Q3 = EBIT_Q4, reportType = reportType)
            return d

        return False
    def updateCompleteDataBase(self):
        update_quaterly = 1
        update_yearly = 1
        try:
            qtr_row = readStockDetails_from_Sqlite(self.sqlite_file, self.stockSymbol, True);
            yearly_row = readStockDetails_from_Sqlite(self.sqlite_file, self.stockSymbol, False);
            """ if data is uptodate return """
            if qtr_row!=None and yearly_row!=None and \
                common_code.current_year == yearly_row[common_code.YearlyIndex_Y1Name] and\
                common_code.current_qtr == qtr_row[common_code.QuaterlyIndex_Q1Name]:
                return
            if common_code.current_qtr == qtr_row[common_code.QuaterlyIndex_Q1Name]:
                update_quaterly = 0
                self.qtr_reportType = qtr_row[common_code.QuaterlyIndex_reportType]
            if common_code.current_year == yearly_row[common_code.YearlyIndex_Y1Name]:
                update_yearly = 0
        except :
            print ("Exception updateCompleteDataBase. May be you want to fix this.")
            
        """ proceed with update """
        if update_quaterly == 1:
            print ("call quaterlyUpdate ....")
            if self.quaterlyUpdate() == False:
                return False
        if update_yearly == 1:
            print ("call yearly Update....")
            self.yearlyUpdate()
           
    def getPromotorHoldings(self):
        try:
            source = myUrlopen(self.promotorLink)
            result = self.splitString(source, '(in %)</td>', '<td class="tdh">', '</td>', 1, 5)
            self.result_dict['PHQuater1'], self.result_dict['PHQuater2'], self.result_dict['PHQuater3'],\
            self.result_dict['PHQuater4'], self.result_dict['PHQuater5'] = result['output']

            result = self.splitString(source, 'Total of Promoters', '<td class="">', '</td>', 1, 5 )
            self.result_dict['totalPromoterQ1'], self.result_dict['totalPromoterQ2'], self.result_dict['totalPromoterQ3'],\
            self.result_dict['totalPromoterQ4'] ,self.result_dict['totalPromoterQ5'] = result['output']

            result = self.splitString(source, '<strong>Institutions</strong>', '<td class="">', '</td>', 1, 5 )
            self.result_dict['totalInstitQ1'], self.result_dict['totalInstitQ2'], self.result_dict['totalInstitQ3'],\
            self.result_dict['totalInstitQ4'], self.result_dict['totalInstitQ5'] = result['output']

            result = self.splitString(source, 'Foreign Institutional Investors</td>', '<td class="">', '</td>', 1, 5 )
            self.result_dict['FIIQ1'], self.result_dict['FIIQ2'], self.result_dict['FIIQ3'], self.result_dict['FIIQ4'],\
            self.result_dict['FIIQ5'] = result['output']

            result = self.splitString(source, 'Financial Institutions / Banks</td>', '<td class="">', '</td>', 1, 5 )
            self.result_dict['FinInstitQ1'],  self.result_dict['FinInstitQ2'], self.result_dict['FinInstitQ3'],\
            self.result_dict['FinInstitQ4'], self.result_dict['FinInstitQ4'] = result['output']

            result = self.splitString(source, 'Mutual  Funds / UTI</td', '<td class="">', '</td>', 1, 5 )
            self.result_dict['MFQ1'], self.result_dict['MFQ2'], self.result_dict['MFQ3'], self.result_dict['MFQ4'],\
            self.result_dict['MFQ5'] = result['output']

            print("in percent                %s\t%s\t%s\t%s\t%s" % (self.result_dict['PHQuater1'], self.result_dict['PHQuater2'],\
            self.result_dict['PHQuater3'], self.result_dict['PHQuater4'], self.result_dict['PHQuater5'] ))
            print("Tot PH                  : %s\t\t%s\t\t%s\t\t%s\t\t%s" % (self.result_dict['totalPromoterQ1'], self.result_dict['totalPromoterQ2'],\
            self.result_dict['totalPromoterQ3'], self.result_dict['totalPromoterQ4'] ,self.result_dict['totalPromoterQ5']))
            print("Tot Institutions        : %s\t\t%s\t\t%s\t\t%s\t\t%s" % (self.result_dict['totalInstitQ1'], self.result_dict['totalInstitQ2'],\
            self.result_dict['totalInstitQ3'], self.result_dict['totalInstitQ4'], self.result_dict['totalInstitQ5']))
            print("Financial Institutions  : %s\t\t%s\t\t%s\t\t%s\t\t%s\n" % (self.result_dict['FinInstitQ1'],  self.result_dict['FinInstitQ2'],
            self.result_dict['FinInstitQ3'], self.result_dict['FinInstitQ4'], self.result_dict['FinInstitQ4']))
            print("FII                     : %s\t\t%s\t\t%s\t\t%s\t\t%s" % (self.result_dict['FIIQ1'], self.result_dict['FIIQ2'],\
            self.result_dict['FIIQ3'], self.result_dict['FIIQ4'],self.result_dict['FIIQ5']))
            print("Mutal Funds             : %s\t\t%s\t\t%s\t\t%s\t\t%s" % (self.result_dict['MFQ1'], self.result_dict['MFQ2'],\
            self.result_dict['MFQ3'], self.result_dict['MFQ4'], self.result_dict['MFQ5']))
            return True

        except :
            print ('faild in getPromotorHoldings loop')
            return False

    def getCashFlowData(self):
        try:
            cashFlow_source = myUrlopen(self.cashFlow_link)
            string = 'Net Cash From Operating Activities</td>'
            CFyear1 = cashFlow_source.split(string)[1].split('<td class="">')[1].split('</td>')[0]
            CFyear2 = cashFlow_source.split(string)[1].split('<td class="">')[2].split('</td>')[0]
            CFyear3 = cashFlow_source.split(string)[1].split('<td class="">')[3].split('</td>')[0]

            string = 'Figures in Rs crore</td>'
            firstYear = cashFlow_source.split(string)[1].split('<td class="tdh">')[1].split('</td>')[0]
            secondYear = cashFlow_source.split(string)[1].split('<td class="tdh">')[2].split('</td>')[0]
            thirdYear = cashFlow_source.split(string)[1].split('<td class="tdh">')[3].split('</td>')[0]

            print ('Cash Flow from Operations: ' + self.reportType)
            print("          %s\t%s\t%s" % (firstYear, secondYear, thirdYear))
            print("in Crs:   %s\t%s\t%s" % (CFyear1, CFyear2, CFyear3))

            self.result_dict['CFYearName1'] = firstYear
            self.result_dict['CFYearName2'] = secondYear
            self.result_dict['CFYearName3'] = thirdYear
            self.result_dict['CFYear1'] = float(CFyear1)
            self.result_dict['CFYear2'] = float(CFyear2)
            self.result_dict['CFYear3'] = float(CFyear3)

        except :
            print ('faild in getCashFlowData loop')
            return False        

    def getRatios(self):
        try:
            ratioSource = myUrlopen(self.ratio_link)
            result = self.splitString(ratioSource, 'Return on Net Worth (%)</td>', '<td class="">' ,'</td>', 1, 3)
            returnOnNetWorth_year1, returnOnNetWorth_year2, returnOnNetWorth_year3 = result['output']

            result = self.splitString(ratioSource, '<td class="tdh tdC">Ratios</td>', '<td class="tdh">' ,'</td>', 1, 3)
            year1, year2, year3 = result['output']

            result = self.splitString(ratioSource, 'Debt-Equity Ratio</td>', '<td class="">' ,'</td>', 1, 3)
            debtToEquity_year1, debtToEquity_year2, debtToEquity_year3 = result['output']

            result = self.splitString(ratioSource, 'Interest Coverage ratio</td>', '<td class="">' ,'</td>', 1, 3)
            interestCoverage_year1, interestCoverage_year2, interestCoverage_year3 = result['output']

            print("Ratios                \t%s\t%s\t%s" % (year1, year2, year3))
            print("Return On Net Worth : \t%s\t%s\t%s" % (returnOnNetWorth_year1, returnOnNetWorth_year2, returnOnNetWorth_year3))
            print("Interest Coverage   : \t%s\t%s\t%s" % (interestCoverage_year1, interestCoverage_year2, interestCoverage_year3 ))
            print("Debt-Equity         : \t%s\t%s\t%s" % (debtToEquity_year1, debtToEquity_year2, debtToEquity_year3))

            self.result_dict['RatioYearName1'] = year1
            self.result_dict['RatioYearName2'] = year2
            self.result_dict['RatioYearName3'] = year3
            self.result_dict['RONWyear1'] = float(returnOnNetWorth_year1)
            self.result_dict['RONWyear2'] = float(returnOnNetWorth_year2)
            self.result_dict['RONWyear3'] = float(returnOnNetWorth_year3)
            self.result_dict['ICyear1'] = float(interestCoverage_year1)
            self.result_dict['ICyear2'] = float(interestCoverage_year2)
            self.result_dict['ICyear3'] = float(interestCoverage_year3)
            self.result_dict['DEyear1'] = float(debtToEquity_year1)
            self.result_dict['DEyear2'] = float(debtToEquity_year2)
            self.result_dict['DEyear3'] = float(debtToEquity_year3)
            return True

        except :
            print ('faild in getRatio bussinesSTD loop')
            return False
