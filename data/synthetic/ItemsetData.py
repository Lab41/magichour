import random
import sys
from collections import defaultdict


class ItemsetData:
    # Initiates the ItemsetData object
    # Inputs
    # minRealTemplates = The lower bound for the template ID range used to create true sequences
    # maxRealTemplates = The upper bound for the template ID range used to create true sequences
    # minfillerTemplates = The lower bound for the template ID range used as filler in transactions
    # maxfillerTemplates = The upper bound for the template ID range used as
    # filler in transactions

    def __init__(
            self,
            minrealTemplates=1,
            maxrealTemplates=999,
            minfillerTemplates=1000,
            maxfillerTemplates=1500):

        # Templates id range in true planned patterns and filler patterns
        self.realTemplates = range(minrealTemplates, maxrealTemplates)
        self.fillerTemplates = range(minfillerTemplates, maxfillerTemplates)

        # Lists to store real events and the generated transactions
        self.realEventsList = []
        self.transactionsList = []

        # Variables for tracking usage statistics in object
        self.counter = defaultdict(int)
        self.wasItUsed = defaultdict(int)

        # Create list of defined event sequences

    # Inputs
    # numRealPatterns = The true number of unique sequences that will appear in the transactions
    # minRealEventLength = The minimum length for the unique sequences
    # maxRealEventLength = The maximum length for the unique sequences
    def createRealEvents(
            self,
            numRealPatterns=20,
            minRealEventLength=2,
            maxRealEventLength=15):

        realEvent = set()
        realEvents = set()
        realEventsList = []
        lenRealPatterns = []

        # Create array of semi-random event lengths
        for x in range(numRealPatterns):
            lenRealPatterns.append(
                random.randint(
                    minRealEventLength,
                    maxRealEventLength))

        # Build real events
        for i in range(numRealPatterns):
            realEvent.clear()
            for j in range(lenRealPatterns[i]):
                realEvent.add(random.choice(self.realTemplates))
            realEvents.add(frozenset(realEvent))

        for entry in realEvents:
            self.realEventsList.append(entry)

    # Insert high frequency templates IDs into existing transactionsList
    # Inputs
    # value = The template ID of the high frequency item
    # modChance = The modular probability of inserting the high frequency item
    # (ex: 20=5%, 10=10%, 5=20%)
    def addFreq(self, value=-1, modChance=10):

        # Occasionally add in high frequency template value of -1
        for row in self.transactionsList:
            if random.randint(0, 100) % modChance == 0:
                row.add(value)
                self.wasItUsed[value] += 1

    # Create transactions of template IDs
    # Inputs
    # numTransactions = Number of transactions to generate
    # transactionLength = The upper bound for the length of any given transaction
    # maxUse = The upper bound on how many times a filler template can be
    # inserted into the transactions
    def createTransactions(
            self,
            numTransactions=1000,
            transactionLength=20,
            maxUse=100):

        for i in range(numTransactions):
            transaction = set()
            transactionList = []

            # If 1, add in a real event and finish the remainder with filler
            if (random.randint(0, 1)):
                real = random.choice(self.realEventsList)
                diff = transactionLength - len(real)
                for j in range(diff):
                    ok = False
                    isItStuck = 0
                    while (not ok):
                        temp = random.choice(self.fillerTemplates)
                        if self.wasItUsed[temp] < maxUse:
                            # if temp not in jumble: self.wasItUsed[temp]+=1
                            # jumble.add(temp)
                            if temp not in transaction:
                                self.wasItUsed[temp] += 1
                            transaction.add(temp)
                            ok = True
                        else:
                            isItStuck += 1
                            if isItStuck > 1000:
                                print "Having trouble finding a usable filler Template. Skipping this step."
                            ok = True

                for item in real:
                    # if item not in jumble: self.wasItUsed[item]+=1
                    # jumble.add(item)
                    if item not in transaction:
                        self.wasItUsed[item] += 1
                    transaction.add(item)
                self.counter[frozenset(real)] += 1

            # If 0, put in only filler templates
            else:
                useLength = random.randint(2, transactionLength)
                for k in range(useLength):
                    ok = False
                    while (not ok):
                        temp = random.choice(self.fillerTemplates)
                        if self.wasItUsed[temp] < maxUse:
                            # if temp not in jumble: self.wasItUsed[temp]+=1
                            # jumble.add(temp)
                            if temp not in transaction:
                                self.wasItUsed[temp] += 1
                            transaction.add(temp)
                            ok = True
                        else:
                            isItStuck += 1
                            if isItStuck > 1000:
                                print "Having trouble finding a usable filler Template. Skipping this step."
                            ok = True

            for slot in transaction:
                transactionList.append(slot)
            random.shuffle(transactionList)
            self.transactionsList.append(set(transactionList))
            # self.transactions.add(frozenset(transaction))

    # Check for unintended patterns due to filler templates randomly inserted in generated transactions
    # WARNING - pairwise set comparison is really slow
    def checkPatterns():

        unintended = defaultdict(int)
        for line1 in self.transactionsList:
            for line2 in self.transactionsList:
                if line1 != line2:
                    test = frozenset(set(line1).intersection(set(line2)))
                    if test != set() and len(test) > 1 and test not in self.realEventsList:
                        unintended[test] += 1
        return unintended

    # Write transactions to file
    # Inputs
    # outFile = File name to write transactions
    def writeTransactions(self, outFile):

        outputFile = open(outFile, 'w')
        for line in self.transactionsList:
            outputFile.write(''.join([str(i) + ' ' for i in line]) + "\n")
        outputFile.close()

        # Write Metrics/Stats File plus unintended pattern analysis

    # WARNING - pairwise set comparison in unintended pattern analysis is really slow
    # Inputs
    # outFile = File name to write transactions
    def writeFullStats(outFile):

        outputFile = open(outFile, 'w')
        # Output the real events that were inserted in transactions
        outputFile.write("------------" +
                         str(len(self.realEventsList)) +
                         " Real Events (Pattern->Count)----------\n")
        for entity in self.counter:
            outputFile.write(''.join([str(i) +
                                      ' ' for i in sorted(entity, key=int)]) +
                             "->" +
                             str(self.counter[entity]) +
                             "\n")

            # Output any new/unintended patterns in the transactions
        outputFile.write(
            "\n\n-------Unintended Filler Pattern Stats (Pattern->Count if Count > 1 and Pattern Length > 1)------\n")
        unintended = checkPatterns()
        for pattern in sorted(unintended, key=unintended.get, reverse=True):
            if unintended[pattern] > 1:
                outputFile.write(''.join([str(i) +
                                          ' ' for i in sorted(pattern, key=int)]) +
                                 "->" +
                                 str(unintended[pattern]) +
                                 "\n")

        # Output template usage stats
        outputFile.write(
            "\n\n-----------Template Stats (Temple->Count if Count > 100)------------\n")
        for template in sorted(
                self.wasItUsed,
                key=self.wasItUsed.get,
                reverse=True):
            if self.wasItUsed[template] > 100:
                outputFile.write(str(template) + "->" +
                                 str(self.wasItUsed[template]) + "\n")
        outputFile.close()

        # Write Metrics/Stats File

    # Inputs
    # outFile = File name to write transactions
    def writeStandardStats(self, outFile):

        outputFile = open(outFile, 'w')
        # Output the real events that were inserted in transactions
        outputFile.write("------------" +
                         str(len(self.realEventsList)) +
                         " Real Events (Pattern->Count)----------\n")
        for entity in self.counter:
            outputFile.write(''.join([str(i) +
                                      ' ' for i in sorted(entity, key=int)]) +
                             "->" +
                             str(self.counter[entity]) +
                             "\n")

            # Output template usage stats
        outputFile.write(
            "\n\n-----------Template Stats (Temple->Count if Count > 100)------------\n")
        for template in sorted(
                self.wasItUsed,
                key=self.wasItUsed.get,
                reverse=True):
            if self.wasItUsed[template] > 100:
                outputFile.write(str(template) + "->" +
                                 str(self.wasItUsed[template]) + "\n")
        outputFile.close()
