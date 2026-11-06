"""
A CT series as the data tree's DICOM loader (fcn_load.sort_dcm + load_dcm) reads it, with the tags a
small-animal CBCT export (Xstrahl SARRP) leaves empty or repeats: every slice InstanceNumber 1, no Series
or Acquisition Number, empty PatientID / StudyID, coronal slices, unsigned 16-bit values above 32767.
The slices are placed by their ImagePositionPatient along the slice normal, not by InstanceNumber.
"""
import random

import numpy as np
import pydicom
import pytest
from pydicom.dataset import Dataset, FileMetaDataset
from pydicom.uid import CTImageStorage, ExplicitVRLittleEndian, generate_uid

from fcn_load.load_dcm import image_int_type, load_images
from fcn_load.sort_dcm import get_data_description

NR, NC, NS = 3, 5, 4                    # file rows (along +z), columns (along +x), files (along -y)
X0, Y0, Z0, STEP = -49.4, 21.44915, -49.4, 0.1


def _write_coronal_series(folder, values):
    """File f holds values[f] (NR x NC, uint16); its IPP is f steps along -y from the first."""
    series, study, frame = generate_uid(), generate_uid(), generate_uid()
    order = list(range(NS))
    random.Random(1).shuffle(order)     # file names out of position order
    for name, f in enumerate(order):
        ds = Dataset()
        ds.file_meta = FileMetaDataset()
        ds.file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
        ds.file_meta.MediaStorageSOPClassUID = ds.SOPClassUID = CTImageStorage
        ds.file_meta.MediaStorageSOPInstanceUID = ds.SOPInstanceUID = generate_uid()
        ds.Modality = 'CT'
        ds.PatientID = ds.StudyID = ''
        ds.SeriesNumber = ds.AcquisitionNumber = None
        ds.InstanceNumber = 1
        ds.SeriesInstanceUID, ds.StudyInstanceUID, ds.FrameOfReferenceUID = series, study, frame
        ds.ImageOrientationPatient = [1, 0, 0, 0, 0, 1]
        ds.ImagePositionPatient = [X0, round(Y0 - f * STEP, 5), Z0]
        ds.PixelSpacing = [STEP, STEP]
        ds.SliceThickness = STEP
        ds.RescaleSlope, ds.RescaleIntercept = 1, 0
        ds.Rows, ds.Columns = NR, NC
        ds.SamplesPerPixel, ds.PhotometricInterpretation = 1, 'MONOCHROME2'
        ds.BitsAllocated = ds.BitsStored = 16
        ds.HighBit, ds.PixelRepresentation = 15, 0
        ds.PixelData = values[f].astype(np.uint16).tobytes()
        pydicom.dcmwrite(folder / f"volume{name:04d}.dcm", ds, enforce_file_format=True)


@pytest.mark.parametrize("peak, dtype", [(36261, np.int32), (12000, np.int16)])
def test_series_with_one_instance_number_is_placed_by_image_position(tmp_path, peak, dtype):
    values = np.random.default_rng(0).integers(6000, 12000, size=(NS, NR, NC))
    values[2, 1, 3] = peak
    _write_coronal_series(tmp_path, values)
    info, _, _ = get_data_description(str(tmp_path))
    (ct,) = load_images(None, info)[0]['']['']['CT']        # one series, of all the files
    vol, meta = ct['3DMatrix'], ct['metadata']
    assert vol.shape == (NR, NS, NC) and meta['AcquisitionPlane'] == 'CORONAL'
    ipp = np.array(meta['ImagePositionPatient'])
    assert np.allclose(ipp, (X0, Y0 - (NS - 1) * STEP, Z0), atol=1e-6)    # the voxel with the lowest x, y, z
    assert np.allclose(meta['PixelSpacing'], (STEP, STEP)) and meta['SliceThickness'] == pytest.approx(STEP)
    assert vol.dtype == dtype and vol.max() == peak         # not wrapped to a negative value
    for f in range(NS):
        r = round(NS - 1 - (Y0 - f * STEP - ipp[1]) / STEP)  # rows stored flipped: y = IPP_y + (n - 1 - r) * step
        assert np.array_equal(vol[:, r, :], values[f])       # the file: its rows along +z, its columns along +x


def test_image_int_type_is_int16_unless_the_values_do_not_fit():
    assert image_int_type(np.array([-1024.0, 3071.0])) == np.int16
    assert image_int_type(np.array([-32768.0, 32767.0])) == np.int16
    assert image_int_type(np.array([0.0, 32768.0])) == np.int32
    assert image_int_type(np.array([-32769.0, 0.0])) == np.int32
    assert image_int_type(np.zeros(0)) == np.int16
