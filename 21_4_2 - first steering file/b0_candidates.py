import sys
import basf2 as b2
# Convenience modules
import modularAnalysis as ma
# Convenience functions to filter standard particles
import stdV0s
# To print statistics
from basf2 import statistics


# get input file number from the command line
filenumber = 1

# Create path.
# This will be define the container of the series of steps
# we are going to perform to do our analysis. All steps will be added
# as "modules" to this path
main = b2.Path()

# Load input data from mdst/udst file
# We are going to add a module to the "main" path to indicate the input
# file containing all the events
ma.inputMdstList(
    environmentType="default",
    filelist=[b2.find_file(f"starterkit/2021/1111540100_eph3_BGx0_"
              f"{filenumber}.root", "examples")],
    path=main,
)

"""
Now, we are going to add the steps that actually filter the data. Each filter
is looking for a specific particle and each candidate (i.e. the result of every
filter) is going to be stored in the ParticleList.
The goal is to create filters and recontruct everything we need so, in the end,
we can find B0 candidates.
"""

# Load electrons, positrons.
# First, we are going to look for electrons and positrons. That is, we are
# going "fill the particle list" with electron/positron candidates based on
# our filtering criteria (i.e. based on "cuts")
ma.fillParticleList(
    decayString="e+",
    cut="electronID>0.1 and dr<0.5 and abs(dz)<2 and thetaInECLAcceptance",
    path=main
)

# Load k_shorts
# Then, we going to look for K_short candidates. The appropiate cuts and
# filters are already programmed and store in a convenience function called
# "stdKshorts" (which is in the module of convenience filters for Standard
# Particles: stdV0s).
# In its inner workings, this function applies the recommended cuts (it looks
# for the K_S0 by looking for its product decays: K_S0 -> pi+ pi-. It looks
# for them using two different methods [V0 and ParticleCombiner] and then
# merges the results).
# K_S0 candidates in a variable called K_S0:merged in the ParticleList
stdV0s.stdKshorts(path=main)

# Reconstruct J/psi
# Now, we are looking for J/psi candidates. There is no convenience function,
# but it is fairly easy to look for the J/psi by its products e+ e-. The syntax
# for the decayString is:
#   parent:label -> children
# where "label" is an optional label to add to the variable in the ParticleList
# If no label is provided, then the variable is just called "parent".
# The cut we are using is setting a mass minus nominal mass lower than 0.11
ma.reconstructDecay(
    decayString="J/psi -> e+ e-",
    cut="dM < 0.11",
    path=main
)

# Reconstruct B0
# Up to this point, we have candidates for the J/psi and the K_S0 (stored in
# the variable K_S0:merged), we can use those them to create a new
# candidate for the B0 particle.
ma.reconstructDecay(
    "B0 -> J/psi K_S0:merged",
    cut="",
    path=main,
)

# Store our results to perform offline analysis.
# A good variable to start with is the beam-constrained mass Mbc, which will be
# stored in a tuple. This variable:
# 1. is only of interest for B0 candidates, so it will be one entry per
#    candidate which is defined by the decayString
# 2. has to peak at the mass of the B0 (which will mean filters are indeed
#    working and we have good candidates)
# 3. will be stored in a file called "Bd2JpsiKS.root" in a tree called "tree"
ma.variablesToNtuple(
    decayString="B0", variables=["Mbc"],
    filename="Bd2JpsiKS.root",
    treename="tree",
    path=main
)

# Start the event loop (actually start processing things)
b2.process(main)

# print results stored in global statistics
print(statistics)
