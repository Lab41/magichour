from collections import namedtuple

from magichour.api.dist.templates.templateEval import read_templates

def parse_words(log_lines):
    """
    Take single LogLine and split words for input to a word count

    Args:
         log_lines(LogLine): Input log line

    Returns:
         : List of (word, count) tuples where the count will always be 1
    """
    words = set(log_lines.processed.split())
    return [(word, 1) for word in words]

def extract_patterns(line, frequent_words):
    """
    Take single LogLine and output a tuple of frequent words and frequent words with skips

    Args:
         log_lines(LogLine): Input log line

    Returns:
        (tuple([str]), list[str]) : tuple of (frequent words in order, freq words with skip counts between frequent words)
    """
    skip = 0 # Count of non-frequent words since the last frequent word
    freq_word_pattern = [] # Pattern of frequent words (ignoring non-frequent words)
    pattern = [] # Pattern with frequent words and skip counts
    for word in line.processed.split():
        # If this is a frequent word
        if word in frequent_words.value:
            # If we've skipped some words since the last frequent word, add to "pattern"
            if skip != 0:
                pattern.append(skip)
                skip = 0
            # Add word to both pattern and freq_word_pattern
            freq_word_pattern.append(word)
            pattern.append(word)
        else:
            # Keep track fo skip count
            skip += 1

    return (tuple(freq_word_pattern), pattern)


def collapse_patterns(input_pattern_tuple):
    """
    Collapse all the related patterns into a single pattern string

    Args:
         input_pattern_tuple((tuple[str], iterable[list[str]])):

    Returns:
        list[list[str]]: Returns a list of pattern strings (where the pattern is a list of strings)
    """
    # Break apart tuple
    freq_word_pattern, patterns = input_pattern_tuple

    # Get unique patterns
    patterns = set([tuple(pattern) for pattern in patterns]) # tuple = hashable

    # Turn original patters from [w1, w2, w3] => [set(), w1, set(), w2, set(), w3, set()]
    # Sets will be used to keep track of an skip words
    aggregate_pattern = [set()]
    for word in freq_word_pattern:
        aggregate_pattern.append(word)
        aggregate_pattern.append(set())

    # Iterate over patters keeping track of number of skips that occur
    for pattern in patterns:
        output_loc = 0
        # TODO: Make 0 and 1 constants
        prev_val = 0
        for word in pattern:
            if isinstance(word, int):
                aggregate_pattern[output_loc].add(word)
                output_loc += 1
                prev_val = 1
            else:
                # TODO: Add check here that it matches what it should match
                if prev_val == 0:
                    aggregate_pattern[output_loc].add(0)
                    output_loc += 2
                else:
                    output_loc += 1
                prev_val = 0

    # Create final pattern strings where sets are collapsed into skip from regex
    final_pattern = []
    for word in aggregate_pattern:
        if isinstance(word, set):
            if len(word) >= 2:
                final_pattern.append('(:? S+){%d,%d}'%(min(word), max(word)))
            elif len(word) == 1 and 0 not in word: # Always skip the same number of values
                final_pattern.append('(:? S+){%d,%d}'%(min(word), max(word)))
        else:
            final_pattern.append(word)
    return final_pattern

def log_cluster(sc, log_lines, support):
    """
    Run log cluster

    Args:
         log_lines(rdd of LogLine): Input log messages as LogLine objects
         support(int): Threshold # of occurrences before a pattern can be included

    Returns:
        list[DistributedTemplateLine]: Returns a list of DistributedTemplateLine objects defining the templates
    """
    frequent_word_dict = log_lines.flatMap(parse_words)\
                                 .reduceByKey(lambda x,y: x+y)\
                                 .filter(lambda (key,count): count > support)\
                                 .collectAsMap()

    frequent_words = sc.broadcast(set(frequent_word_dict.keys()))

    clusters = log_lines.map(lambda x: extract_patterns(x, frequent_words))\
                  .groupByKey()\
                  .filter(lambda (freq_word_pattern, pattern): len(pattern) > support)\
                  .map(collapse_patterns)\
                  .collect()

    templates = [' '.join(cluster) for cluster in clusters]

    transformed_templates = read_templates(templates)
    return transformed_templates
