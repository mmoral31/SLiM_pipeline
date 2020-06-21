# Software pipeline for running evolutionary statistics on genomic data from SLiM divergence simulations

> Requirements:
>
> - SLiM-pipeline package (cloned from https://github.com/mmoral31/SLiM-pipeline.git)
> - Python 2.7
> - SLiM 3.4
> - Jinja 2.11.x
> - EggLib 3.0.0b21
> - BCFtools (run on v1.9)
> - SAMtools and HTSlib



#### Introduction:

---

	SLiM is a powerful evolutionary simulation software with sequence-based genome evolution functionality allowing for the creation of genomic data for downstream evolutionary analysis. Despite this, the ability for iteratively altering the parameters of simulations and parallelizing multiple simulations concurrently are unavailable. In creating the SLiM-pipeline package, we provide this functionality and include downstream analyses for calculating evolutionary statistics on simulated genomic data.

#### Installation:

---

This section will outline the installation of all prerequisite software and the cloning of the SLiM-pipeline Github. Most prerequisites will be installed within a unique Python 2.7 conda environment for ease of access.

1. Create and activate a unique Python 2.7 conda environment

```bash
conda create -n SLiM python=2.7
```

```
conda activate SLiM
```

2. Install the most recent version of BCFtools using conda

```bash
conda install bcftools
```

3. Install the most recent version of Jinja2 using pip

```bash
pip install Jinja2
```

4. Install SLiM from source. Requires downloading the source code from https://messerlab.org/slim/

```bash
cd SLiM
cd ..
mkdir build
cd build
cmake ../SLiM
make slim
make install slim
```

5. Install Egglib from the bioconda channel using conda

```
conda install -c bioconda egglib
```

6. Install Samtools and HTSLib from source. Requires downloading the source code of samtools from http://www.htslib.org/download/

```bash
cd samtools-1.x
./configure --prefix=/where/to/install
make
make install
```

```bash
cd htslib
./configure --prefix=/where/to/install
make
make install
```

7. Clone in the SLiM-pipeline package from the Github repository https://github.com/mmoral31/SLiM_pipeline

```bash
git clone https://github.com/mmoral31/SLiM_pipeline
```

#### Usage:

---

The entire simulation pipeline is run in Python using the simulation_pipeline function of the simulation_pipeline module in the SLiM_pipeline package. Because the entire pipeline is run through a single Python function, the user should create a custom Python script that calls the simulation_pipeline function with a desired set of parameters. The default parameters are listed below. An example Python script can be found in the SLiM_pipeline package (example_runfile.py).

```python
from SLiM_pipeline.simulation_pipeline import simulation_pipeline

simulation_pipeline(simtype, recombination = 0, gfp1 = 0, gfp2 = 0, pop1 = 500, pop2 = 500, mrcoding = 2.5e-6, mrnoncoding = 2.5e-6, generations = 5000, samplingnum = 4, numsamples = 10, simnum = 20)
```

| Parameters    | Description                                                  | Data type |
| ------------- | ------------------------------------------------------------ | --------- |
| simtype       | Used to determine which simulation file to run. Will be substituted into {{simtype}}_template.slim | string    |
| recombination | Rate of recombination for genomes of all individuals in each population | float     |
| gfp1          | Gene flow from population one to population two              | float     |
| gfp2          | Gene flow from population two to population one              | float     |
| pop1          | Size of population one                                       | int       |
| pop2          | Size of population two                                       | int       |
| mrcoding      | Mutation rate of coding regions of all individuals in each population | float     |
| mrnoncoding   | Mutation rate of noncoding regions of all individuals in each population | float     |
| generations   | Number of generations to run SLiM simulation                 | int       |
| samplingnum   | Number of generations to sample at (made in equally-spaced increments until the generation specified by the **generations** parameter) | int       |
| numsamples    | Number of individuals to sample at specified sampling generations | int       |
| simnum        | Number of simulations to parallelize for a single simtype (**NOTE: this will specify both the number of simulations run and the number of cores on which the simulations will be run**) | Int       |



The rest of this manual will not be run by the user but is automatically run by the *simulation_pipeline.py* Python script.

#### The SLiM-pipeline package documentation

---

##### Components:

- simulation-pipeline.py
- egglib_script.py
- regions.txt
- templates
  - commands-template.txt
  - commands2-template.txt
  - pipeline-template.sh
  - ps-template.slim

There are four primary steps in this pipeline: (1) substitution of parameter values into the four template files, (2) running the evolutionary simulations through SLiM, (3) calculating evolutionary statistics using EggLib, and (4) converting output files into CSV format.

##### <u>1. Substitution of parameter values into the four template files</u>

	To run a SLiM simulation, the user is required to supply a unique **.slim** script that uses the program-specific Eidos scripting language. Because no parameter values other than this script are supplied to the *slim* function, parameters must be instantiated directly in the .slim script. This makes the process of iteratively changing parameter values difficult as the text within the script must be altered directly. To allow for this functionality, we used the *Jinja2* Python software which can substitute snippets of text (in our case parameter values) into user-created templates. Four template files are used in this pipeline:

- **ps-template.slim** - Unique .slim script for input into SLiM
- **pipeline-template.sh** - Bash script for running analyses in steps 2-4
- **commands-template.txt** - Text file used to parallelize SLiM simulations
- **commands2-template.txt** - Text file used to parallelize evolutionary statistic calculation

| Template               | Parameters substituted into template                         |
| ---------------------- | ------------------------------------------------------------ |
| ps-template.slim       | Recombination rate, gene flow from population one, gene flow from population two, size of population one, size of population two, mutation rate of coding regions, mutation rate of noncoding regions, sampling times, number of samples per sampling |
| pipeline-template.sh   | Number of simulations, sampling times                        |
| commands-template.txt  | Number of simulations                                        |
| commands2-template.txt | Number of simulations, sampling times                        |

	The pipeline is initiated when the Python wrapper script *simulation-pipeline.py* is called with the parameter values to substitute (see Usage below). Using *Jinja2*, these parameter values are substituted into the appropriate positions using a respective code block for each template.

e.g. Code block for substituting into the template SLiM script

```python
from jinja2 import Environment, PackageLoader
env = Environment(loader=PackageLoader('SLiM-pipeline', 'templates'))
sim_temp_file = simtype + '-template.slim'
sim_template = env.get_template(sim_temp_file)
sim_rendered = sim_template.render(recombination=recombination, gfp1=gfp1, gfp2=gfp2, pop1=pop1, pop2=pop2, mrcoding=mrcoding, mrnoncoding=mrnoncoding, samples=samples, numsamples=numsamples)
sim_final_file = open(simtype + ".slim", "w")
sim_final_file.write(sim_rendered)
sim_final_file.close()
```

##### <u>2. Running evolutionary simulations through SLiM</u>

Using the subprocess module, the Bash script *pipeline.sh* is called within the *simulation_pipeline.py* script with the simtype and resulting CSV name of the simulation:

```python
downstream = subprocess.Popen(['bash', 'pipeline.sh', simtype, csv_name])
```

After setting up directory structure for the simulations, *xargs* is used to run an established number of simulations using the evolutionary software SLiM:

> (before Jinja2 substitution)

```bash
cat commands.txt | xargs -n {{ simnum }} -P {{ simnum }} -I CMD bash -c CMD;
```

> (after Jinja2 substitution with simnum = 3)

```bash
cat commands.txt | xargs -n 3 -P 3 -I CMD bash -c CMD;
```

This Bash command uses the text file *commands.txt* to parallelize SLiM simulations on a specified number of processes.

**NOTE: The number of lines in the *commands.txt* file will be both the number of simulations parallelized and the number of cores on which to run these simulations.**

> (before Jinja2 substitution)

```bash
{% for i in range(1,simnum+1) %}
cd {{ simtype }}-{{ i }}; slim -l {{ simtype }}.slim > {{ simtype }}-{{ i }}-results.txt; cd ..;
{% endfor %}
```

> (after Jinja2 substitution with simnum = 3 and simtype = 'ps')

```bash
cd ps-1; slim -l ps.slim > ps-1-results.txt; cd ..;
cd ps-2; slim -l ps.slim > ps-2-results.txt; cd ..;
cd ps-3; slim -l ps.slim > ps-3-results.txt; cd ..;
```

Each line will run the same SLiM script through the SLiM software which is defined by the simtype given when running the initial Python script *simulation_pipeline.py*. In the given example, the simtype 'ps' will substitute parameters into the *ps-template.slim* file which will create a new file *ps.slim*. New template SLiM scripts can be created to reflect alternate fitness calculations, alternate genome sizes and regions, or any other parameter which cannot be given to the initial *simulation_pipeline.py* script.

The output from these simulations will be VCF files output at specified generations, sampling a specified number of individuals from each population. The sampling generations can be changed by altering the **generations** and **samplingnum** parameters of the *simulation_pipeline.py* script and the number of sampled individuals can be changed by altering the **numsamples** parameter.

##### <u>3. Calculating evolutionary statistics using EggLib</u>

The next step in the Bash script *pipeline.sh* is to calculate evolutionary statistics on the resulting VCF files using *Egglib.IO*. This process is also parallelized using *xargs*:

> (before Jinja2 substitution)

```bash
cat commands2-{{ sample }}.txt | xargs -n {{ simnum }} -P {{ simnum }} -I CMD bash -c CMD;
```

> (after Jinja2 substitution with sample = 1250 and simnum = 3)

```bash
cat commands2-1250.txt | xargs -n 3 -P 3 -I CMD bash -c CMD;
```

Because statistics will be calculated on a series of sampled generations, this Bash command will be called for each sampled generation. Jinja2 substitution will substitute parameters into the *commands2-template.txt* file to create multiple commands text files (e.g. with generations = 5000 and sampnum = 4; commands2-1250.txt, commands2-2500.txt, commands2-3750.txt, commands2-5000.txt):

> (before Jinja2 substitution)

```bash
{% for i in range(1,simnum+1) %}
cd {{ simtype }}-{{ i }}; bgzip {{ simtype }}_{{ sampgen }}p1.vcf; bgzip {{ simtype }}_{{ sampgen }}p2.vcf; bcftools index {{ simtype }}_{{ sampgen }}p1.vcf.gz; bcftools index {{ simtype }}_{{ sampgen }}p2.vcf.gz; bcftools merge {{ simtype }}_{{ sampgen }}p1.vcf.gz {{ simtype }}_{{ sampgen }}p2.vcf.gz -0 --force-samples > {{ simtype }}_{{ sampgen }}p.vcf; python egglib_script.py {{ simtype }}_{{ sampgen }}p.vcf > egglib-{{ sampgen }}_results; cd ..
{% endfor %}
```

> (after Jinja2 substitution with simnum = 3, simtype = 'ps', and gen = 1250)

```bash
cd ps-1; bgzip ps_1250p1.vcf; bgzip ps_1250p2.vcf; bcftools index ps_1250p1.vcf.gz; bcftools index ps_1250p2.vcf.gz; bcftools merge ps_1250p1.vcf.gz ps_1250p2.vcf.gz -0 --force-samples > ps_1250p.vcf; python egglib_script.py ps_1250p.vcf > egglib-1250_results; cd ..
cd ps-2; bgzip ps_1250p1.vcf; bgzip ps_1250p2.vcf; bcftools index ps_1250p1.vcf.gz; bcftools index ps_1250p2.vcf.gz; bcftools merge ps_1250p1.vcf.gz ps_1250p2.vcf.gz -0 --force-samples > ps_1250p.vcf; python egglib_script.py ps_1250p.vcf > egglib-1250_results; cd ..
cd ps-3; bgzip ps_1250p1.vcf; bgzip ps_1250p2.vcf; bcftools index ps_1250p1.vcf.gz; bcftools index ps_1250p2.vcf.gz; bcftools merge ps_1250p1.vcf.gz ps_1250p2.vcf.gz -0 --force-samples > ps_1250p.vcf; python egglib_script.py ps_1250p.vcf > egglib-1250_results; cd ..
```

Each line will index the resulting VCF files from the respective simulation for each population, will merge those indexed VCFs, and will run the *egglib_script.py* Python script to calculate evolutionary statistics on merged VCFs. Egglib.IO requires a unique Python script to be created to run specified sliding window evolutionary statistics on input data. The current script *egglib_script.py* is established to run S, Fs, Fst, D, Dxy, thetaW, Pi, and Da on VCF files from genomes with 10 coding and 10 noncoding regions of length 3000bp for a total genome size of 60000bp. If different evolutionary statistics need to be calculated or the default genome parameters are not the same as those run for the SLiM simulations, the *egglib_script.py* must be altered directly.

The output of Egglib.IO is a text file with statistic values for each evolutionary statistic by region:

```python
257
{'S': 245, 'Fs': -6.206779297027814, 'Fst': 0.3385505310554323, 'D': -1.0859247152249074, 'Dxy': 0.19942857142857132, 'thetaW': 57.5990410246945, 'Pi': 40.80128205128197, 'Da': 0.06751664876476896}
271
{'S': 250, 'Fs': -5.424789604635091, 'Fst': 0.2934577008559135, 'D': -1.306633633729367, 'Dxy': 0.17807999999999985, 'thetaW': 58.774531657851526, 'Pi': 38.15512820512817, 'Da': 0.05225894736842088}
274
{'S': 260, 'Fs': -5.732559889531498, 'Fst': 0.30774832282354403, 'D': -1.0856910028125963, 'Dxy': 0.19598076923076885, 'thetaW': 61.12551292416559, 'Pi': 43.315384615384495, 'Da': 0.060312753036436795}
```

##### 
