from types import SimpleNamespace
import numpy as np
# relevant variables
#

def initialize_software_variables(self):
    #
    self.rulers   = [] 
    self.circle   = [] 
    self.ellipses = []
    self.squares  = []
    self.points   = []
    #
    self.patientID         = None
    self.studyID           = None
    self.modality_metadata = None
    self.series_index      = None
    self._text_dragging    = False
    #
    self.CmapIDX     = np.zeros(4)
    self.LayerAlpha  = np.zeros(4)
    #
    self.LayerAlpha[0]  = 1
    #
    # 
    self._opacities = np.ones(4)
    
    #
    self.current_axial_slice_index    = [-1,-1,-1,-1]
    self.current_sagittal_slice_index = [-1,-1,-1,-1]
    self.current_coronal_slice_index  = [-1,-1,-1,-1]
    self.current_seg_slice_index = -1
    # comparison axes 12 
    self.current_AxComp_slice_index    = np.zeros((12,4))-1
    
    self.slice_thick      = np.zeros(4)
    self.pixel_spac       = np.zeros((4,2))
    self.Im_PatPosition   = np.zeros((4, 3))
    self.Im_Offset        = np.zeros((4, 3))
    self.display_data           = {}
    self.display_data_undo      = {}
    self.display_data_IrIS_eval = {}
    self.display_time_IrIS_eval = {}
    self.current_IrIS_eval_slice_index = np.zeros(4)
    
    self.im_ori_comp         = np.zeros(12)        
    self.slice_thick_comp    = np.zeros((12,4))
    self.pixel_spac_comp     = np.zeros((12,4,2))
    self.Im_PatPosition_comp = np.zeros((12,4, 3))
    self.Im_Offset_comp      = np.zeros((12,4, 3))
    self.display_comp_data   = {}
    self.left_but_pressed    = np.zeros(2)  

    # TG43 - Brachy
    # ——— TG43 storage structure ———
    # create a simple container for TG43
    self.TG43 = SimpleNamespace()
    # within it, add an activesource container
    self.TG43.activesource = SimpleNamespace(
        airkerma_strength=None,
        source_model=None, 
        source_diameter=None,
        source_length_mm=None,
        dose_rate_constant=None,
        radial=None,
        radial_fit=None,
        anisotropy=None,
        along_away_reference=None,
        along_away_reference_calc=None,
        DoseMatrix=None,
        DoseMatrix_res_mm=None,
        DoseMatrix_size=None
    )
    # —————————————————————————— 

    
    self.slice_thick_seg      = np.zeros(4)
    self.pixel_spac_seg       = np.zeros((4,2))
    self.Im_PatPosition_seg   = np.zeros((4, 3))
    self.Im_Offset_seg        = np.zeros((4, 3))
    # ----------------------------------------------
    self.pixel_spacing3Dview    = np.zeros((4,2))
    self.slice_thickness3Dview  = np.zeros(4)
    #
    self.Im_PatPosition3Dview   = np.zeros((4,3))
    self.display_3D_data        = {} 
    self.Im_Offset3Dview        = np.zeros((4, 3))

    #
    self.display_seg_data       = {}
    self.seg_brush = 0
    self.seg_erase = 0
    self.seg_brush_coords = None
    self.seg_init_all_series = True
    self.seg_win_lev = [None, None]
    self.seg_curr_extent = [[None, None], [None, None]]
    self.zoom_scale = None
    self.zoom_center = (None, None, None)
    self.camera_pos = (None, None, None)
    self.seg_init_view = True
    self.seg_prev_data = {"Orientation": None, "Dimensions": (None, None, None),
                          "SliceThickness": None, "PixelSpacing": (None, None)}
    self.struct_colors = {}
    # IrIS ################################################################
    # this varibale will be resized depeding on the number of dwell positions
    # the number of colluns should remaing the same and was included here for documentation purposes.
    # [:,0]  - Idx of the 1st peak (initial positions)
    # [:,1]  - Idx of the 2nd peak (last positions)
    # [:,2]  - Idx of the 1st peak (without transit)
    # [:,3]  - Idx of the 2nd peak (without transit)
    # [:,4]  - time (s) 1st peak 
    # [:,5]  - time (s) 2nd peak
    # [:,6]  - time (s) 1st peak (without transit)
    # [:,7]  - time (s) 2nd peak (without transit)
    # [:,8]  - Dwell   time (s)  (without transit)
    # [:,9]  - Transit time (s)  
    # [:,10] - Total   time (s) 
    # [:,11] - Total   time 10 Ci (s) 
    # [:,12] - Position (X)
    # [:,13] - Position (Y)
    # [:,14] - Position (Z)
    # [:,15] - Channel (Z)
    # [:,16] - Ac (Z)
    self.Dw_pos_info   = np.zeros((1,17))
    
    # Dw pos brachy plans 
    self.dwell_actors_ax = []     # Initialize an empty list to store dwell actors
    self.dwell_actors_co = []
    self.dwell_actors_sa = []
    # Ch pos brachy plans 
    self.channel_actors_ax = []   # Initialize an empty list to store dwell actors
    self.channel_actors_co = []
    self.channel_actors_sa = []

    # Display struct contoru
    self.structure_actors_ax = [] # Initialize an empty list

    # Circle ROI -----------------------------------------------------------------------------------
    # Initialize a list to store circle actors if it doesn't exist
    self.circle_actors_ax = []
    self.circle_actors_co = []
    self.circle_actors_sa = []
   
        
