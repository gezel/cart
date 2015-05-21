##################################################################
###########  REQUIRED PARAMETERS TO BE SET BY THE USER ###########
##################################################################
####################
#### Foreground ####
####################
fn_fg=cmap_foreground_codim2.tsv

##################################################################
###########     GENERAL PARAMETERS : DO NOT MODIFY     ###########
##################################################################
####################
#Installation folder
####################
cur_dir=`pwd`
CART_INSTALLATION_DIRECTORY="$(dirname "$cur_dir")"
####################
####  verbose   ####
####################
verbose_level=2
####################
## results output ##
####################
out_dir="example_out"

##################################################################
###########  OPTIONAL PARAMETERS TO BE SET BY THE USER ###########
##################################################################

#################### Name Matching module related
####################
#### Background ####
####################
fn_bg=cmap_background.tsv
####################
#Output foreground #
####################
out_nm_fg=${out_dir}/"out-nm-${fn_fg}"
####################
#Output background #
####################
out_nm_bg=${out_dir}/"out-nm-${fn_bg}"
####################
####    Fuzzy   ####
####################
fuzzy=true
####################
####  Heuristic ####
####################
heuristic=true
####################
####  Universe  ####
####################
universe=STITCH

#################### Enrichment module related
####################
#### Databases  ####
####################
dbs="drug-ATC-code-L3,STITCH-drug-targets,drug-side-effects"
####################
####   alpha    ####
####################
alpha="0.05"
####################
####   method   ####
####################
method="Fisher"
####################
#### correction ####
####################
correction="FDR"
####################
## final output enr
####################
out_enr_enr_final=${out_dir}/"out-enr-enr-final.tsv"
####################
## final output ann
####################
out_enr_ann_final=${out_dir}/"out-enr-ann-final.tsv"

#################### Visualization module related (table with http link)
####################
####   output   ####
####################
cart_interactive_table=${out_dir}/"cart-interactive-table.html"

#################### Visualization module related (intereactive network generator)
####################
####   output   ####
####################
cart_interactive_network=${out_dir}/"cart-interactive-network.html"

#################### Synonyms module related
####################
####  synonyms  ####
####################
synonym_option=false


##################################################################
###########                       RUN                  ###########
##################################################################
# prepare
if [ -d $out_dir ];
    then
        echo "${out_dir} already exist ! Choose another directory name where results will be outputed or delete the directory ${out_dir}"
        exit
    else
        mkdir $out_dir
fi
dbs=(${dbs//,/ })
# match foreground

python2.7 ../src/name_matching.py -n ${fn_fg} -o ${out_nm_fg} -a ${fuzzy} -e ${heuristic} -s ${synonym_option} --verbose ${verbose_level}
if [[ $fn_bg == "NULL" ]]
then
  out_nm_bg="ALL"
else
  # match background
  python2.7 ../src/name_matching.py -n ${fn_bg} -o ${out_nm_bg} -a ${fuzzy} -e ${heuristic} -s ${synonym_option} --verbose ${verbose_level}
fi
# perform enrichment calculation for each database
echo -e 'property\tdatabase\tcorrected p value\tp value\todds ratio\tn_r' > ${out_enr_enr_final}
col_ent=`mktemp /tmp/XXXXXXXXXX`
tmp_ann=`mktemp /tmp/XXXXXXXXXX`
touch ${out_enr_ann_final}
for i in "${!dbs[@]}"
do
  db=${dbs[i]}
 ### create tmp files (one for the enrichment and one for the annotation)
  file_enr=`mktemp /tmp/XXXXXXXXXX`
  file_ann=`mktemp /tmp/XXXXXXXXXX`
  python2.7 ../src/enrichment_calculation.py -f ${out_nm_fg} -b ${out_nm_bg} -d $db -o ${file_enr} -p ${file_ann} -a ${alpha} -m ${method} -c ${correction} --verbose ${verbose_level}
  tail -n +2 ${file_enr} >> ${out_enr_enr_final}
  cut -f3 ${file_ann} > $col_ent
  paste ${out_enr_ann_final} $col_ent > $tmp_ann
  mv $tmp_ann ${out_enr_ann_final}
  echo `head ${out_enr_ann_final}`
done
cut -f1,2 ${file_ann} > $col_ent
paste $col_ent ${out_enr_ann_final} > $tmp_ann
mv $tmp_ann ${out_enr_ann_final}

## visualization table
python2.7 ../src/result_annotator.py -i ${out_enr_enr_final} -o ${cart_interactive_table}
## visualization network
python2.7 ../src/network_generator.py -a ${out_enr_ann_final} -e ${out_enr_enr_final} -o ${cart_interactive_network}
