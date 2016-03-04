# ************************************
# Analyze template order and time duration for observed events
# Input - List of TimedEvents namedtuples, Threshold for Median Absolute Deviation, Boolean value for verbose display output
# Output - List of named tuples, each containing event_id, most frequent template order, order consistency score, kurtosis score, outlier count    
# ************************************

import numpy
import math
import distance
from operator import itemgetter
from scipy.stats import kurtosis
from collections import defaultdict, namedtuple

def consistencyCheck(timed_events, madThreshold=3, verbose=False):             
        
    eventStats = namedtuple('eventStats', ['event_id','order','timing'])
    eventStatsList = []
    eventScore = namedtuple('eventScore', ['event_id', 'mostFreqOrder', 'orderScore', 'kurtosis', 'madOutliers'])
    eventScoreList = []
    
    # Create dictionary of the indices for each event from timed_events results
    eventLookup = defaultdict(list)
    for i in range(0,len(timed_events)): eventLookup[timed_events[i].event_id].append(i)
       
    # Determine arrival order and timing of templates in each observed event in timed_events
    for event in eventLookup:
    
       orderDict = defaultdict(int)
       diffDict = defaultdict(list)
       
       # Review each observed instance of an event id       
       for instance in eventLookup[event]:
 
          # Extract and sort by timestamp, then template id
          templateTupleList = []         
          for template in timed_events[instance].timed_templates: templateTupleList.append((template.ts, template.templateId))           
          templateTupleList = sorted(templateTupleList, key=itemgetter(0,1))
                              
          # Create hashable key of template order for orderDict
          orderString = ""
          for entry in templateTupleList: 
             if orderString == "": orderString += str(entry[1])
             else: orderString += "*"+str(entry[1])
          orderDict[orderString] += 1
          
          # Calculate event duration                
          timeStamps = [x[0] for x in templateTupleList]
          diffDict[orderString].append(max(timeStamps)-min(timeStamps))
                                   
       eventStatsList.append(eventStats(event, orderDict, diffDict))  
    
    # Run stats on each event based on metadata compiled in eventStatsList  
    for event in eventStatsList:
       
       candidateList = []
                    
       # Find most frequent order for current event
       mostFreqOrder = max(event.order, key=event.order.get)
       
       # Include variations based on Levenshtein distance
       for variation in event.order:
          if distance.levenshtein(mostFreqOrder.split('*'),variation.split('*'))<=2: candidateList.append((variation, event.order[variation]))
       
       # Build array of all event durations 
       timingArray = []
       for value in event.timing: 
          for item in event.timing[value]: timingArray.append(item)
              
       # Order is scored by sum of count of most frequent order plus similar patterns divided by overall sum of all order counts
       orderScore = float(sum([x[1] for x in candidateList])) / float(sum([event.order[y] for y in event.order]))
       
       # Calculate Kurtosis, which can provide an indication of the distribution's tailedness
       kurtosisScore = kurtosis(timingArray, bias=False)
       
       # Calculate Median Absolute Deviation and search for outliers based on user-supplied threshold
       outlierCounter = 0
       data = numpy.array(timingArray)
       median = numpy.median(data)
       diff = numpy.array(abs(data - median))
       mad = 1.4826 * numpy.median(diff)
       # If 50% of values are equal, MAD = 0 and MAD predictably flags all non-median items as outliers
       if mad == 0: 
          madWorked = False
          outlierCounter = -1          
       else:
          madWorked = True
          for item in timingArray:
             if item  > median + madThreshold*mad or item < median - madThreshold*mad: outlierCounter += 1
       if outlierCounter != -1: madScore = float(outlierCounter)/float(len(timingArray))
       else: madScore = None
       eventScoreList.append(eventScore(event.event_id,mostFreqOrder.split('*'), orderScore, kurtosisScore, madScore)) 
       
       # Optional summary output for each event   
       if verbose:
       
          # Display most frequent event order 
          print "------\n\n"
          print "The following event was scored:" 
          print "\t" + "%0.2f" % orderScore + " for predictable order (an event with a reliably predictable order has a score of 1.0)"
          print "\t" + "%0.2f" % kurtosisScore + " for Kurtosis (a normal distribution has a Kurtosis score of 0)"
          if madWorked:
             print "\t" + str(outlierCounter) + " duration values were outside " + str(madThreshold) + " Median Absolute Deviations"
          else:
             print "\tMedian Absolute Deviation scoring was not possible on duration data for this event" 
          
          # Display event duration statistics across all event order variations    
          print "\nEvent Duration Statistics:"
          print "\tMean / Median:","%0.2f" % numpy.mean(timingArray),"/",numpy.median(timingArray)
          print "\tStandard Deviation:", "%0.2f" % numpy.std(timingArray)   
          if madWorked: print "\tMedian Absolute Deviation:", "%0.2f" % mad
          print "\tMin / Max:", numpy.amin(timingArray), "/", numpy.amax(timingArray)
          
          # Display other observed event order permutations
          print "\nMost Frequent Event Order: " + "\n\t" + ' '.join(mostFreqOrder.split('*')).strip() + " (observed " + str(event.order[mostFreqOrder]) + "x)"          
          if len(candidateList)>1:
             print "\nEvent was observed in the following permutations with a Levenshtein distance of 2 or less:"
             for variation in candidateList: 
                if variation[0] != mostFreqOrder: print "\t" + ' '.join(variation[0].split('*')).strip() + " (observed " + str(variation[1]) + "x)"
          if len(event.order)-len(candidateList):       
             print "\nEvent was also observed as:"
             for entry in event.order:
                if entry not in [x[0] for x in candidateList]: print "\t" + ' '.join(entry.split('*')).strip() + " (observed " + str(event.order[entry]) + "x)"                        
          print "\n"
    
    return eventScoreList                                            
