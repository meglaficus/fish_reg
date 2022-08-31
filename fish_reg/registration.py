import SimpleITK as sitk
import numpy as np
from tqdm import tqdm
import copy


def interpolate_array(array0, start, period):

    array = copy.deepcopy(array0)

    if start != 0:
        inter_array = np.zeros((start, 3))
        first = array[start]
        second = array[start + period]

        for j in range(start):
            inter_array[start - j - 1] = first - \
                (second - first) * ((j+1) / period)

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
                inter_array[j] = second + \
                    (second - first) * ((j+1) / period)

            array[i+period + 1:] = inter_array
            break

    return array


def register_video(video_path: str, define_slice: bool = False, start_frame: int = 0, end_frame: str = 100, sampling_rate: int = 3, smoothing_width: int = 8) -> None:
    """Performs stabilization on a video using simpleElastix and some homebrew algorithms for smoothing.

    Args:
        video_path (str): path to the video file
        define_slice (bool, optional): To perform only on subset of video. Defaults to False.
        start_frame (int, optional): If define_slice, which slice to start with. Defaults to None.
        end_frame (str, optional): If define_slice which slice to end with. Defaults to None.
        sampling_rate (int, optional): Every how many slices to perform registration. Defaults to 3.
        smoothing_width (int, optional): How wide should the window be for the median smoothing. Defaults to 5.

    """

    # Read video and decide on reference slice
    video = sitk.ReadImage(video_path)

    video_array = sitk.GetArrayFromImage(video)

    number_of_slices = video_array.shape[0]
    middle_slice = video_array[number_of_slices // 2]
    middle_img = sitk.GetImageFromArray(middle_slice)

    # Cropping the video length if define_slice
    if define_slice:
        video_array = video_array[start_frame:end_frame]

    # Construct the elastix imag filter
    elastixImageFilter = sitk.ElastixImageFilter()
    elastixImageFilter.SetParameterMap(sitk.GetDefaultParameterMap("rigid"))
    elastixImageFilter.SetFixedImage(middle_img)
    elastixImageFilter.SetLogToConsole(False)

    # Do registration for every third slice and save only the transformation parameters
    transform_params = np.zeros((number_of_slices, 3))

    for i in tqdm(range(0, len(video_array), sampling_rate)):
        elastixImageFilter.SetMovingImage(
            sitk.GetImageFromArray(video_array[i]))
        elastixImageFilter.Execute()

        param_map = elastixImageFilter.GetTransformParameterMap()[0]
        transform_params[i] = ([float(i)
                               for i in param_map['TransformParameters']])

    center_of_rotation = np.array(
        [float(i) for i in param_map['CenterOfRotationPoint']])

    # Extract two arrays of parameters, each with every sixth image filled and a faze shift of 3 images
    first_transform_array = np.empty(transform_params.shape)
    second_transform_array = np.empty(transform_params.shape)

    first_transform_array[:] = np.nan
    second_transform_array[:] = np.nan

    for i in range(0, len(transform_params), sampling_rate):
        if i % (2*sampling_rate) == 0:
            first_transform_array[i] = transform_params[i]
        else:
            second_transform_array[i] = transform_params[i]

    # Interpolate in between the set parameters

    # Execute interpolation and combine by taking the mean
    first_transform_array = interpolate_array(
        first_transform_array, 0, 2*sampling_rate)

    second_transform_array = interpolate_array(
        second_transform_array, sampling_rate, 2*sampling_rate)

    total_transform_array = (first_transform_array +
                             second_transform_array) / 2

    # Now perform median-smoothing
    smooth_transform_array = copy.deepcopy(total_transform_array)

    for i in range(smoothing_width, len(total_transform_array)):
        smooth_transform_array[i] = np.median(
            total_transform_array[i-smoothing_width:i+1+smoothing_width], axis=0)

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
    if not define_slice:
        out_image.CopyInformation(video)

    print('Saving...')
    out_image = sitk.Cast(out_image, video.GetPixelID())
    sitk.WriteImage(out_image, f'{video_path[:-4]}_fixed.tif')


if __name__ == '__main__':
    video_path = '2022_08_25_ 000001_AFW.tif'
    register_video(video_path, define_slice=True, start_frame=3100,
                   end_frame=3300, sampling_rate=5, smoothing_width=8)
