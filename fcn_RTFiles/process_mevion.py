import numpy as np
import time
from scipy.io import loadmat
import pandas as pd

def read_proton_plan(plan,structured_data):
    RTP = structured_data[plan['patient_id']][plan['study_id']][plan['modality']][plan['series_index']]['metadata']['DCM_Info']

    # Record the time
    start_time = time.time()
    
    # Determine the number of beams used
    num_beams = len(RTP.IonBeamSequence)
    M_RTP = {}
    
    # TPS system
    RayStationPlan = 1
    
    for beam in range(num_beams):
        # Skip the setup beam
        if RTP.IonBeamSequence._list[beam].TreatmentDeliveryType == 'SETUP':
            continue
        # Indicate what beam it is
        Beam_ID = RTP.IonBeamSequence._list[beam].BeamNumber
        
        # Indicate the control points in the plan
        num_ctrlPts = RTP.IonBeamSequence._list[beam].NumberOfControlPoints
        
        AACdx = []; AAC1g = []; AAC1f = []; AAC1e = []; AAC1d = []; AAC1c = []; AAC1b = []; AAC1a = []; AAC2g = [];
        AAC2f = []; AAC2e = []; AAC2d = []; AAC2c = []; AAC2b = []; AAC2a = []

        # Determine for each control point if it is spot/mlc/aperture shape and loop over eahc layer
        # Jump two steps, as these two belong to the same control point (e.g. begin/end)
        for ctrlPt in range(0, num_ctrlPts, 2):
            # Get the range shifter settings per control point
            RSSeq = RTP.IonBeamSequence._list[beam].IonControlPointSequence._list[ctrlPt].RangeShifterSettingsSequence._list[0].RangeShifterSetting
            
            if RSSeq[-3:].casefold() == 'MLC':
                # then it is an Aria plan
                RayStationPlan = 0
                leafPositions = RTP.IonBeamSequence._list[beam].IonControlPointSequence._list[ctrlPt].ScanSpotPositionMap
                # Assign coordinates for every leaf from position map
                Cdx=leafPositions[7]
                C1a=leafPositions[16]
                C1b=leafPositions[18]
                C1c=leafPositions[20]
                C1d=leafPositions[22]
                C1e=leafPositions[24]
                C1f=leafPositions[26]
                C1g=leafPositions[28]
                C2a=leafPositions[2]
                C2b=leafPositions[4]
                C2c=leafPositions[6]
                C2d=leafPositions[8]
                C2e=leafPositions[10]
                C2f=leafPositions[12]
                C2g=leafPositions[14]
                
            # Find if it is a 'SPOT'
            if (len(RSSeq) > 18) and (RSSeq[-4:].casefold() != 'SPOT'):
                continue
           
            # Retrieve the coordinates of the radiation beam spots
            spot_positions = RTP.IonBeamSequence._list[beam].IonControlPointSequence._list[ctrlPt].ScanSpotPositionMap
            # Divide in x and y coordinate 
            spot_positions = np.array(spot_positions)
            # uneven numbers are x_spot
            x = spot_positions[1::2]
            # even numbers are y_spot
            y = spot_positions[::2]
            
            # Initiate all variables
            if 'x_spot' not in locals():
                idx = 0;
                x_spot = np.zeros(len(x))
                y_spot = np.zeros(len(y))
                # The dose per spot
                pulse_charge = np.zeros(len(y))
                
            else:
                idx = len(x_spot)
                x_spot = np.concatenate((x_spot, np.zeros(len(x))))
                y_spot = np.concatenate((y_spot, np.zeros(len(y))))
                # The dose per spot
                pulse_charge = np.concatenate((pulse_charge, np.zeros(len(y))))
            # Save all the x-spots and y-spots
            x_spot[idx:idx+len(x)] = x
            y_spot[idx:idx+len(y)] = y
            # The dose per spot
            pulse_charge[idx:idx+len(y)] = RTP.IonBeamSequence._list[beam].IonControlPointSequence._list[ctrlPt].ScanSpotMetersetWeights
            
            # Get the plate sequence (plates)
            # Get the snoutdistance (snoutdist)
            # Get the gantry angle (gantry_ang)
            # Get the couch angle (couch_ang)
            energy = RSSeq
            energy = energy[0:18]
            
            if idx == 0:
                plates = np.zeros((len(x), len(energy)))
                snoutdist = np.zeros(len(x))
                gantry_ang = np.zeros(len(x))
                couch_ang = np.zeros(len(x))
                transx = np.zeros(len(x))
                transy = np.zeros(len(x))
                transz = np.zeros(len(x))
                
            else:
                plates = np.concatenate((plates, np.zeros((len(x), len(energy)))))
                snoutdist = np.concatenate((snoutdist, np.zeros(len(x))))
                gantry_ang = np.concatenate((gantry_ang, np.zeros(len(x))))
                couch_ang = np.concatenate((couch_ang, np.zeros(len(x))))
                transx = np.concatenate((transx, np.zeros(len(x))))
                transy = np.concatenate((transy, np.zeros(len(x))))
                transz = np.concatenate((transz, np.zeros(len(x))))
                
            for j in range(len(energy)):
                plates[idx:idx+len(x), j] = float(energy[j])
            
            # Get the snout distance
            snoutdist[idx:idx+len(x)] = RTP.IonBeamSequence._list[beam].IonControlPointSequence._list[0].SnoutPosition
            # Get the gantry angle
            gantry_ang[idx:idx+len(x)] = RTP.IonBeamSequence._list[beam].IonControlPointSequence._list[0].GantryAngle
            # Get the snout distance
            couch_ang[idx:idx+len(x)] = RTP.IonBeamSequence._list[beam].IonControlPointSequence._list[0].PatientSupportAngle
            # add motion
            off = 0
            transx[idx:idx+len(x)] = off
            transy[idx:idx+len(x)] = off
            transz[idx:idx+len(x)] = off
            
            # Get the MLC positions
            if 'Cdx' in locals():
                value = np.full(Cdx, len(x)); AACdx.append(value)
                value = np.full(C1g, len(x)); AAC1g.append(value)
                value = np.full(C1f, len(x)); AAC1f.append(value)
                value = np.full(C1e, len(x)); AAC1e.append(value)
                value = np.full(C1d, len(x)); AAC1d.append(value)
                value = np.full(C1c, len(x)); AAC1c.append(value)
                value = np.full(C1b, len(x)); AAC1b.append(value)
                value = np.full(C1a, len(x)); AAC1a.append(value)
                value = np.full(C2g, len(x)); AAC2g.append(value)
                value = np.full(C2f, len(x)); AAC2f.append(value)
                value = np.full(C2e, len(x)); AAC2e.append(value)
                value = np.full(C2d, len(x)); AAC2d.append(value)
                value = np.full(C2c, len(x)); AAC2c.append(value)
                value = np.full(C2b, len(x)); AAC2b.append(value)
                value = np.full(C2a, len(x)); AAC2a.append(value)

            else:
                zeros = np.zeros((len(x)))
                AACdx.append(zeros); AAC1g.append(zeros); AAC1f.append(zeros); AAC1e.append(zeros); 
                AAC1d.append(zeros); AAC1c.append(zeros); AAC1b.append(zeros); AAC1a.append(zeros); 
                AAC2g.append(zeros); AAC2f.append(zeros); AAC2e.append(zeros); AAC2d.append(zeros); 
                AAC2c.append(zeros); AAC2b.append(zeros); AAC2a.append(zeros) 
        
        AACdx = concat_float64(AACdx); AAC1g = concat_float64(AAC1g); AAC1f = concat_float64(AAC1f)
        AAC1e = concat_float64(AAC1e); AAC1d = concat_float64(AAC1d); AAC1c = concat_float64(AAC1c)
        AAC1b = concat_float64(AAC1b); AAC1a = concat_float64(AAC1a); AAC2g = concat_float64(AAC2g)
        AAC2f = concat_float64(AAC2f); AAC2e = concat_float64(AAC2e); AAC2d = concat_float64(AAC2d)
        AAC2c = concat_float64(AAC2c); AAC2b = concat_float64(AAC2b); AAC2a = concat_float64(AAC2a)
        
        # Loading the energies with some predefined
        try:        
            data = loadmat('energiesMevion.mat')
        except: 
            print("missing energiesMevion.mat file")
            return
        energiesMevion = data['energiesMevion']
        
        # Use the predefined values. Now look into the plate configuration and decide what energy belongs to that config.
        Energy = np.zeros((plates.shape[0]))
        for p in range(plates.shape[0]):
            w = energiesMevion[:, 1:19] - np.fliplr(plates[p, :][None, :])
            w = np.sum(np.abs(w), axis=1)
            Energy[p] = energiesMevion[w==0,0][0]
        
        # Present everything in a dataframe
        result = {
            'x_spot': x_spot,
            'y_spot': y_spot,
            'pulse_charge': pulse_charge,
            'snoutdist': snoutdist,
        }
        
        # Add plates 1–18
        for i in range(18):
            result[f'Plate_{i+1}'] = plates[:, i]
        
        # Add the rest
        result.update({
            'transx': transx,
            'transy': transy,
            'transz': transz,
            'gantry_ang': gantry_ang,
            'couch_ang': couch_ang,
            'AACdx': AACdx,
            'AAC1a': AAC1a,
            'AAC1b': AAC1b,
            'AAC1c': AAC1c,
            'AAC1d': AAC1d,
            'AAC1e': AAC1e,
            'AAC1f': AAC1f,
            'AAC1g': AAC1g,
            'AAC2a': AAC2a,
            'AAC2b': AAC2b,
            'AAC2c': AAC2c,
            'AAC2d': AAC2d,
            'AAC2e': AAC2e,
            'AAC2f': AAC2f,
            'AAC2g': AAC2g,
            'Energy': Energy,
        })
        
        # Make the DataFrame
        df = pd.DataFrame(result)
        
        # Store it in a dictionary with dynamic key
        M_RTP[f'Beam_{Beam_ID}'] = {'Info': df}
        #M_RTP[f'Beam_{Beam_ID}'] = {'FileModDate': RTP.FileModDate}
        M_RTP[f'Beam_{Beam_ID}']['RTPlanDate'] =  RTP.RTPlanDate
        M_RTP[f'Beam_{Beam_ID}']['MU_plan'] = RTP.IonBeamSequence._list[beam].FinalCumulativeMetersetWeight
        M_RTP[f'Beam_{Beam_ID}']['Isocenter'] = RTP.IonBeamSequence._list[beam].IonControlPointSequence._list[0].IsocenterPosition._list
        M_RTP[f'Beam_{Beam_ID}']['fractions'] = RTP.FractionGroupSequence._list[0].NumberOfFractionsPlanned
        M_RTP[f'Beam_{Beam_ID}']['BeamName'] = RTP.IonBeamSequence._list[beam].BeamName
        
        if RayStationPlan == 1:
            M_RTP[f'Beam_{Beam_ID}']['Info'].iloc[:,27:35] = 100
            M_RTP[f'Beam_{Beam_ID}']['Info'].iloc[:,35:42] = -100
        
        # Clear the variable from the last loop
        del couch_ang, gantry_ang, snoutdist, transx, transy, transz, pulse_charge, x_spot, y_spot, plates
        del AAC1a, AAC1b, AAC1c, AAC1d, AAC1e, AAC1f, AAC1g
        del AAC2a, AAC2b, AAC2c, AAC2d, AAC2e, AAC2f, AAC2g, AACdx

        structured_data[plan['patient_id']][plan['study_id']][plan['modality']][plan['series_index']]['metadata']['Plan_Protons_Beams'] = M_RTP
    # elapsed_time = time.time() - start_time
    # print(f"Elapsed time: {elapsed_time:.2f} seconds")



def concat_float64(arr_list):
    return np.concatenate([arr.ravel() for arr in arr_list]).astype(np.float64)