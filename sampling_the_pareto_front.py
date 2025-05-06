import numpy as np
import os
import subprocess as sp
from tqdm import tqdm
from collections import deque

script_execution_folder = "/dls/physics/exr35747/my_own_elegant/TL/"
submission_script_filename = "sub_script_calcs.sh"

max_current = 370 #mA
min_current = 10 #mA
current_sampling_points = 170

print(f"For current range [150,800]mA, this corresponds to a current step size of {(max_current-min_current)/current_sampling_points}")


vertical_emittance_start_value = 1 # pm rad
vertical_emittance_end_value = 8*25 # 8pm rad is the nominal, so this is a 25x increase in emittance, or 5x increase in vertical beam size

### Now the goal is to efficiently sample the vertical emittance values to be able to construct the Pareto front. 
### This was done by wanting to ensure that the hypotenuse distance between points sampled remained roughly invariant

nominal_step_size = 1 
estimated_emittance_function = lambda x: 89.19*x**(1/4) # number calculated from inverting radiation limit to find emittance value
d_emit = lambda x: nominal_step_size / np.sqrt(1+(0.25*(estimated_emittance_function(x)/x))**(2))
data_deque = deque([vertical_emittance_start_value])

while data_deque[-1] < vertical_emittance_end_value:
    data_deque.append(data_deque[-1] + d_emit(data_deque[-1]))

vertical_emittances = np.array(data_deque)
print("Number of emittance points: ", len(vertical_emittances))
number_of_emittance_points = len(vertical_emittances) 
print(f"Total number of operations is {current_sampling_points*number_of_emittance_points}")

os.chdir(script_execution_folder)

for i in tqdm(range(number_of_emittance_points), desc="Jobs submitted"):
    run_command = f"qsub -N TL_{i} ./{submission_script_filename} {vertical_emittances[i]} {i} {current_sampling_points}"  
    sp.run(run_command.split(" "), stdout=sp.DEVNULL) # execute command