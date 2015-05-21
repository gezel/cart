import re
import math
import argparse
import os
import ConfigParser
# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.


def generateTabFormatFromEnrichmentOutputs(annotation_file,description_file,enrichment_results_file,header_js1,header_js2,index2,html_page_for_output):
    #build foreground dictionary (key chemical)
    foreground_annotation_map = {}
    cid_name_map = {}
    databases_used = []
    ##build the cid name mapping (@DICT)
    with open(annotation_file) as f:
        #next(f)
        for line in f:
            line = line.strip()
            el = line.split('\t')
            if el[0] == "CID" and el[1] == "Name":
                databases_used = el[2:]
            else:
                chemical_cid = el[0]
                chemical_name = el[1]
                if len(chemical_name) > 30:
                    chemical_name = chemical_name[:30]
                term_databases = el[2:]
                # Brauch man nicht aber naja .. 
                if chemical_cid != "NA":
                    cid_name_map[chemical_cid] = chemical_name
                    for term_category in term_databases:
                        terms = term_category.split(";")
                        for t in terms:
                            t = t.strip()
                            if t != "NA" and len(t) >= 1:
                                if t in foreground_annotation_map:
                                    foreground_annotation_map[t].append(chemical_cid)
                                else:
                                    foreground_annotation_map[t] = [chemical_cid]
                else:
                    print "ERROR : the CID column of the enrichment output contains a NA !!"
                            
    print databases_used
    term_name_dict = {}
    term_link_dict = {}
    term_db_dict = {}
    ##build the term description map (@DICT)
    ##build term name map (@DICT)
    ##build term db map (@DICT)
    print description_file 
    with open(description_file) as f:
        for line in f:
            el = line.split("\t")     
	    if len(el) < 4:
                print line
	        print el
            term_id = el[0].lower().strip()
            db = el[2].strip()
            description = el[3].strip()
            html_link = el[4].strip()
            if db != "Indications":
                if len(description) > 30:
                    description = description[:30]
                description = description.split(";")[0]
                term_name_dict[term_id] = description
                term_link_dict[term_id] = html_link
                term_db_dict[term_id] = db
        #print term_name_dict
        #print term_link_dict
        #print term_db_dict
        
    ##Build the term p value map (@DICT)
    ##Build the termp odd ratios map (@DICT)
    term_p_value_dict = {}
    term_odd_ratios_dict = {}
    with open(enrichment_results_file) as f:
        next(f)
        for line in f:
            el = line.split("\t")
            term = el[0]
            db = el[1]
            p_value = el[2]
            odds = el[4]
            if p_value == "inf":
                p_value = 10000
            if odds == "inf":
                odds = 10000
            term_p_value_dict[term] = p_value
            term_odd_ratios_dict[term] = odds
#    print term_p_value_dict
#    print term_odd_ratios_dict
#    print term_db_dict

    ##Now create the final html page
    ####First load index1.html
    final_html_file = ""
    #print len(final_html_file)
    with open(header_js1, 'r') as content_file:
        content1 = content_file.read()
        final_html_file = final_html_file + content1
        logo_targets_needed = True
        logo_classifications_needed = True
        logo_phenotypes_needed = True
        drugbank_done = False
        print "DEBUG: databases used are : " + str(databases_used)
        if ("drug-ATC-code" in databases_used) or ("drug-ATC-code-L1" in databases_used) or ("drug-ATC-code-L2" in databases_used) or ("drug-ATC-code-L3" in databases_used):
            final_html_file = final_html_file + "<br><br><img src=\"http://det.embl.de/~det/img/atc-ftc-logo.png\"  width=\"170\" height=\"60\" border=\"0\"><br>"
            final_html_file = final_html_file + "<input type=\"checkbox\" id=\"atc\" value=\"Yes\" checked>ATC "
            logo_classifications_needed = False
            print("Detected drug-ATC-code")

        if "chembl-ftc-drug-terms" in databases_used:
            if logo_classifications_needed:
                final_html_file = final_html_file + "<br><br><img src=\"http://det.embl.de/~det/img/atc-ftc-logo.png\"  width=\"170\" height=\"60\" border=\"0\"><br>"
                logo_classifications_needed = False
            final_html_file = final_html_file + "<input type=\"checkbox\" id=\"ftc\" value=\"Yes\" checked>FTC "
            print("Detected chembl-ftc-drug-terms")
        

        if "STITCH-drug-targets" in databases_used:
            final_html_file = final_html_file + "<br><br><img src=\"http://det.embl.de/~det/img/molecular-targets-logo.png\"  width=\"190\" height=\"65\" border=\"0\"><br>"
            final_html_file = final_html_file + "<input type=\"checkbox\" id=\"stitch\" value=\"Yes\" checked>STITCH "
            logo_targets_needed = False
            print("Detected STITCH-drug-targets")

        if "TTD-targets" in databases_used:
            if logo_targets_needed:
                final_html_file = final_html_file + "<br><br><img src=\"http://det.embl.de/~det/img/molecular-targets-logo.png\"  width=\"190\" height=\"65\" border=\"0\"><br>"
                logo_targets_needed = False
            final_html_file = final_html_file + "<input type=\"checkbox\" id=\"ttd\" value=\"Yes\" checked>TTD "
            print("Detected TTD-targets")

        if "drugbank-targets-action" in databases_used:
            if logo_targets_needed:
                final_html_file = final_html_file + "<br><br><img src=\"http://det.embl.de/~det/img/molecular-targets-logo.png\"  width=\"190\" height=\"65\" border=\"0\"><br>"
                logo_targets_needed = False
            final_html_file = final_html_file + "<input type=\"checkbox\" id=\"drugbank\" value=\"Yes\" checked>Drugbank "
            drugbank_done = True
            print("Detected drugbank-targets-action")
        
        if "drugbank-metabolization-action" in databases_used:
            if logo_targets_needed:
                final_html_file = final_html_file + "<br><br><img src=\"http://det.embl.de/~det/img/molecular-targets-logo.png\"  width=\"190\" height=\"65\" border=\"0\"><br>"            
                logo_targets_needed = False
            if not drugbank_done:
                final_html_file = final_html_file + "<input type=\"checkbox\" id=\"drugbank\" value=\"Yes\" checked>Drugbank "
                drugbank_done = True
                print("Detected drugbank-metabolization-action")
        
        if "toxicity_DrugMatrix" in databases_used:
            final_html_file = final_html_file + "<br><br><img src=\"http://det.embl.de/~det/img/adverse-drug-reactions-logo.png\"  width=\"170\" height=\"50\" border=\"0\"><br>"
            logo_phenotypes_needed = False
            final_html_file = final_html_file + "<input type=\"checkbox\" id=\"toxicity\" value=\"Yes\" checked>Toxicity "
            print("Detected toxicity_DrugMatrix")
            
        if "drug-side-effects" in databases_used:
            if logo_phenotypes_needed:
                final_html_file = final_html_file + "<br><br><img src=\"http://det.embl.de/~det/img/adverse-drug-reactions-logo.png\"  width=\"170\" height=\"50\" border=\"0\"><br>"
                logo_phenotypes_needed = False
            final_html_file = final_html_file + "<input type=\"checkbox\" id=\"sideeffect\" value=\"Yes\" checked>Side effect "    	
            print("Detected drug-side-effects")

        with open(header_js2, 'r') as content_file:
            content2 = content_file.read()
            final_html_file = final_html_file + content2
                
        
        ####Second load the enrichment terms information
        print 'assigning colors to terms ..'
        for term in term_p_value_dict:
    #        print term
            #if term_name_dict[term].lower() == "amenorrhoea":
            #    print "caca"
            db = term_db_dict[term.lower()]
            color="#A9A9F5";
            shape="ellipse";
            # @TODO toxicology teerms are not in the description file yet can appear as annotation and will remain with the color and shape of the target alike terms !!
            if db == "ATC" or db == "ChEMBL-FTC":
                color="#D0F5A9";
                shape="rectangle";
            if db == "SIDER" or db == "DrugMatrix":
                color="#F79F81";
                shape="triangle";
            #p_wert = str(math.log(float(term_p_value_dict[term]))/math.log(10))
            p_wert = str(term_p_value_dict[term])
            odd_wert = str(term_odd_ratios_dict[term])
            label = term_name_dict[term.lower()]
            if label == '':
                label = term
            final_html_file = final_html_file + "\n" + "{ data: { id: \'" + term + "\', label: \'" + label + "\', faveColor: \'" + color + "\', href:\'" + term_link_dict[term.lower()] + "\', faveShape: \'" + shape + "\', weight:30, db: \'" + term_db_dict[term.lower()] + "\', pval: " + p_wert + ", odds: " + odd_wert + " } },\n"
    ####Third load the chemical information
    print 'creating nodes and edges ..'
    all_cids = cid_name_map.keys()
    for cid in all_cids:
        final_html_file = final_html_file + "{ data: { id: \'" + cid +"\', label: \'" + cid_name_map[cid] + "\', faveColor: \'#848484\', href:\'http://stitch.embl.de/interactions/" + cid_name_map[cid].upper() + "?species=9606\', faveShape:\'roundrectangle\', weight:60, db:\'unfiltered\', pval: -10000, odds: 10000 } },\n"
    print len(final_html_file)
    final_html_file = final_html_file + "   ],\n    edges: [\n"
    print len(final_html_file)
    ####Fourth create the network
    network_tab = ""
    for term in term_p_value_dict:
        #########
        ######### CAREFUL !!! the term.upper() might be buggy !!
        #########
        chemicals = foreground_annotation_map[term]
        for cid in chemicals:
            
            network_tab = network_tab + "{ data: { source: \'" + term + "\', target: \'" + cid + "\' } },\n";
    network_tab = network_tab.strip()               
    final_html_file = final_html_file + '\n' + network_tab
    print len(final_html_file)
    ####Fifth load index1.html
    print 'printing footer to final html output ..'
    with open(index2, 'r') as content_file:
        content = content_file.read()
        final_html_file = final_html_file + content
    print 'printing final string to final html ..'
    f = open(html_page_for_output,'w')
    f.write(final_html_file)
    f.close()


if __name__ == '__main__': 
    #annotation_res_ex = "/Users/deghou/desktop/annotation-res.tab"
    #enrichment_res_ex = "/Users/deghou/desktop/enrichment-res.tab"
    #description_file_ex = "/Users/deghou/desktop/description-file.tab"
    #index1 = "/Users/deghou/Desktop/index1.html"
    #index2 = "/Users/deghou/Desktop/index2.html"
    parser = argparse.ArgumentParser(description='Generates a HTML page rendering an interactive network', version='0.1')
    parser.add_argument('-a', '--annotations', type=str, help='annotation file (enrichment output)')
    parser.add_argument('-e', '--enrichments', type=str, help='enrichment file (enrichment output)')
    parser.add_argument('-o', '--final_html_output', type=str, help='final html output') 
	#generateTabFormatFromEnrichmentOutputs(annotation_res_ex,description_file_ex, enrichment_res_ex,index1,index2)
    args = parser.parse_args()
    cfg_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../conf/settings.cfg')
    cfg = ConfigParser.ConfigParser()
    cfg.read(cfg_file)
    description_file = cfg.get('visualization', 'description_file')
    header_js1 = cfg.get('visualization','header_js1')
    header_js2 = cfg.get('visualization','header_js2')
    
    footer_js = cfg.get('visualization','footer_js')
    generateTabFormatFromEnrichmentOutputs(args.annotations,description_file,args.enrichments,header_js1,header_js2,footer_js,args.final_html_output)
    
