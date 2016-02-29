# Purpose - ItemsetData is a class to generate transaction data with seeded events in order to test mining algorithms

import random
import sys
from collections import defaultdict, namedtuple
import matplotlib.pyplot as plt
import numpy as np 

class ItemsetData:

   # Initiates the ItemsetData object
   # Inputs
   # minRealTemplates = The lower bound for the template ID range used to create true sequences
   # maxRealTemplates = The upper bound for the template ID range used to create true sequences
   # minfillerTemplates = The lower bound for the template ID range used as filler in transactions
   # maxfillerTemplates = The upper bound for the template ID range used as filler in transactions   
   def __init__(self, minrealTemplates=1, maxrealTemplates=200, minfillerTemplates=300, maxfillerTemplates=500):    
   
       # Templates id ranges in true planned patterns and filler patterns
       self.minrealTemplates = minrealTemplates
       self.maxrealTemplates = maxrealTemplates
       self.minfillerTemplates = minfillerTemplates
       self.maxfillerTemplates = maxfillerTemplates
       self.realTemplates = range(minrealTemplates,maxrealTemplates)
       self.fillerTemplates = range(minfillerTemplates,maxfillerTemplates)
       
       # Lists to store real events and the generated transactions
       self.realEventsList = []
       self.transactionsList = []
       #self.transactionsWindows = []
       
       # Variables for tracking usage statistics in object
       self.counter = defaultdict(int)
       self.wasItUsed = defaultdict(int) 
       self.fillerTemplatesLimit = defaultdict(int)	   	   	   
     
   # Create list of defined event sequences
   # Input 
   # numRealPatterns = The true number of unique sequences that will appear in the transactions
   # minRealEventLength = The minimum length for the unique sequences
   # maxRealEventLength = The maximum length for the unique sequences
   # Output
   # Returns a list containing list of templates that can be used as frequent itemsets
   def createRealEvents(self, numRealPatterns=20, minRealEventLength=2, maxRealEventLength=15):

	   realEvent = []
	   lenRealPatterns =[]
	   done = False
	   
	   # Create array of semi-random event lengths 
	   for x in range(numRealPatterns):
		  lenRealPatterns.append(random.randint(minRealEventLength,maxRealEventLength))
   
	   # Build real events
	   for i in range(numRealPatterns):
		  realEvent = []
		  for j in range(lenRealPatterns[i]):
		     done = False
		     while (not done):
		        tempChoice = random.choice(self.realTemplates)
		        if tempChoice not in realEvent: 
		           realEvent.append(tempChoice)
		           done = True
		  self.realEventsList.append(realEvent)
	   
	   return self.realEventsList

   
   # Insert high frequency templates IDs into existing transactionsList
   # Inputs 
   # value = The template ID of the high frequency item
   # modChance = The modular probability of inserting the high frequency item (ex: 20=5%, 10=10%, 5=20%)
   def addFreq(self, value=-1, modChance=10):
      
        # Occasionally add in high frequency template value of -1
        for row in self.transactionsList:
           if random.randint(0,100) % modChance == 0:
				 row.append(value)
				 self.wasItUsed[value]+=1
  
   
   # Create transactions of template IDs
   # Inputs 
   # numTransactions = Number of transactions to generate
   # transactionLength = The upper bound for the length of any given transaction
   # probabilityEvent = The probability that an event is inserted into a transaction
   # paddingLimit = The maximum number of filler templates to pad when inserting a seeded event in a transaction
   # Outputs
   # Returns a list of transactions or a list of namedtuples
   def createTransactions(self, numTransactions=1000, transactionLength=20, probabilityEvent=.5, paddingLimit=2):
       
       # Create randomized usage limits for filler templates
       for i in self.fillerTemplates: self.fillerTemplatesLimit[i]=random.randint(int(numTransactions)/1000,int(numTransactions/50))
       probabilityEvent = int((1-probabilityEvent)*100)
            
       for i in range(numTransactions):
          
          if i !=0 and i % 10000 == 0: sys.stderr.write("\nJust passed " + str(i) + " transactions...")  
          transactionList = []
          
          # If true, add in a real event and pad with a semi-random amount of filler
          if(random.randint(0,100)>probabilityEvent):
                    
			  real = list(random.choice(self.realEventsList))
			  
			  for j in range(len(real)):			     			     
			     isItStuck = 0
			     
			     for k in range(random.randint(0,paddingLimit)):
			        ok = False
			        while(not ok):
					temp = int(random.gauss(self.maxfillerTemplates/2, self.minfillerTemplates))					
					if temp>self.minfillerTemplates and temp<self.maxfillerTemplates and self.wasItUsed[temp]<self.fillerTemplatesLimit[temp]:
					   self.wasItUsed[temp]+=1
					   transactionList.append(temp)
					   ok = True
					else: 
					   isItStuck += 1
					   if isItStuck > 1000: ok = True
			     
			     self.wasItUsed[real[j]]+=1
			     transactionList.append(real[j])
			     
			     for k in range(random.randint(0,paddingLimit)):
			        ok = False
			        while(not ok):
					temp = int(random.gauss(self.maxfillerTemplates/2, self.minfillerTemplates))					
					if temp>self.minfillerTemplates and temp<self.maxfillerTemplates and self.wasItUsed[temp]<self.fillerTemplatesLimit[temp]:
					   self.wasItUsed[temp]+=1
					   transactionList.append(temp)
					   ok = True
					else: 
					   isItStuck += 1
					   if isItStuck > 1000: ok = True
			     
			  self.counter[frozenset(real)] += 1     
						
		  # If false, put in only filler templates
          else:
			  useLength = random.randint(3,transactionLength)
			  for k in range(useLength):
				 ok = False
				 isItStuck = 0 
				 while(not ok):
					temp = int(random.gauss(self.maxfillerTemplates/2, self.minfillerTemplates))					
					if temp>self.minfillerTemplates and temp<self.maxfillerTemplates and self.wasItUsed[temp]<self.fillerTemplatesLimit[temp]:
					   self.wasItUsed[temp]+=1
					   transactionList.append(temp)
					   ok = True  
					else: 
					   isItStuck += 1
					   if isItStuck > 1000: ok = True 
          
          self.transactionsList.append(transactionList)            
                             
       return self.transactionsList      
           	       	       
   # Write transactions to file
   # Inputs
   # outFile = File name to write transactions   
   def writeTransactions(self, outFile):

	   outputFile = open(outFile, 'w')   
	   for line in self.transactionsList:
		  outputFile.write(''.join([str(i) + ' ' for i in line]) + "\n")     
	   outputFile.close() 

   # Write Metrics/Stats File
   # Inputs
   # outFile = File name to write transactions 
   def writeStandardStats(self, outFile):
   
	   outputFile = open(outFile, 'w')   
	   # Output the real events that were inserted in transactions   
	   outputFile.write("------------" + str(len(self.realEventsList)) + " Real Events (Pattern->Count)----------\n")    
	   for entity in self.counter:
		  outputFile.write(''.join([str(i) + ' ' for i in entity]) + "->" + str(self.counter[entity]) +"\n")  
	  
	   # Output template usage stats
	   outputFile.write("\n\n-----------Template Stats (Temple->Count if Count > 500)------------\n")  
	   for template in sorted(self.wasItUsed, key=self.wasItUsed.get, reverse=True):
		  if self.wasItUsed[template] > 500:
			 outputFile.write(str(template) + "->" + str(self.wasItUsed[template]) +"\n")        
	   outputFile.close()
   
   #Plot bar chart of overall template usage 
   def plotTemplateUsage(self, title):
   
      index = np.arange(len(self.wasItUsed))
      fig, ax = plt.subplots()
      bar_width = 1
      opacity = 0.4
      templateIDs = []
      usageStats = []
      newLabels = []
      
      for x in sorted(self.wasItUsed.items()):
         if x[0] % 50 != 0: templateIDs.append('')
         else: templateIDs.append(x[0])
         usageStats.append(x[1])

      templatesPlot = plt.bar(index, usageStats, bar_width,
                 alpha=opacity,
                 color='b')
      
      plt.xlabel('Template ID')
      plt.ylabel('Times Used')
      plt.title(title + ' - Templates Used in Transactions')
      plt.xticks(index, templateIDs, rotation="vertical")
      plt.show()
       
                          
      