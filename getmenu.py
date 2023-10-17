import csv

class Menu():
    def __init__(self):
        pass
    
    def csvToFormattedList(self):
        daysOfMonthCount = 0
        menuListOfMonth = []
        with open("yemekhane.csv", encoding="utf-8") as csvfile:
            csvReader = csv.reader(csvfile)
            for row in csvReader:
                menuListOfMonth.append(row)
                daysOfMonthCount += 1
        return menuListOfMonth, daysOfMonthCount

    def isStructureCorrupt(self, menuListOfMonth):
        expected_num_columns = 7  
        #Upgradable Component
        for row in menuListOfMonth:
            if len(row) != expected_num_columns: 
                return True  
        return False  

    def getFormattedMenu(self):
        menuListOfMonth, daysOfMonthCount = self.csvToFormattedList()
        
        if self.isStructureCorrupt(menuListOfMonth):
            #This part can be upgraded for better controls
            return "The structure of the Excel file is corrupt or has changed."

        
        excelRowCount = 1
        dateOfMonth = []
        sortedMenuList = []
        for _ in range(daysOfMonthCount - 2):
            excelRowCount += 1
            dateOfMonth.append(menuListOfMonth[excelRowCount][0])
            tempMenuRow = [menuListOfMonth[excelRowCount][2], menuListOfMonth[excelRowCount][3], menuListOfMonth[excelRowCount][4], menuListOfMonth[excelRowCount][5], menuListOfMonth[excelRowCount][6]]
            tempMenuRow = "\n".join(tempMenuRow)
            sortedMenuList.append(tempMenuRow)
        
        finalFormOfMenuList = []
        daysOfMonthCount2 = 0
        for isEmpty in sortedMenuList:
            if isEmpty == '\n\n\n\n':
                weekendText = sortedMenuList[daysOfMonthCount2].replace('\n\n\n', 'Haftasonu Yemek Hizmeti Yoktur')
                finalFormOfMenuList.append(weekendText)
                daysOfMonthCount2 += 1
            else:
                finalFormOfMenuList.append(isEmpty)
                daysOfMonthCount2 += 1
        
        return finalFormOfMenuList, dateOfMonth

