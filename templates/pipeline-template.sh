for i in {1..{{ simnum }}}; do mkdir $1-$i; done;
for i in {1..{{ simnum }}}; do cp $1.slim ./$1-$i; done;
cat commands.txt | xargs -n {{ simnum }} -P {{ simnum }} -I CMD bash -c CMD;
for i in {1..{{ simnum }}}; do cp egglib_script.py ./$1-$i; done;
for i in {1..{{ simnum }}}; do cp regions.txt ./$1-$i; done;
echo 'Start evolutionary statistic calculation';
{% for sample in samples %}
cat commands2-{{ sample }}.txt | xargs -n {{ simnum }} -P {{ simnum }} -I CMD bash -c CMD;
echo 'Next step';
for i in {1..{{ simnum }}}; do cd $1-$i; awk -F" " '/^\{/' egglib-{{ sample }}_results | sed 's/[A-Za-z]*//g' | awk -F" " '{print $2 $4 $6 $8 $10 $12 $14 $16}' | sed 's/.$//' | sed '1iS,Fs,Fst,D,Dxy,thetaW,Pi,Da,Region' | paste -d "," /dev/stdin regions.txt > $2_sampgen={{ sample }}_run=$i.csv; cd ..; done;
{% endfor %}
echo 'Pipeline complete';
