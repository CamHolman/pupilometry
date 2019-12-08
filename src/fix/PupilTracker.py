from collections import defaultdict

import numpy as np
import matplotlib
import pandas as pd

matplotlib.use('agg')

try:
    import cv2
except ImportError:
    print("Could not find cv2. You won't be able to use the pupil tracker.")

class PupilTracker:
    """
    Parameters:

    perc_high                    : float        # upper percentile for bright pixels
    perc_low                     : float        # lower percentile for dark pixels
    perc_weight                  : float        # threshold will be perc_weight*perc_low + (1- perc_weight)*perc_high
    relative_area_threshold      : float        # enclosing rotating rectangle has to have at least that amount of area
    ratio_threshold              : float        # ratio of major and minor radius cannot be larger than this
    error_threshold              : float        # threshold on the RMSE of the ellipse fit
    min_contour_len              : int          # minimal required contour length (must be at least 5)
    margin                       : float        # relative margin the pupil center should not be in
    contrast_threshold           : float        # contrast below that threshold are considered dark
    speed_threshold              : float        # eye center can at most move that fraction of the roi between frames
    dr_threshold                 : float        # maximally allow relative change in radius

    """

    def __init__(self, param):
        self._params = param
        self._center = None
        self._radius = None
        self._last_detection = 1

    @staticmethod
    def goodness_of_fit(contour, ellipse):
        center, size, angle = ellipse
        angle *= np.pi / 180
        err = 0
        for coord in contour.squeeze().astype(np.float):
            posx = (coord[0] - center[0]) * np.cos(-angle) - (coord[1] - center[1]) * np.sin(-angle)
            posy = (coord[0] - center[0]) * np.sin(-angle) + (coord[1] - center[1]) * np.cos(-angle)
            err += ((posx / size[0]) ** 2 + (posy / size[1]) ** 2 - 0.25) ** 2

        return np.sqrt(err / len(contour))

    @staticmethod
    def restrict_to_long_axis(contour, ellipse, corridor):
        center, size, angle = ellipse
        angle *= np.pi / 180
        R = np.asarray([[np.cos(-angle), - np.sin(-angle)], [np.sin(-angle), np.cos(-angle)]])
        contour = np.dot(contour.squeeze() - center, R.T)
        contour = contour[np.abs(contour[:, 0]) < corridor * ellipse[1][1] / 2]
        return (np.dot(contour, R) + center).astype(np.int32)

    def get_pupil_from_contours(self, contours, small_gray, show_matching=5):
        ratio_thres = self._params['ratio_threshold']
        area_threshold = self._params['relative_area_threshold']
        error_threshold = self._params['error_threshold']
        min_contour = self._params['min_contour_len']
        margin = self._params['margin']
        speed_thres = self._params['speed_threshold']
        dr_thres = self._params['dr_threshold']
        err = np.inf
        best_ellipse = None
        best_contour = None
        results, cond  = defaultdict(list), defaultdict(list)

        for j, cnt in enumerate(contours):
            if len(contours[j]) < min_contour:  # otherwise fitEllipse won't work
                continue

            ellipse = cv2.fitEllipse(contours[j])
            ((x, y), axes, angle) = ellipse
            if min(axes) == 0:  # otherwise ratio won't work
                continue

            ratio = max(axes) / min(axes)
            area = np.prod(ellipse[1]) / np.prod(small_gray.shape)
            curr_err = self.goodness_of_fit(cnt, ellipse)

            results['ratio'].append(ratio)
            results['area'].append(area)
            results['rmse'].append(curr_err)
            results['x coord'].append(x / small_gray.shape[1])
            results['y coord'].append(y / small_gray.shape[0])

            center = np.array([x / small_gray.shape[1], y / small_gray.shape[0]])
            r = max(axes)

            dr = 0 if self._radius is None else np.abs(r - self._radius) / self._radius
            dx = 0 if self._center is None else np.sqrt(np.sum((center - self._center) ** 2))

            results['dx'].append(dx)
            results['dr/r'].append(dr)
            matching_conditions = 1 * (ratio <= ratio_thres) + 1 * (area >= area_threshold) \
                                  + 1 * (curr_err < error_threshold) \
                                  + 1 * (margin < center[0] < 1 - margin) \
                                  + 1 * (margin < center[1] < 1 - margin) \
                                  + 1 * (dx < speed_thres * self._last_detection) \
                                  + 1 * (dr < dr_thres * self._last_detection)
            cond['ratio'].append(ratio <= ratio_thres)
            cond['area'].append(area >= area_threshold)
            cond['rmse'].append(curr_err < error_threshold)
            cond['x coord'].append(margin < center[0] < 1 - margin)
            cond['y coord'].append(margin < center[1] < 1 - margin)
            cond['dx'].append(dx < speed_thres * self._last_detection)
            cond['dr/r'].append(dr < dr_thres * self._last_detection)

            results['conditions'] = matching_conditions
            cond['conditions'].append(True)

            if curr_err < err and matching_conditions == 7:
                best_ellipse = ellipse
                best_contour = cnt
                err = curr_err
                cv2.ellipse(small_gray, ellipse, (0, 0, 255), 2)
            elif matching_conditions >= show_matching:
                cv2.ellipse(small_gray, ellipse, (255, 0, 0), 2)

        if best_ellipse is None:
            df = pd.DataFrame(results)
            df2 = pd.DataFrame(cond)

            # print('-', end="", flush=True)
            if np.any(df['conditions'] >= show_matching):

                idx = df['conditions'] >= show_matching
                df = df[idx]
                df2 = df2[idx]
                df[df2] = np.nan
                # print("\n", df, flush=True)
            self._last_detection += 1
        else:
            self._last_detection = 1

        return best_contour, best_ellipse

    def preprocess_image(self, frame, eye_roi):
        h = int(self._params['gaussian_blur'])
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        img_std = np.std(gray)

        small_gray = gray[slice(*eye_roi[0]), slice(*eye_roi[1])]
        blur = cv2.GaussianBlur(small_gray, (h, h), 0)
        _, thres = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return gray, small_gray, img_std, thres, blur

    @staticmethod
    def display(gray, blur, thres, eye_roi, fr_count, n_frames, ncontours = 0, contour=None, ellipse=None, eye_center=None,
                font=cv2.FONT_HERSHEY_SIMPLEX):
        cv2.imshow('blur', blur)
        cv2.imshow('threshold', thres)

        if contour is not None and ellipse is not None and eye_center is not None:
            cv2.putText(gray, "{fr_count}/{frames} {ncontours}".format(fr_count=fr_count, frames=n_frames,
                                                                       ncontours=ncontours),
                        (10, 30), font, 1, (127, 127, 127), 2)
            ellipse = list(ellipse)
            ellipse[0] = tuple(eye_center)
            ellipse = tuple(ellipse)
            cv2.drawContours(gray, [contour], 0, (255, 0, 0), 1, offset=tuple(eye_roi[::-1, 0]))
            cv2.ellipse(gray, ellipse, (0, 0, 255), 2)
            epy, epx = np.round(eye_center).astype(int)
            gray[epx - 3:epx + 3, epy - 3:epy + 3] = 0
        cv2.imshow('frame', gray)

    def track(self, videofile, eye_roi, display=False):

        #print ("Made it inside track")

        
        contrast_low = self._params['contrast_threshold']

        #print("Tracking videofile", videofile)
        cap = cv2.VideoCapture(videofile)
        traces = []

        n_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fr_count = 0
        while cap.isOpened():
            if fr_count >= n_frames:
                print("Reached end of videofile ", videofile)
                break

            # --- read frame
            ret, frame = cap.read()
            fr_count += 1
            
            # print ("Current frame is:", fr_count)

            # --- if we don't get a frame, don't add any tracking results
            if not ret:
                traces.append(dict(frame_id=fr_count))
                continue

            # --- print out if there's not display
            if fr_count % 500 == 0:
                print("\tframe ({}/{})".format(fr_count, n_frames))

            # --- preprocess and treshold images
            gray, small_gray, img_std, thres, blur = self.preprocess_image(frame, eye_roi)

            # --- if contrast is too low, skip it
            if img_std < contrast_low:
                traces.append(dict(frame_id=fr_count,
                                   frame_intensity=img_std))
                #print ('_', end="", flush=True)
                if display:
                    self.display(gray, blur, thres, eye_roi, fr_count, n_frames)
                continue

            # --- detect contours
            ellipse, eye_center, contour = None, None, None
            
            ## Note: modifying the below to expect 2 outputs due to differences between OpenCV2,3,4
            ## See Link: https://stackoverflow.com/questions/20851365/opencv-contours-need-more-than-2-values-to-unpack
            
            #_, contours, hierarchy1 = cv2.findContours(thres, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            contours, hierarchy1 = cv2.findContours(thres, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            contour, ellipse = self.get_pupil_from_contours(contours, small_gray)
            if display:
                self.display(gray, blur, thres, eye_roi, fr_count, n_frames, ncontours=len(contours))


            if contour is None:
                traces.append(dict(frame_id=fr_count, frame_intensity=img_std))
            else:
                eye_center = eye_roi[::-1, 0] + np.asarray(ellipse[0])
                self._center = np.asarray(ellipse[0]) / np.asarray(small_gray.shape[::-1])
                self._radius = max(ellipse[1])

                traces.append(dict(center=eye_center,
                                   major_r=np.max(ellipse[1]),
                                   rotated_rect=np.hstack(ellipse),
                                   contour=contour.astype(np.int16),
                                   frame_id=fr_count,
                                   frame_intensity=img_std
                                   ))
            if display:
                self.display(gray, blur, thres, eye_roi, fr_count, n_frames, ellipse=ellipse,
                             eye_center=eye_center, contour=contour, ncontours=len(contours))
            if (cv2.waitKey(1) & 0xFF == ord('q')):
                raise PipelineException('Tracking aborted')

        cap.release()
        cv2.destroyAllWindows()

        return traces
