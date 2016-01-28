if __name__ == "__main__":
    main()

def main():
    parser = OptionParser()

    parser.add_option("-d", "--directory", dest="directory",
                help="Data directory to recursively read")
    
    logging_choices = ("ERROR", "WARNING", "INFO", "DEBUG")
    default_logging = "INFO"
    parser.add_option("--log_level", dest="log_level", type="choice", choices=logging_choices, default=default_logging,
            help="Logging level. Valid choices: %s. Default: %s" % (logging_choices, default_logging)) 

    (options, args) = parser.parse_args()

    # Create logger
    level = logging.getLevelName(options.log_level)
    logging.basicConfig(level=level)
    logger = logging.getLogger(__name__)

    # Read data directory, store lines into var lines
    logger.info("Opening file (%s)." % options.filename)
    open_fn = gzip.open if options.filename.endswith(".gz") else open
    with open_fn(options.filename) as f:
        if options.num_lines == -1:
            logger.info("Reading entire file.")
            lines = f.readlines()
        else:
            logger.info("Reading %s lines." % options.num_lines)
            lines = list(islice(f, options.num_lines))

    # Parse lines into (t, line)
    
