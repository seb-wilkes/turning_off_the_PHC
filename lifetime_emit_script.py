#%%
import numpy as np
from eleganttools import SDDS
import subprocess as sp
from tqdm.contrib import tenumerate as tqdm
import sys
from scipy.interpolate import interp1d
import csv
# definitions below

print(f"Calculations commencing for Vertical Emittance = {sys.argv[1]} pm\t[Run {sys.argv[2]}]")

max_current = 370 #mA
min_current = 10 #mA

dir = "/dls/physics/exr35747/simulation_output/"
ibs_emit_tool = "/dls/physics/exr35747/my_own_elegant/faster_elegant/ibsEmittance"
twiss_parameters_file = "/dls/physics/exr35747/my_own_elegant/TL/run.twi"
dynamic_aperture_file = "/dls/physics/exr35747/my_own_elegant/TL/DTBA.mmap"
output_dir = "/dls/physics/exr35747/my_own_elegant/TL/calc_output/"
run_number = int(sys.argv[2])

sample_points = int(sys.argv[3])
current = np.linspace(min_current, max_current, sample_points, endpoint=True) # mAmps
Q_bunch = current * 1e-3* 1.87e-6 / 899 # Coulombs
Q_bunch *= 1e9 # in units of nC
tl_data = np.copy(current) * 0
emittance_data = np.copy(current)*0
energy_spread_data = np.copy(current)*0
ey = float(sys.argv[1]) * 1e-12 # should be specified in picometres


#%%
for i,q in tqdm(Q_bunch):
    run_command_ibs = f"{ibs_emit_tool} {twiss_parameters_file} {output_dir}run{run_number*sample_points + i[0]}.ibs -charge={q} -emityInput={ey} -fixEmity=1 -RF=Voltage=1.420,harmonic=934"    
    sp.run(run_command_ibs.split(" "), stdout=sp.DEVNULL) # execute command
    ibs_vals = SDDS(f"{output_dir}run{run_number*sample_points + i[0]}.ibs").as_dict()
    ex, sdelta, sz = ibs_vals["emitx"], ibs_vals["sigmaDelta"], ibs_vals["sigmaz"]*1e3
    # print(ex, sdelta, sz)
    emittance_data[i] = ex
    energy_spread_data[i] = sdelta
    run_command_tl = f"touschekLifetime {output_dir}run{run_number*sample_points + i[0]}.tl -twiss={twiss_parameters_file} -aperture={dynamic_aperture_file} -charge={q} -length={sz} -emitInput={ex} -emityInput={ey} -deltaInput={sdelta}"    
    sp.run(run_command_tl.split(" "), stdout=sp.DEVNULL) # execute command
    tl_output = SDDS(f"{output_dir}run{run_number*sample_points + i[0]}.tl").as_dict()
    tl_data[i] = tl_output["tLifetime"]


mu_rad = 300/4 # maximum radiation limit

intercept = current/tl_data - mu_rad

tl_model = interp1d(current, intercept, kind='quadratic') # interpolation type
emit_model = interp1d(current, emittance_data, kind='quadratic')
e_spread_model = interp1d(current, energy_spread_data, kind='quadratic') 

fine_current = np.linspace(np.min(current), np.max(current), 1000, endpoint=True)
fine_emit_x = emit_model(fine_current)
fine_e_spread = e_spread_model(fine_current)

intercept_arg = np.argmin(np.abs(tl_model(fine_current)))

max_current, ex_opt, e_spread_at_max = fine_current[intercept_arg],\
                                        fine_emit_x[intercept_arg],\
                                        fine_e_spread[intercept_arg]

with open(f"{output_dir}new_opt{run_number}.csv", "w") as output_file:
    csv_writer = csv.writer(output_file)
    csv_writer.writerow([ey, max_current, ex_opt, e_spread_at_max])
    
