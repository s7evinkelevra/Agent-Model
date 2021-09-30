from Bio.Seq import Seq
from matplotlib.ticker import LinearLocator
from matplotlib import cm
import random
from pprint import pprint
import itertools
from collections import deque
import uuid
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time


rng = np.random.default_rng()

# Random base sequence of length


def randomDNAseq(length):
  return ''.join(random.choice('GCAT') for _ in range(length))

# Random proteinogenic amino acids sequence of length


def randomASseq(length):
  return ''.join(random.choice('ACDEFGHIKLMNOPQRSTUVWY') for _ in range(length))

# Random bitstring


def randomBitseq(length):
  return ''.join(random.choice('01') for _ in range(length))

# Generate allele with unique id and random position in peptide space


def randomPSallele(peptide_space_length):
  return {
      "x": rng.integers(low=1, high=peptide_space_length),
      "y": rng.integers(low=1, high=peptide_space_length),
      "id": uuid.uuid4()
  }


def sliding_window_iter(seq, width):
  it = iter(seq)
  result = tuple(itertools.islice(it, width))
  if len(result) == width:
    yield result
  for elem in it:
    result = result[1:] + (elem,)
    yield result

# Sliding window iterator over sequence seq and of window width of n


def window(seq, n=2):
    it = iter(seq)
    win = deque((next(it, None) for _ in range(n)), maxlen=n)
    yield win
    append = win.append
    for e in it:
        append(e)
        yield win



start_time = time.perf_counter_ns()

peptide_space_length = 1000

host_n = 10000
host_allele_initial_n = 150
host_allele_length = 9

host_fitness_initial = 1
host_fitness_increment = 0.2

host_species_n = 1


pathogen_n = 100000
pathogen_haplotype_initial_n = 400
pathogen_haplotype_length = 100

pathogen_fitness_initial = 1
pathogen_fitness_increment = 1

pathogen_species_n = 1

host_allele_pool = [[randomPSallele(peptide_space_length) for _ in range(
    host_allele_initial_n)] for _ in range(host_species_n)]


def generateHost():
  species = random.choice(range(host_species_n))
  allele_1_data = random.choice(host_allele_pool[species])
  allele_2_data = random.choice(host_allele_pool[species])
  return {
      "species": species,
      "fitness": host_fitness_initial,
      "allele_1_id": allele_1_data["id"],
      "allele_1_x": allele_1_data["x"],
      "allele_1_y": allele_1_data["y"],
      "allele_2_id": allele_2_data["id"],
      "allele_2_x": allele_2_data["x"],
      "allele_2_y": allele_2_data["y"]
  }


host_data = [generateHost() for _ in range(host_n)]

hosts = pd.DataFrame(host_data)

pathogen_haplotype_pool = [[randomPSallele(peptide_space_length) for _ in range(
    pathogen_haplotype_initial_n)] for _ in range(pathogen_species_n)]


def generatePathogen():
  species = random.choice(range(pathogen_species_n))
  haplotype = random.choice(pathogen_haplotype_pool[species])
  return {
      "species": species,
      "fitness": pathogen_fitness_initial,
      "haplotype_id": haplotype["id"],
      "haplotype_x": haplotype["x"],
      "haplotype_y": haplotype["y"]
  }


pathogen_data = [generatePathogen() for _ in range(pathogen_n)]

pathogens = pd.DataFrame(pathogen_data)

print(f'host count - {len(hosts)}')
print(f'host allele count (unique) - {len(hosts.allele_1_id.unique())}')

print(f'pathogen count - {len(pathogens)}')
print(
    f'pathogen haplotype count (unique) - {len(pathogens.haplotype_id.unique())}')

sim_gen_n = 10000
sim_logging_interval = 50

sim_allele_subsample_n = 100


def uniqueAlleleCount():
  print("yeee")


"""
print(hosts[['allele_1_id', 'allele_2_id']].value_counts())
print(hosts[['allele_1_id', 'allele_2_id']].values.ravel('K'))
print(len(pd.unique(hosts[['allele_1_id', 'allele_2_id']].values.ravel('K'))))

host_allele_all = hosts[['allele_1_id', 'allele_2_id']].values.ravel('K')
unique, counts = np.unique(host_allele_all, return_counts=True)
# print(np.asarray((unique,counts)).T)
print(counts)
plt.bar([str(i)[10:15] for i in unique], counts)
"""


def eucDist(x0, y0, x1, y1):
  dX = x1 - x0
  dY = y1 - y0
  return np.sqrt(dX*dX + dY * dY)


def infect(host):
  infecting_pathogen = pathogens.sample()
  dist1 = eucDist(host["allele_1_x"], host["allele_1_y"],
                  infecting_pathogen["haplotype_x"], infecting_pathogen["haplotype_y"])
  dist2 = eucDist(host["allele_2_x"], host["allele_2_y"],
                  infecting_pathogen["haplotype_x"], infecting_pathogen["haplotype_y"])
  min_dist = np.min([dist1, dist2])

  if(min_dist < 200):
    return host["fitness"] - host_fitness_increment
  else:
    return host["fitness"]



""" 
for i in range(sim_gen_n):
  # log every sim_logging_interval'th generation
  if(i % sim_logging_interval == 0):
    print("logging data")

  # infection regieme
  ## each host is infected between 1 and n times
  infecting_pathogen_species = 0
  hosts["fitness"] = hosts.apply(infect, axis=1)
  print(hosts)
  break
 """
end_time = time.perf_counter_ns()

print((end_time-start_time) / 1000)