import argparse
import re
import sys
import os
import scipy
import scipy.stats as stats
from time import time
from statsmodels.stats import multitest
import ConfigParser

class EnrichmentCalculator:
    ### Constructor initializes the database
    def __init__(self, db_type, verbose):
        # this method raises Errors if db_type is not recognized or if the database file cannot be read
        self.verbosity = verbose
        # get settings from config file
        self.__readConfig()
        if not db_type in self.__SUPP_DATABASES:
            raise ValueError('\'%s\' is not a supported database' % db_type)
        self.db_type = db_type
        try:
            self.db_prop_cid_map = self.readDB()
        except IOError:
            raise
        self.background = None
        self.fg_score_dict = None
        self.fg_name_dict = None


    ### Class method to parse a list of CIDs into a dictionary
    @classmethod
    def parseCIDList(self, cid_file):
        cid_score_dict = dict()
        cid_name_dict = dict()
        with open(cid_file, 'r') as fin:
            for line in fin:
                l = line.split('\t')
                c = l[0].strip()
                name = line.split('\t')[3]
                if len(l) > 1:
                    s = l[1].strip()
                    if s == 'NA':
                        s = float('NaN')
                    else:
                        s = float(s)
                        assert(s >= 0)
                else:
                    s = -1.0
                # ignore lines where CID (first field) is 'NA'
                if c.upper() != 'NA':
                    # TODO THIS NEEDS FIXING!!! user can supply the same drug multiple times in input...
                    #assert(c not in cid_score_dict)
                    cid_score_dict[c] = s
                    cid_name_dict[c] = name
        assert fin.closed
        dic_to_return = {"cid_score_dict":cid_score_dict, "cid_name_dict":cid_name_dict}
        return dic_to_return


    ### Method to read in a drug property database from its corresponding file
    def readDB(self):
        fn_db = self.__DB_DIR + "/" + self.__DB_PREFIX + '_' + self.db_type + '.' + self.__DB_FORMAT
        if self.verbosity >= 2:
            print '  reading %s database from %s...' % (self.db_type, fn_db)
        db_cid_prop_map = dict()
        try:
            with open(fn_db, 'r') as fdb:
                for line in fdb:
                    if line.startswith('CID'):
                        pass
                    l = line.split('\t')
                    c = l[0].strip()
                    p = l[1].strip()
                    # TODO parse scores
                    #s = l[2].strip()
                    if p in db_cid_prop_map.viewkeys():
                        db_cid_prop_map[p] = db_cid_prop_map[p].union(set([c]))
                    else:
                        db_cid_prop_map[p] = set([c])
            assert fdb.closed            
        except IOError:
            print 'Failed to read database from %s' % fn_db
            raise
        if self.verbosity >= 2:
            print '  initialized %s database (%i annotations).' %(self.db_type, len(db_cid_prop_map))
        return(db_cid_prop_map)


    ### Method to set the background set of chemicals
    def setBackground(self, bg='ALL'):
        self.background = bg
        if self.background == 'ALL':
            self.background = set([item for subset in self.db_prop_cid_map.values() for item in subset])
            self.bg_cid_prop_map = self.db_prop_cid_map
        else:
            self.bg_cid_prop_map = dict()
            for k in self.db_prop_cid_map.viewkeys():
                v = self.db_prop_cid_map[k]
                v = v.intersection(self.background)
                self.bg_cid_prop_map[k] = v


    ### Method to match a foreground list of chemical against the drug annotation database
    def matchForeground(self, fg_score_dict, match_file=None):
        # check for annotations of the foreground drugs
        db_cid_prop_map = dict()
        for k in self.db_prop_cid_map:
            for v in self.db_prop_cid_map[k]:
                if v in db_cid_prop_map:
                    db_cid_prop_map[v].append(k)
                else: 
                    db_cid_prop_map[v] = [k]

        matched_fg = dict()
        # this awkward testing for the 'None' string is necessary (at least convenient) for Galaxy integration
        if match_file is not None and not match_file == 'None':
            fout = open(match_file, 'w')
            print >>fout, 'CID\tName\t%s' %(self.db_type)
        else:
            fout = open(os.devnull, 'w')
        for c in fg_score_dict.viewkeys():
            if c in db_cid_prop_map:
                print >>fout, '%s\t%s\t%s' %(c, self.fg_name_dict[c], '; '.join(db_cid_prop_map[c]))
                #print "writing to file " + match_file + " line : " + str(c) + " : " + str('; '.join(db_cid_prop_map[c]))
                matched_fg[c] = fg_score_dict[c]
            else:
                print >>fout, '%s\t%s\tNA' %(c,self.fg_name_dict[c])
        fout.close()
        # Make sure that the background contains the entire foreground
        #if self.background is not None:
        #    # TODO solvede this should rather result in a more explicit error!
        #    if len(set(matched_fg.viewkeys()).difference(self.background)) != 0:
	#        sys.stderr.write("The chemicals listed in the foreground are not all found in the background !")
	#        sys.exit(1)
	    #assert(len(set(matched_fg.viewkeys()).difference(self.background)) == 0)
        self.fg_score_dict = matched_fg


    ### Method to perform the actual enrichment calculations
    def calcEnrichment(self, method='Fisher', correction='FDR'):
        if not method in self.__SUPP_METHODS:
            raise ValueError('\'%s\' is not a supported method' % method)
        # get the union set of drug properties of any of the foreground drugs
        db_dict = dict()
        if method == 'Fisher':
            p_val = list()
            odds_r = list()
            n_r = list()
            props = list()
            chemicals = list()
            # test each property (k) independently for enrichment
            # (e.g. drug targets with ligand set L in foreground F)
            # assemble 2x2 contingency table (rows: in F / not in F; cols: in L / not in L)
            foreground = set(self.fg_score_dict.viewkeys())
            not_foreground = self.background.difference(foreground)
            for k in self.bg_cid_prop_map.viewkeys():
                ligands = self.db_prop_cid_map[k]
                ct_11 = len(foreground.intersection(ligands)) # in F & in L
                ct_12 = len(foreground.difference(ligands)) # in F & not in L
                ct_21 = len(not_foreground.intersection(ligands)) # not in F & in L
                ct_22 = len(not_foreground.difference(ligands)) # not in F & not in L                    
                table = [[ct_11, ct_12], [ct_21, ct_22]]
                o, p = stats.fisher_exact(table)
                props.append(k)
                odds_r.append(o)
                n_r.append(str(ct_11)+'/'+str(ct_11+ct_21))
                p_val.append(p)
            # correct for multiple testing
            if correction=='FDR':
                tmp1, p_adj, tmp2, tmp3 = multitest.multipletests(p_val, method='fdr_bh')
                p_adj = [p for p in p_adj]
            elif correction=='Bonferroni':
                p_adj = [p*len(p_val) for p in p_val]
            else:
                print 'Unknown method for multiple hypothesis correction:'
                print correction
                print 'Exiting'
                exit(1)
            return(props, odds_r, n_r, p_val, p_adj)
        else:
             raise ValueError('\'%s\' is not yet implemented' % method)          
        # TODO IMPLEMENT other methods (like Wilcoxon test or ROC for ranked drug lists)

        
    def __readConfig(self):
        cfg_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../conf/settings.cfg')
        cfg = ConfigParser.ConfigParser()
        cfg.read(cfg_file)

        self.__DB_DIR = cfg.get('annotation', 'db_dir')
        self.__DB_FORMAT = cfg.get('annotation', 'db_format')
        self.__DB_PREFIX = cfg.get('annotation', 'db_prefix')
        tmp = cfg.get('annotation', 'supp_methods')
        self.__SUPP_METHODS = re.findall(r"[[\w\\._-]+", tmp)
        tmp = cfg.get('annotation', 'supp_databases')
        self.__SUPP_DATABASES = re.findall(r"[[\w\\._-]+", tmp)

        if self.verbosity >=2:
            print 'Annotation database dir        = ' + self.__DB_DIR
            print 'Annotation database format     = ' + self.__DB_FORMAT
            print 'Annotation database prefix     = ' + self.__DB_PREFIX
            print 'Annotation supported methods   = ' + ', '.join(self.__SUPP_METHODS)
            print 'Annotation supported databases = ' + ', '.join(self.__SUPP_DATABASES)


def __main__():
    # parse command-line arguments
    parser = argparse.ArgumentParser(description='Calculates enrichment of drug properties', version='0.1')
    parser.add_argument('-f', '--foreground', type=str, help='file name of the drug foreground')
    parser.add_argument('-b', '--background', type=str, default='ALL', help='file name of the drug background')
    parser.add_argument('-d', '--database', type=str, help='drug property database')
    parser.add_argument('-o', '--enrichment_output', type=str, help='name of the output file to which enrichments will be written')
    parser.add_argument('-p', '--annotation_output', type=str, help='name of the output file with information on the availability of durg annotations')
    parser.add_argument('-m', '--method', type=str, default='Fisher', help='method to be used for enrichment calculation')
    parser.add_argument('-a', '--alpha', type=float, default=0.05, help='alpha level for type I error control (i.e. p-value cutoff)')
    parser.add_argument('-c', '--correction', type=str, default='FDR', help='Correction method for multiple hypothesis testing [FDR, Bonferroni]')
    parser.add_argument('--verbose', type=int, default=1, help='verbosity level')

    st = time()
    args = parser.parse_args()
    assert(args.foreground is not None)
    assert(args.database is not None)
    assert(args.enrichment_output is not None)
    assert(args.alpha > 0 and args.alpha <= 1)
    
    if args.verbose >= 2:
        print 'calculating %s enrichment for foreground drugs from %s using %s method and the background from %s...' \
            %(args.database, args.foreground, args.method, args.background)

    # instantiate the Enrichment tool
    if args.verbose >= 2:
        print '  initalizing enrichment tool with database of type %s...' % args.database
    t = time()
    try:
        enr = EnrichmentCalculator(args.database, args.verbose)
    except ValueError as e:
        print 'Failed to initialise the Enrichment tool:'
        print e.__str__()
        print 'Exiting'
        exit(1)
    except IOError:
        print 'Failed to initialise the Enrichment tool'
        print 'Exiting'
        exit(1)
    e = time() - t
    if args.verbose >= 2:
        print '  done (took %.1f sec).' % e

    # initialize background
    if args.background != 'None' and args.background != 'ALL':
        # this awkward testing for the 'None' string is necessary (at least convenient) for Galaxy integration
        if args.verbose >= 2:
            print '  reading background drug file...'
        t = time()
        dic_returned = EnrichmentCalculator.parseCIDList(args.background)
        bg_score_dict = dic_returned["cid_score_dict"]
        bg = set(bg_score_dict.viewkeys())
        e = time() - t
        if args.verbose >= 2:
            print '  done (took %.1f sec).' % e
    else:
        bg = 'ALL'
    enr.setBackground(bg)

    # read input CID files for foreground
    if args.verbose >= 2:
        print '  reading & matching foreground drug file...'
    t = time()
    dic_returned = EnrichmentCalculator.parseCIDList(args.foreground)
    fg_score_dict = dic_returned["cid_score_dict"]
    # TODO this needs a better implementation .. should not be settable like that.
    enr.fg_name_dict = dic_returned["cid_name_dict"]
    # match foreground chemicals to the DB
    enr.matchForeground(fg_score_dict, args.annotation_output)
    e = time() - t
    if args.verbose >= 2:
        print '  done (took %.1f sec).' % e

    # calculate enrichments
    if args.verbose >= 1:
        print '  calculating enrichment of %s using the %s method' % (enr.db_type, args.method)
    t = time()
    (props, odds_r, n_r, p_val, p_adj) = enr.calcEnrichment(args.method, args.correction)

    with open(args.enrichment_output, 'w') as fout:
        # sort results by significance
        srt_idx = sorted(range(len(p_adj)), key=p_adj.__getitem__)
        props = [props[i] for i in srt_idx]
        odds_r = [odds_r[i] for i in srt_idx]
        n_r = [n_r[i] for i in srt_idx]
        p_val = [p_val[i] for i in srt_idx]
        p_adj = [p_adj[i] for i in srt_idx]

        # print header
        print >>fout, 'property\tdatabase\tcorrected p value\tp value\todds ratio\tn_r'
        # print significant enrichments
        for i, p in enumerate(p_adj):
            if p < args.alpha:
                print >>fout, '%s\t%s\t%g\t%g\t%f\t%s' %(props[i], args.database,p, p_val[i], odds_r[i], n_r[i])
    assert fout.closed
    e = time() - t
    if args.verbose >= 2:
        print '  done (took %.1f sec).' % e

    e = time() - st
    if args.verbose >= 1:
        print 'Enrichment calculation performed in %.1f sec.' %e


if __name__ == '__main__': __main__()
    
    

# use cases:
# python enrito.py -f fg_test1.txt -d 'target_STITCH'                        # took 309.6 sec in total
# python enrito.py -f fg_test1.txt -d 'target_DrugBank'                      # took 0.1 sec in total
# python enrito.py -f fg_test2.txt -d 'side-effect_SIDER'                    # took 9.3 sec in total
# python enrito.py -f fg_test3.txt -b bg_cmap_modules.txt -d 'target_STITCH' # took 114.6 sec in total
# python enrito.py -f fg_adrb.txt  -d 'target_STITCH'                        # took 310.5 sec in total
# python enrito.py -f fg_adrb.txt  -d 'target_DrugBank'                      # took 0.1 sec in total
