# Purpose - Score and plot algorithm results against generated frequent itemset data 

import copy
import multiprocessing
import sys
from collections import namedtuple

from magichour.api.local.modelgen import events
from magichour.validate.datagen.ItemsetData import *

algorithmScore = namedtuple('algorithmScore', ['totalScore', 'numEvents', 'proposedEvents', 'exactMatches', 'strongMatches', 'weakMatches', 'noMatches', 'parameter'])

# Plot Algorithm Results
def plotResults(name, steps, score, numTransactions, numRealEvents):
   
   correct = [x.exactMatches for x in score]
   strong = [x.strongMatches for x in score]
   weak = [x.weakMatches for x in score]
   none = [x.noMatches for x in score]
               
   n_groups = len(steps)
   index = np.arange(n_groups)
   fig, ax = plt.subplots()
   bar_width = .2
   opacity = 0.4

   rects1a = plt.bar(index, correct, bar_width,
                 alpha=opacity,
                 color='g',
                 label='Exact Matches')
   rects1b = plt.bar(index + bar_width, strong, bar_width,
                 alpha=opacity,
                 color='b',
                 label='Strong Matches')
   rects1c = plt.bar(index + bar_width*2, weak, bar_width,
                 alpha=opacity,
                 color='y',
                 label='Weak Matches')                
   rects1d = plt.bar(index + bar_width*3, none, bar_width,
                 alpha=opacity,
                 color='r',
                 label='No Significant Overlap')                

   plt.xlabel('Parameter')
   plt.ylabel('Number of Events Identified')
   plt.title(name + ":" + str(numTransactions) + " transactions, " + str(numRealEvents) + " seeded events")
   plt.xticks(index + bar_width*2, steps)
   plt.legend(loc=2)
   plt.show()

# Score algorithm results against test data
def scoreResults(answerKey, algorithmResults, parameter):
   
   numAnswers = len(answerKey)
   resultsLength = len(algorithmResults)
   totalScore = 0
   exactMatches = 0
   strongMatches = 0
   weakMatches = 0
   noMatches = 0
   
   for algorithmAnswer in algorithmResults:
      noMatch = True      
      for correctAnswer in answerKey:
         totalDifference = len(correctAnswer.symmetric_difference(algorithmAnswer.template_ids)) 
         totalSimilarity = len(correctAnswer.intersection(algorithmAnswer.template_ids)) 
         onesidedDifference = len(correctAnswer.difference(algorithmAnswer.template_ids))
         if totalDifference == 0:
            exactMatches += 1
            noMatch = False           
         elif totalSimilarity > totalDifference:
            strongMatches += 1
            noMatch = False
         elif totalSimilarity > onesidedDifference:
            weakMatches += 1
            noMatch = False
      if noMatch: noMatches += 1
                     
   totalScore = float(exactMatches + (.5*strongMatches) + (.01*weakMatches) - (.01*noMatches)) / numAnswers
   
   return algorithmScore(totalScore, numAnswers, resultsLength, exactMatches, strongMatches, weakMatches, noMatches, parameter)

# Print scores
def printScores(algorithmName, score):
    for normalScores in score: 
        print "\n\n---" + algorithmName + " Scores ---"
        print "\nNumber of seeded events: ", normalScores.numEvents
        print "Total number of events proposed by " + algorithmName + ": " + str(normalScores.proposedEvents)
        print "Parameter: ", normalScores.parameter
        print "Total score (maximum of 1.0): ", normalScores.totalScore
        print "Exactly matched " + str(normalScores.exactMatches) + " of the " + str(normalScores.numEvents) + " generated events (" + str(100*normalScores.exactMatches/normalScores.numEvents) + "%)"
        print "Partial matches: ", str(normalScores.strongMatches)
        print "Weak matches: ", str(normalScores.weakMatches)
        print "No significant overlap: ", str(normalScores.noMatches)	
        sys.stdout.flush()

# Write algorithm results to a file        
def writeResults(results, filename):
    outputFile = open(filename, 'w')
    for result in results: 
        outputFile.write(''.join([str(i) + ' ' for i in result.template_ids]))
        outputFile.write("\n")
    outputFile.close()
        
# Included to allow multiprocessing execution of PARIS algorithm
def run_score_paris(inputData):
   	  testData, r, iterations, tau, highFreq, verbose = inputData
   	  sys.stderr.write("Running PARIS with tau " + str(tau) + "\n")
   	  parisResults = events.paris(testData.transactionsList, r, iterations, tau)
   	  if verbose:
   	     if (highFreq): filename="paris"+str(tau)+"hifreq.results"
   	     else: filename="paris"+str(tau)+".results" 
   	     writeResults(parisResults,filename)
   	  return scoreResults(testData.counter, parisResults, tau)

# Included to allow multiprocessing execution of FPGrowth algorithm
def run_score_fpgrowth(inputData):
   	  testData, support, highFreq, verbose = inputData
   	  sys.stderr.write("Running FPGrowth with minimum support " + str(support) + "\n")  	  
   	  fpgrowthResults = events.fp_growth(testData.transactionsList, support)
   	  if verbose:
   	     if (highFreq): filename="fpgrowth"+str(support)+"hifreq.results"
   	     else: filename="fpgrowth"+str(support)+".results" 
   	     writeResults(fpgrowthResults,filename)
   	  return scoreResults(testData.counter, fpgrowthResults, support)

# Included to allow multiprocessing execution of Glove algorithm
def run_score_glove(inputData):
      testData, num_components, glove_window, epochs, highFreq, verbose = inputData
      sys.stderr.write("Running glove with epochs " + str(epochs) + "\n" )
      gloveResults = events.glove(testData.transactionsList, num_components, glove_window, epochs)
      if verbose:
         if (highFreq): filename="glove"+str(epochs)+"hifreq.results"
         else: filename="glove"+str(epochs)+".results"
         writeResults(gloveResults,filename)
      return scoreResults(testData.counter, gloveResults, epochs)
   	  
# Main function
def main(argv):
   
   # Set algorithms to test
   testParis = True
   testGlove = True
   testFPGrowth = False
   
   # Control amount of detailed feedback as plots and output files
   verbose = False
   showPlots = False
   
   # Main variables to tweak for generating real events,transactions,events and plots
   numTransactions = 150000
   numRealEvents = 20
   minRealTemplateID = 1
   maxRealTemplateID = 500
   minFillTemplateID = 1000
   maxFillTemplateID = 2500
   minRealEventLength = 4
   maxRealEventLength = 8
   transactionLength = 20
   probabilityEvent = .20
   paddingLimit = 2
   
   # Initiating ItemSet object and generating real events for seeding in transactions
   testData = ItemsetData(minRealTemplateID,maxRealTemplateID,minFillTemplateID,maxFillTemplateID)
   testData.createRealEvents(numRealEvents, minRealEventLength, maxRealEventLength)
   sys.stderr.write("\nCreated " + str(len(testData.realEventsList)) + " Real Events")
   
   # Generating transactions 
   testData.createTransactions(numTransactions, transactionLength, probabilityEvent, paddingLimit)
   sys.stderr.write("\nCreated " + str(len(testData.transactionsList)) + " transactions\n")
      
   # Show histogram of template usage
   if (showPlots): testData.plotTemplateUsage("Standard Data")
   
   # Writing out transactions and answer key, if needed offline
   if verbose:
      testData.writeTransactions("testData.transactions")
      testData.writeStandardStats("testData.answerkey")
   
   # Create a clone of original data set 
   testDataFreqs = ItemsetData()
   testDataFreqs = copy.deepcopy(testData)
   
   # Adding high frequency items to clone of original data set
   testDataFreqs.addFreq(2001,100) 
   testDataFreqs.addFreq(2002,100)
   testDataFreqs.addFreq(2003,100) 
   testDataFreqs.addFreq(2004,100) 
 
   # Show histogram of template usage
   if (showPlots): testDataFreqs.plotTemplateUsage("High Frequency Data")
  
   # Writing out high freq transactions and answer key, if needed offline
   if verbose: 
      testDataFreqs.writeTransactions("testDataFreqs.transactions")
      testDataFreqs.writeStandardStats("testDataFreqs.answerkey")
   
   # Prepare for multiprocessing
   p = multiprocessing.Pool(multiprocessing.cpu_count())
   
   # Test Glove
   if testGlove:
       epochs = [2,3,4,5,6,7,8,9,10,20]
       test_cases = []
       test_cases_freq = []
       for step in epochs:
		  test_cases.append((testData, 16, 10, step, False, verbose))
		  test_cases_freq.append((testDataFreqs, 16, 10, step, True, verbose))
       
       normalScore = p.map(run_score_glove, test_cases)
       printScores("Glove - Standard", normalScore)
       if (showPlots): plotResults("Glove - Standard", epochs, normalScore, numTransactions, numRealEvents) 
             
       freqsScore = p.map(run_score_glove, test_cases_freq)
       printScores("Glove - High Frequency", freqsScore)           
       if (showPlots): plotResults("Glove - High Frequency", epochs, freqsScore, numTransactions, numRealEvents)  
              
   # Test PARIS
   if testParis:
	   tau = [5,10,15]
	   test_cases = []
	   test_cases_freq = []   
	   for step in tau:
		  test_cases.append((testData, 0, 2, step, False, verbose))
		  test_cases_freq.append((testDataFreqs, 0, 2, step, True, verbose))
   		   
	   normalScore = p.map(run_score_paris, test_cases) 
	   printScores("PARIS - Standard", normalScore)
	   if (showPlots): plotResults("PARIS - Standard", tau, normalScore, numTransactions, numRealEvents) 
      
	   freqsScore = p.map(run_score_paris, test_cases_freq)
	   printScores("PARIS - High Frequency", freqsScore)    
	   if (showPlots): plotResults("PARIS - High Frequency", tau, freqsScore, numTransactions, numRealEvents) 
             
	      	   
   # Test FP-Growth
   if testFPGrowth:
	   support = [.05,.1]
	   test_cases = []
	   test_cases_freq = []	   
	   for level in support:
		  test_cases.append((testData, level, False, verbose))
		  test_cases_freq.append((testDataFreqs, level, True, verbose))
   
	   normalScore = p.map(run_score_fpgrowth, test_cases) 
	   printScores("FPGrowth - Standard", normalScore)
	   if (showPlots): plotResults("FPGrowth - Standard", support, normalScore, numTransactions, numRealEvents) 
	   
	   freqsScore = p.map(run_score_fpgrowth, test_cases_freq) 
	   printScores("FPGrowth High Frequency", freqsScore)     
	   if (showPlots): plotResults("FPGrowth High Frequency", support, freqsScore, numTransactions, numRealEvents) 
	         

if __name__ == "__main__":
    main(sys.argv[1:])