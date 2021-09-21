# Agent based Model V1

**Question:** What drives the landmark features of classical MHC-I genes (**high polymorphism**/TSP/positive selection at the PBD)?

**Hypothesis:** [Fluctuating selection as important driver of MHC-I polymorphism, co-evolution possibly only minor effect]

**Approach:** Create an agent-based (hosts and parasites as entities) simulation model that can approximate the interaction between multiple hosts and parasites and is able control and integrate the effects of different balancing selection mechanisms (HA/NFDS/FS) and multi-species co-evolution acting on the selection of MHC genes.

```bash
python src/model.py # to run the model
```

## Introduction

[WIP]

## The Model

An agent based model simulates actions and interactions of autonomous agents (hosts and parasites) to investigate the behavior of a complex system (i.e. allele frequencies) [[wiki](https://en.wikipedia.org/wiki/Agent-based_model)]. [Complex behavior can arise from these interaction despite simple rules for the singular agent](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life).

The model is similarly structured to [Lighten et al 2017][Lighten], but with the addition of multiple host- and parasite species with different infection regimes (representing fluctuating selection). As noted in [Ejsmond 2018][Ejsmond], the co-evolution of host-parasite does not account for the high allele count; the introduction of (random/) novel parasites each generation was neccessary (and sufficient!) to drive the high number of alleles. This random seeding of parasites does not seem biologically plausible ("[...] ≈100 entirely new, typically very divergent [parasite] haplotypes in a population of 10,000 individuals."). A more plausible mechanism, similar in effect, could be fluctuating selection: novel parasites don't appear randomly, but fluctuate in time and space and are drawn from a big (but not infinite) pool of parasites (epitopes).

## Input
  - Number of host/parasite "species" (pools to draw alleles from)
    - [Lighten][Lighten]: 1 host species, 1 parasite species
    - [Ejsmond][Ejsmond]: 1 host species, 10 parasites species -> but how is that species defined? All parasites species are generated randomly and selected randomly for infection -> in effect just a bigger pool of parasites?
  - Initial population sizes (population size remains constant during simulation)
    - [Lighten][Lighten]: 10<sup>2</sup> - 10<sup>4</sup> === # of hosts === # of parasites
    - [Ejsmond][Ejsmond]: 10<sup>2</sup> - 10<sup>5</sup> === # of hosts === # of parasites
  - Number of alleles per population
    - Both: 2 random alleles per individual -> 1000 pop == 2000 for the hosts, 1000 for the parasites (!not clear! triple check -> check in matlab by changing the plotting starting point to the first generation)
  - MHC promiscouity (constant or distribution for random initialization)
    - Both: constant/not considered -> fitness is determined relatively
  - Epitope/paratope space size
    - Both: 1000*1000 units
  - Infection regime
    - [Lighten][Lighten]: Each host is infected by one random parasite each generation
    - [Ejsmond][Ejsmond]: Each host is infected by one random parasite drawn from the 10 available parasite species each generation (!not clear!: so only one 10th of parasites are involved each generation?)
  - Fitness increments for the host (-> defines generation time, see host section)
    - Both: 0.25 -> host generation time == 4 * parasite generation time
  - Relative fitness value -> ratio of surviving/dying hosts/parasites
    - Both: top 50 % hosts are resistent (gain 0.25 fitness), bottom 50 % of host are susceptible (loose 0.25 fitness)
    - Both: top 50 % parasites survive (and reproduce), bottom 50 % of die
  - Reproduction regime
    - Both:
      - Hosts with a fitness > 1 reproduce
        1. Produce 2 gamets with one haplotype each
        2. All gametes are paired in two and fuse, generating new Hosts
      - Parasite that survive reproduce two clonal offsring each
  - Mutation rates for hosts and parasites
    - [Lighten][Lighten]: 10<sup>-1</sup> -> expected heterozygosity of ≈1 with a population size of 10<sup>3</sup>-10<sup>4</sup>
    - [Ejsmond][Ejsmond]: down to 10<sup>-4</sup> (upper bound for MHC mutation rate)
  - Co-Evolution ("Red Queen dynamics" -> selection of parasites based on their relative fitness + mutation)
  - Random pathongen seeding (as control)
    - [Lighten][Lighten]: 100 parasites with random haplotype per generation
  - Strength of NFDS -> magnitude of fitness boost for rare alleles (curve?)
  - Strength of HA/DAA -> implicit in the fitness calculation
  - Strength of FS -> indirectly through infection/reproduction regime
  - Simulation runtime (in generations)
    - [Ejsmond][Ejsmond]: 10600

## Output
  - Host/parasite genotype coordinate in epitope/paratope space over time
  - Allele count / effective number of alleles (allele count from a defined subset ob individuals)
  - Allele tracking information (unique id) (TSP)
  - Supertype information -> assigned when first generated (?)
  - Average fitness over time for alleles vs allele count

## Components

The model has a number of components which can interact with each other. Firstly, the agents. They are the effective unit of the simulation and posses a set of properties (such as alleles) and rules ("reproduce when fitness reaches threshold") and update their properties and act on their rules once each simulation cycle. Secondly, there are infection regime, reproduction regime and the epitope/paratope space (fitness calculation), which describe the environment the agents act in.

### Agents

#### Host

The host is a diploid organism that can reproduce sexually. With whom the host reproduces is determined by the reproduction regime and when is dependent on host fitness. A host can carry one or more MHC loci with 2 alleles each. If there are 2 or more loci, linkage/recombination could be considered.

The hosts alleles represent the Peptide Binding Domain (PBD) of MHC-I molecule, which can bind to a repertoire of epitopes. The size of that repertoire is the promiscuity of that MHC-I variant. Which epitopes the MHC-I variant can bind is represented by the 2D-coordinates in the epitope/paratope space, the size of the repertoire is represented by the area covered in the epitope/paratope space.

Fitness calculation is relative (to maintain a constant population size), such that the number of offspring is always equal the number of dying hosts. More details in the fitness calculation section [hosts are sorted by fitness and the top proportion of fittest hosts is resistent the bottom proportion susceptible].

##### Properties
  - Locus/Loci
    - 2 Allels per locus
  - Fitness (0 to 1)
  - Fitness increment steps -> host generation time = fitness increment step * parasite generation time (1)
    - Fitness increment value = 1/increment steps
  - Relative fitness: proportion of surviving/dying hosts each generation
    - Number of offspring -> depends on fitness calculation; if 50% of hosts die each generation, the remaining 50 % need to produce one offspring each (2 gametes per host)
  - Age
  - Mutation rate

##### Rules
  - Each Host can be infected once by one (-> or maybe multiple?) parasite each generation
    - Whether is host is resistent or susceptible is determined by the relative fitness (fittest x% of all hosts are resistent, rest is susceptible)
  - If the host is resistent to an infection, fitness is increased by the fitness increment value
  - if the host susceptible to an infection, fitness is reduced by the fitness increment value
  - If fitness is less or equal zero, the host dies and is removed from the pool of hosts
  - If fitness is greater than one:
    1. The host will produces two gametes with one allele each
    2. Determine if mutation occurs and apply it
    3. Gametes of all reproducing hosts fuse according to the reproduction regieme

#### Parasite

The parasite is a haploid organsism that reproduces clonally. The parasites haplotype (single locus/single allele) represents its peptidome as a 2D coordinate on the epitope/paratope space. Fitness, as with the host, is relative. 

##### Properties
  - Haplotype
  - Relative fitness: proportion of surviving/dying hosts each generation
    - Number of offspring -> depends on fitness calculation; if 50% of hosts die each generation, the remaining 50 need to produce on offspring each (2 gametes per host)
  - Age
  - Mutation rate

##### Rules
  - Each Parasite infects a single host each generation
  - Fitness is sorted and fittest proportion, according to the relative fitness property, survives. All others die.
  - The surviving fraction reproduces clonally, with mutation when applicable, such that the population size is restored (i.e. as many parsites reproduce as have died) 

### Infection Regime

Every host is infected by one Parasite each generation. How that parasite is selected is determined by the given infection regieme.

#### 1. Random Parasites 

Parasites are drawn from one large pool of every parasite from every species. Host-Parasite interaction is constant and only driven by parasitic diversity. 

#### 2. Fluctuating Parasites over Time

Which parasite species are present is determined by a "scheduele". Example: Generation 1-100 -> species 1, generation 101-200 -> species 2,... etc. 

#### 3. Associated Parasites

Every host is assigned one parasite species and is infected only by parasites drawn from that species. Host still reproduce according to their reproduction regieme. The associated parasite of host offspring is randomly choosen from either parent.

Represents a basic spatial association of parasites to hosts.

#### 4. Fluctuating Parasites over Space

Hosts are infected by the closest individual parasite. Parasites could move every generation in a random or non-random direction or could be redistributed completely in the given space.

#### 5. Fluctuating Parasites over Space and Time 

Combination of 2. and 4.

### Reproduction Regime




### Fitness Calculation

Either approach of Stefan 2019 (alleles as bitstrings) or approach of [Lighten et al 2017][Lighten] (2D epitope/paratope space).


## Todo 
  - Look into real data & analyze it
  - Better understanding for epitope/paratope space
  - Define all input and output parameters
    - Determine realistic range of values for the input parameters -> Lighten et al, but investigate further
  - Recreate Lighten et al / Ejsmond Model in Python
  - 



## Notes
  - Trans-species Polymorphism (TSP)
  - Implement supertypes?
  - How are the different species implemented? -> different allele frequencies? Different positions in the epitope/paratope space?
  - How many are loci co-amplified? -> if not known unable to determine correct zygosity
  - Red Queen Arms Race is not observed in real data 
    - alleles rarely disappear completly or entirely new alleles appear
    - Where do signals of positive selection come from?
      - NFDS (positive selection acts on rare alleles)
  - Completely novel parasites rarely appear -> pool of all parasites from which to draw from
    - Thought: MHC diversity is strongly driven by parasite peptidome diversity -> peptidomes of parasites is largely unique ([Özer 2021][Özer])
  - How important is recombination (with 2 or more loci)
  - Different mutation rates for host and parasite -> maybe ratio between host/parasite mutation rate important
  - Promiscuous and fastidious MHC variants ()
    - Why not evolve in the direction of most promiscuous variant? False-Positive detection of self, fastidious variants possibly advantageous for specific, nasty parasites 
    - Solution: use realistic average promiscuity
  - What real data is available?
  - Balancing selection might help introgression -> introgressed alleles are initially rare (NFDS) and probably diverged (DAA). In a population that has high polymorphism already, heterozygosity is already high and additional, introgressed alleles won't increase heterozygosity much
  - Generally: Importance of introgression?
  - Is paratope the correct name for the MHC peptide binding domain (PBD)?
  - Peptidome is mostly unique to the specific pathogen -> can the peptidome of a pathogen be represented as a single point in epitope space?
  - Is the mutation rate per organism or per allele?
  - NFDS assumes much shorter generation time/higher mutation rates for the coevolution -> generation time as parameter
  - "balancing selection very strong in MHC based on sequence patterns"
  - MHC class I -> HLA-A, HLA-B, HLA-C
  - MHC class II -> HLA-DR, HLA-DP, HLA-DQ
  - Individual MHC diversity -> Variation in allele numbers range can range from 1 to 40 (example numbers)
    - Allele sharing (-> multiple loci can carry the same allele) OR copy number variation
    - Copy number variation only in MHC, neighbouring genes don't exhibit CNV
    - Difference in copy number might be adaptive -> more pathogen diversity, higher copy number 
    - Coevolution of genome structure
    - More copies -> more "material" for recombination -> evolutionary advantage

[Lighten]:https://www.nature.com/articles/s41467-017-01183-2
[Ejsmond]:https://www.nature.com/articles/s41467-018-06821-x
[Özer]:https://academic.oup.com/mbe/advance-article/doi/10.1093/molbev/msab176/6295886?login=true