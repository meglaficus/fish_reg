import SimpleITK as sitk
import numpy as np
from tqdm import tqdm
import copy


def main(video_path, start_frame = None, end_frame = None, sampling_rate = 3, smoothing_width = 5):

    # Read video and decide on reference slice
    video = sitk.ReadImage(video_path)

    video_array = sitk.GetArrayFromImage(video)
    number_of_slices = video_array.shape[0]

    middle_slice = video_array[number_of_slices // 2]
    middle_img = sitk.GetImageFromArray(middle_slice)
    
    
    # Construct the elastix imag filter
    elastixImageFilter = sitk.ElastixImageFilter()
    elastixImageFilter.SetParameterMap(sitk.GetDefaultParameterMap("rigid"))
    elastixImageFilter.SetFixedImage(middle_img)
    elastixImageFilter.SetLogToConsole(False)

    # Do registration for every third slice and save only the transformation parameters
    transform_params = np.zeros((number_of_slices, 3))

    for i in tqdm(range(0, len(video_array), 3), desc='Registering'):
        elastixImageFilter.SetMovingImage(sitk.GetImageFromArray(video_array[i]))
        elastixImageFilter.Execute()

        param_map = elastixImageFilter.GetTransformParameterMap()[0]
        transform_params[i] = ([float(i) for i in param_map['TransformParameters']])

    center_of_rotation = np.array([float(i) for i in param_map['CenterOfRotationPoint']])
        
    # Extract two arrays of parameters, each with every sixth image filled and a faze shift of 3 images
    first_transform_array = np.empty(transform_params.shape)
    second_transform_array = np.empty(transform_params.shape)

    first_transform_array[:] = np.nan
    second_transform_array[:] = np.nan


    for i in range(0, len(transform_params), 3):
        if i % 6 == 0:
            first_transform_array[i] = transform_params[i]
        else:
            second_transform_array[i] = transform_params[i]
            


    # Interpolate in between the set parameters
    def fill_out_array(array0, start, period):
        
        array = copy.deepcopy(array0)
        
        if start != 0:
            inter_array = np.zeros((start, 3))
            first = array[start]
            second = array[start + period]
            
            for j in range(start):
                inter_array[start - j - 1] = first - (second - first) * ((j+1) / period)
                    
            array[:start] = inter_array
        
        for i in range(start, len(array0), period):
        
                
            first = array[i]
            second = array[i+period]
            inter_array = np.zeros((period - 1, 3))
            
            for j in range(period-1):
                inter_array[j] = first + (second - first) * ((j + 1) / period)
            
            array[i+1:i+period] = inter_array
            
            # To handle the end of the array
            if len(array0) - i == period + 1:
                break
            
            if len(array0) - i <= 2 * period:
                
                remainder = len(array0) - i - period - 1
                inter_array = np.zeros((remainder, 3))
                
                for j in range(remainder):
                    inter_array[j] = second + (second - first) * ((j+1) / period)
                    
                array[i+period + 1:] = inter_array
                
                break
            
        return array

    # Execute interpolation and combine by taking the mean
    first_transform_array = fill_out_array(first_transform_array, 0, 6)
    second_transform_array = fill_out_array(second_transform_array, 3, 6)

    total_transform_array = (first_transform_array + second_transform_array) / 2

    # Now perform median-smoothing
    smooth_transform_array = copy.deepcopy(total_transform_array)

    for i in range(5, len(total_transform_array) - 5):
        smooth_transform_array[i] = np.median(total_transform_array[i-5:i+6], axis=0)
        
    # Construct transform and resampler, then apply to video
    out_array = np.zeros(video_array.shape)

    transform = sitk.Euler2DTransform()
    transform.SetCenter(center_of_rotation)

    for i in range(len(video_array)):
        transform.SetTranslation(smooth_transform_array[i][1:3])
        transform.SetAngle(smooth_transform_array[i][0])
        
        img = sitk.Resample(sitk.GetImageFromArray(video_array[i]),
                    middle_img, 
                    transform,
                    sitk.sitkLinear, 
                    0.0)
        
        out_array[i] = sitk.GetArrayFromImage(img)
        
    out_image = sitk.GetImageFromArray(out_array)
    out_image.CopyInformation(video)

    print('Saving...')
    out_image = sitk.Cast(out_image, video.GetPixelID())
    sitk.WriteImage(out_image, f'{video_path[:-4]}_fixed.tif')

if __name__ == '__main__':
    video_path = '2022_08_25_ 000001_AFW.tif'
    main(video_path)