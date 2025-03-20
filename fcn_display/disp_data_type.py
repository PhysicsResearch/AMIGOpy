import numpy as np

def adjust_data_type_input(self,idx):
    data_type = self.display_data[idx].dtype
    #
    if data_type == np.int16:
        self.dataImporterAxial[idx].SetDataScalarTypeToShort()
        self.dataImporterSagittal[idx].SetDataScalarTypeToShort()
        self.dataImporterCoronal[idx].SetDataScalarTypeToShort()
    elif data_type == np.uint16:
        self.dataImporterAxial[idx].SetDataScalarTypeToUnsignedShort()
        self.dataImporterSagittal[idx].SetDataScalarTypeToUnsignedShort()
        self.dataImporterCoronal[idx].SetDataScalarTypeToUnsignedShort()
    elif data_type == np.float32:
        self.dataImporterAxial[idx].SetDataScalarTypeToFloat()
        self.dataImporterSagittal[idx].SetDataScalarTypeToFloat()
        self.dataImporterCoronal[idx].SetDataScalarTypeToFloat()
    elif data_type == np.int8:
        self.dataImporterAxial[idx].SetDataScalarTypeToChar()
        self.dataImporterSagittal[idx].SetDataScalarTypeToChar()
        self.dataImporterCoronal[idx].SetDataScalarTypeToChar()
    elif data_type == np.uint8:  # This would typically represent binary data
        self.dataImporterAxial[idx].SetDataScalarTypeToUnsignedChar()
        self.dataImporterSagittal[idx].SetDataScalarTypeToUnsignedChar()
        self.dataImporterCoronal[idx].SetDataScalarTypeToUnsignedChar()
    elif data_type == np.float64:
        self.dataImporterAxial[idx].SetDataScalarTypeToDouble()
        self.dataImporterSagittal[idx].SetDataScalarTypeToDouble()
        self.dataImporterCoronal[idx].SetDataScalarTypeToDouble()
    elif data_type == np.bool_:
        # bool will be treated as unsigned char (0/1)
        scalar_type_method = "SetDataScalarTypeToUnsignedChar"
    else:
        raise ValueError(f"Unsupported data type: {data_type}")
    # #     
    
def adjust_data_type_comp_input(self,axes,layer):
    data_type =self.display_comp_data[axes,layer].dtype
    #
    if data_type == np.int16:
        self.dataImporterAxComp[axes,layer].SetDataScalarTypeToShort()
    elif data_type == np.uint16:
        self.dataImporterAxComp[axes,layer].SetDataScalarTypeToUnsignedShort()
    elif data_type == np.float32:
        self.dataImporterAxComp[axes,layer].SetDataScalarTypeToFloat()
    elif data_type == np.int8:
        self.dataImporterAxComp[axes,layer].SetDataScalarTypeToChar()
    elif data_type == np.uint8:  # This would typically represent binary data
        self.dataImporterAxComp[axes,layer].SetDataScalarTypeToUnsignedChar()
    elif data_type == np.float64:
        self.dataImporterAxComp[axes,layer].SetDataScalarTypeToDouble()
    # Add more conditions for other data types if needed
    else:
        raise ValueError(f"Unsupported data type: {data_type}")
    # #    

def adjust_data_type_input_IrIS_eval(self,idx):
    data_type = self.display_data_IrIS_eval[idx].dtype
    #
    if data_type == np.int16:
        self.dataImporterIrEval[idx].SetDataScalarTypeToShort()
    elif data_type == np.uint16:
        self.dataImporterIrEval[idx].SetDataScalarTypeToUnsignedShort()
    elif data_type == np.float32:
        self.dataImporterIrEval[idx].SetDataScalarTypeToFloat()
    elif data_type == np.int8:
        self.dataImporterIrEval[idx].SetDataScalarTypeToChar()
    elif data_type == np.uint8:  # This would typically represent binary data
        self.dataImporterIrEval[idx].SetDataScalarTypeToUnsignedChar()
    elif data_type == np.float64:
        self.dataImporterIrEval[idx].SetDataScalarTypeToDouble()
    # Add more conditions for other data types if needed
    else:
        raise ValueError(f"Unsupported data type: {data_type}")
    # #    