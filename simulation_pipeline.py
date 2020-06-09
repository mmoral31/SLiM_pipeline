def simulation_pipeline(simtype, recombination = 0, gfp1 = 0, gfp2 = 0, pop1 = 500, pop2 = 500, mrcoding = 2.5e-6, mrnoncoding = 2.5e-6, generations = 5000, samplingnum = 4, numsamples = 10, simnum = 20):

	import os
	import random
	import subprocess
	sim_id = random.randrange(0, 100000)
	new_sim_dir = './' + simtype + '-' + str(sim_id)
	os.mkdir(new_sim_dir)
	copy = subprocess.Popen(['cp', '-r', 'SLiM_pipeline', './' + new_sim_dir])
	copy.wait()
	os.chdir(new_sim_dir)
	regions = subprocess.Popen(['mv', 'SLiM_pipeline/regions.txt', '.'])
	regions.wait()
	egglib = subprocess.Popen(['mv', 'SLiM_pipeline/egglib_script.py', '.'])
	egglib.wait()

	samples = [None] * samplingnum
	for i in range(samplingnum):
		samples[i] = int((i+1)*(generations/samplingnum))

	csv_name = simtype + "-" + str(sim_id) + "_recom=" + str(recombination) + "_gfp1=" + str(gfp1) + "_gfp2=" + str(gfp2) + "_pop1=" + str(pop1) + "_pop2=" + str(pop2) + "_mrcod=" + str(mrcoding) + "_mrnc=" + str(mrnoncoding) + "_gen=" + str(generations) + "_sampn=" + str(samplingnum) + "_nsamp=" + str(numsamples)

	from jinja2 import Environment, PackageLoader
	env = Environment(loader=PackageLoader('SLiM_pipeline', 'templates'))
	sim_temp_file = simtype + '-template.slim'
	sim_template = env.get_template(sim_temp_file)
	sim_rendered = sim_template.render(simtype=simtype, recombination=recombination, gfp1=gfp1, gfp2=gfp2, pop1=pop1, pop2=pop2, mrcoding=mrcoding, mrnoncoding=mrnoncoding, samples=samples, numsamples=numsamples)
	sim_final_file = open(simtype + ".slim", "w")
	sim_final_file.write(sim_rendered)
	sim_final_file.close()
	c1_template = env.get_template('commands-template.txt')
	c1_rendered = c1_template.render(simnum=simnum, simtype=simtype)
	c1_final_file = open('commands.txt', 'w')
	c1_final_file.write(c1_rendered)
	c1_final_file.close()

	samples = [None] * samplingnum
	for i in range(samplingnum):
		samples[i] = int((i+1)*(generations/samplingnum))

	c2_template = env.get_template('commands2-template.txt')
	for sample in samples:
		c2_rendered = c2_template.render(simnum=simnum, sampgen=sample, simtype=simtype)
		c2_final_file = open('commands2-' + str(sample) + '.txt', 'w')
		c2_final_file.write(c2_rendered)
		c2_final_file.close()

	samples = [None] * samplingnum
	for i in range(samplingnum):
		samples[i] = int((i+1)*(generations/samplingnum))

	pipe_template = env.get_template('pipeline-template.sh')
	pipe_rendered = pipe_template.render(simnum=simnum, samples=samples)
	pipe_final_file = open('pipeline.sh', 'w')
	pipe_final_file.write(pipe_rendered)
	pipe_final_file.close()

	downstream = subprocess.Popen(['bash', 'pipeline.sh', simtype, csv_name])
	downstream.wait()
	os.chdir('./..')
