from solr_controller import SolrController

import argparse
from time import time


def __main__():
    # parser for command-line arguments
    parser = argparse.ArgumentParser(description='Matches chemical names to STITCH IDs', version='0.1')
    # make argparse handle booleans more reasonably
    def str2bool(v):
        if v.lower() in ('yes', 'true', 't', '1'):
            return True
        elif v.lower() in ('no', 'false', 'f', '0'):
            return False
        else:
            print 'Unknown boolean argument: %s' %v
            return False    
    parser.register('type','bool',str2bool)
    parser.add_argument('-n', '--namefile', type=str, help='file name of the chemical list')
    parser.add_argument('-o', '--outputfile', type=str, help='file name of the matching output')
    parser.add_argument('-u', '--universe', default='STITCH', type=str, help='chemical ID universe (STITCH or PUBCHEM)')
    parser.add_argument('-a', '--approximate', default=True, type=str2bool, help='also attempt fuzzy matching')
    parser.add_argument('-e', '--heuristic', default=True, type=str2bool, help='also attempt heuristic matching')
    parser.add_argument('-s', '--synonyms', default=False, type=str2bool, help='perform synonym retrieval instead of name matching')
    parser.add_argument('--verbose', type=int, default=1, help='verbosity level')
    
    st = time()
    args = parser.parse_args()
    print("DEBUG: " + args.outputfile)
    # check arguments for validity
    # TODO this should be better tied to the config file!
    if (args.universe.upper() == 'STITCH'):
        universe = 'stitch20141111'
    elif (args.universe.upper() == 'PUBCHEM'):
        universe = 'pubchem-unfiltered20141110'
    else:
        print 'Unknown chemical ID universe (-u / --universe argument):'
        print args.universe
        print 'Exiting'
        exit(1)
        
    if args.namefile is None:
        print 'Name of file with list of chemical needs to be provided (-n / --namefile argument)'
        print 'Exiting'
        exit(1)
        
    if args.outputfile is None:
        print 'Name of output file needs to be provided (-o / --outputfile argument)'
        print 'Exiting'
        exit(1)

    # TODO this should be part of a function that can also be called externally
    # init name matching parameters
    exact = True
    if args.verbose >=3:
        print 'approximate option: %s' %args.approximate
        print 'heuristic option: %s' %args.heuristic
        print 'synonyms option: %s' %args.synonyms

    # start a SolrController instance and delegate name matching to it
    sc = SolrController(args.verbose, search_space=universe)
    if args.synonyms:
        sc.findSynonyms(args.namefile, args.outputfile, args.approximate, exact, args.heuristic)
    else:
        sc.matchNames(args.namefile, args.outputfile, args.approximate, exact, args.heuristic)

    e = time() - st
    if args.verbose >=1:
        print 'Name matching performed in %.1f sec.' %e



if __name__ == '__main__': __main__()
