import egglib.io as eggo
import egglib.stats as stats
import sys

ingroup = {1: {1: {0: [0],1: [1], 2: [2], 3: [3], 4: [4], 5: [5], 6: [6], 7: [7], 8: [8], 9: [9]}, 2: {10: [10], 11: [11], 12: [12], 13: [13], 14: [14], 15: [15], 16: [16], 17: [17], 18: [18], 19: [19]} }}
pop_structure = stats.make_structure(ingroup, None)

vcf = sys.argv[1]
vcf_parser = eggo.VcfParser(vcf)

sliding_window = vcf_parser.slider(3000, 3000)

compute = stats.ComputeStats()
compute.configure(struct=pop_structure, multi=False)
compute.add_stats("Dxy")
compute.add_stats("Fst")
compute.add_stats("Pi")
compute.add_stats("D")
compute.add_stats("Da")
compute.add_stats("Fs")
compute.add_stats("S")
compute.add_stats("thetaW")
while sliding_window.end_bound != 59999:
	sliding_window.next()
	print(sliding_window.num_sites)
	print(compute.process_sites(sliding_window, struct=pop_structure))

