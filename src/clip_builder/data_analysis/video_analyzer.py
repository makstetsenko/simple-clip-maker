import cv2
import numpy as np
from dataclasses import dataclass
from typing import List, Literal
from skimage.metrics import structural_similarity as ssim


IntensityLevel = Literal["low", "medium", "high"]


@dataclass
class SceneInfo:
    index: int
    start_time: float
    end_time: float
    duration: float
    intensity_score: float  # normalized 0–1 (relative intensity)
    intensity_level: IntensityLevel
    is_static: bool
    hist_diff: float
    diff_norm: float

    def to_json(self):
        return {
            "index": self.index,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "intensity_score": self.intensity_score,
            "intensity_level": self.intensity_level,
            "is_static": self.is_static,
            "hist_diff": self.hist_diff,
            "diff_norm": self.diff_norm,
        }

    @staticmethod
    def from_json(value: dict):
        return SceneInfo(
            index=value["index"],
            start_time=value["start_time"],
            end_time=value["end_time"],
            duration=value["duration"],
            intensity_score=value["intensity_score"],
            intensity_level=value["intensity_level"],
            is_static=value["is_static"],
            hist_diff=value["hist_diff"],
            diff_norm=value["diff_norm"],
        )


# w_hist, w_ssim, w_edge, w_flow
# They directly change combined_diff, so they affect where cuts are:
# Increase w_hist → cuts driven more by color/lighting changes.
# Increase w_ssim → cuts driven more by structural changes.
# Increase w_edge → cuts driven more by edge-structure changes.
# Increase w_flow → cuts driven more by motion discontinuities.


def analyze_video_scenes(
    video_path: str,
    frame_step: int = 2,  # sample every Nth frame (affects scene count)
    scene_k_sigma: float = 2,  # threshold = mean + k * std of combined diff
    min_scene_duration: float = 1.0,  # merge scenes shorter than this (sec)
    w_hist: float = 0.4,
    w_ssim: float = 0.3,
    w_edge: float = 0.2,
    w_flow: float = 0.1,
) -> List[SceneInfo]:
    """
    Detect scenes using a combination of:
      - color histogram diff
      - structural diff (SSIM)
      - edge map diff
      - optical flow magnitude

    Then compute a relative intensity_score (0–1) and intensity_level per scene.
    All exposed parameters influence scene count / placement.
    """

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 24

    # Per-frame metrics
    times: List[float] = []

    hist_diffs: List[float] = []
    ssim_diffs: List[float] = []
    edge_diffs: List[float] = []
    flow_mags: List[float] = []

    # Also collect basic features for per-scene intensity
    motions: List[float] = []
    edge_densities: List[float] = []
    brightnesses: List[float] = []

    prev_frame = None
    prev_gray = None
    prev_edges = None
    prev_hist = None
    prev_flow = None

    frame_idx = 0

    scale = 0.3

    while True:
        ret, frame_normal = cap.read()
        if not ret:
            break

        if frame_idx % frame_step != 0:
            frame_idx += 1
            continue

        t = frame_idx / fps
        times.append(t)

        frame = cv2.resize(frame_normal, (0, 0), fx=scale, fy=scale)

        # increase contrast
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=3.5, tileGridSize=(4, 4))
        gray = clahe.apply(gray)

        # ----- per-frame basic features (for intensity later) -----
        brightness = float(gray.mean())
        brightnesses.append(brightness)

        if prev_gray is None:
            motion = 0.0
        else:
            diff = cv2.absdiff(gray, prev_gray)
            motion = float(diff.mean())
        motions.append(motion)

        edges = cv2.Canny(gray, 50, 150)
        edge_density = float(np.count_nonzero(edges)) / edges.size
        edge_densities.append(edge_density)

        # ----- histogram diff (HSV) -----
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        hsv[..., 2] = clahe.apply(hsv[..., 2])  # boost V (brightness)
        hist = cv2.calcHist([hsv], [0, 1], None, [32, 32], [0, 180, 0, 256])  # bins for H and S
        cv2.normalize(hist, hist)

        if prev_hist is None:
            hist_diff = 0.0
        else:
            hist_diff = float(cv2.compareHist(prev_hist, hist, cv2.HISTCMP_BHATTACHARYYA))
        hist_diffs.append(hist_diff)
        prev_hist = hist

        # ----- SSIM diff (structural difference) -----
        if prev_gray is None:
            ssim_diff = 0.0
        else:
            ssim_score, _ = ssim(prev_gray, gray, full=True)
            ssim_diff = float(1.0 - ssim_score)  # 0 = same, 1 = very different
        ssim_diffs.append(ssim_diff)

        # ----- edge map diff -----
        if prev_edges is None:
            edge_diff = 0.0
        else:
            # edges are 0/255; normalize to 0–1 before diff
            edge_norm = edges.astype(np.float32) / 255.0
            prev_edge_norm = prev_edges.astype(np.float32) / 255.0
            edge_diff = float(np.mean(np.abs(edge_norm - prev_edge_norm)))
        edge_diffs.append(edge_diff)
        prev_edges = edges

        # ----- optical flow magnitude -----
        if prev_gray is None:
            flow_mag = 0.0
        else:
            flow = cv2.calcOpticalFlowFarneback(
                prev_gray,
                gray,
                None,
                pyr_scale=0.5,
                levels=3,
                winsize=15,
                iterations=3,
                poly_n=5,
                poly_sigma=1.2,
                flags=0,
            )
            mag = np.sqrt(flow[..., 0] ** 2 + flow[..., 1] ** 2)
            flow_mag = float(np.mean(mag))
        flow_mags.append(flow_mag)
        prev_flow = flow if prev_gray is not None else None

        prev_gray = gray
        prev_frame = frame
        frame_idx += 1

    cap.release()

    n = len(times)
    if n == 0:
        return []

    # make numpy arrays
    hist_arr = np.array(hist_diffs)
    ssim_arr = np.array(ssim_diffs)
    edge_arr = np.array(edge_diffs)
    flow_arr = np.array(flow_mags)

    # because first frame has 0.0 for all metrics, lengths should match n
    # but if off by one due to first-frame logic, pad or trim
    def ensure_len(x: np.ndarray, target: int) -> np.ndarray:
        if len(x) == target:
            return x
        if len(x) > target:
            return x[:target]
        # pad with first value
        if len(x) == 0:
            return np.zeros(target, dtype=np.float32)
        pad_val = x[0]
        pad = np.full(target - len(x), pad_val, dtype=x.dtype)
        return np.concatenate([x, pad])

    hist_arr = ensure_len(hist_arr, n)
    ssim_arr = ensure_len(ssim_arr, n)
    edge_arr = ensure_len(edge_arr, n)
    flow_arr = ensure_len(flow_arr, n)

    motions_arr = ensure_len(np.array(motions), n)
    edge_density_arr = ensure_len(np.array(edge_densities), n)
    brightness_arr = ensure_len(np.array(brightnesses), n)

    # ----- normalize each diff metric to 0–1 -----
    def norm(x: np.ndarray) -> np.ndarray:
        min_v, max_v = float(x.min()), float(x.max())
        if max_v - min_v < 1e-6:
            return np.zeros_like(x)
        return (x - min_v) / (max_v - min_v)

    hist_n = norm(hist_arr)
    ssim_n = norm(ssim_arr)
    edge_n = norm(edge_arr)
    flow_n = norm(flow_arr)

    # normalize weights so their sum = 1.0 (optional but nice)
    w_sum = w_hist + w_ssim + w_edge + w_flow
    if w_sum <= 0:
        w_hist = w_ssim = w_edge = w_flow = 0.25
        w_sum = 1.0
    w_hist /= w_sum
    w_ssim /= w_sum
    w_edge /= w_sum
    w_flow /= w_sum

    # ----- combined difference per frame (this drives cuts) -----
    combined_diff = w_hist * hist_n + w_ssim * ssim_n + w_edge * edge_n + w_flow * flow_n

    # ignore first few frames for stats to avoid startup artifacts
    diffs_for_stats = combined_diff[5:] if n > 5 else combined_diff
    mean_diff = float(diffs_for_stats.mean())
    std_diff = float(diffs_for_stats.std()) if diffs_for_stats.size > 1 else 0.0

    threshold = mean_diff + scene_k_sigma * std_diff

    # ----- find initial scene boundaries (by combined_diff threshold) -----
    scene_start_idxs: List[int] = [0]
    for i in range(1, n):
        if combined_diff[i] > threshold:
            scene_start_idxs.append(i)

    # convert to (start_idx, end_idx)
    scene_ranges: List[tuple[int, int]] = []
    for i, start_idx in enumerate(scene_start_idxs):
        if i + 1 < len(scene_start_idxs):
            end_idx = scene_start_idxs[i + 1] - 1
        else:
            end_idx = n - 1
        if end_idx < start_idx:
            end_idx = start_idx
        scene_ranges.append((start_idx, end_idx))

    # ----- merge very short scenes -----
    merged_ranges: List[tuple[int, int]] = []
    for start_idx, end_idx in scene_ranges:
        start_t = times[start_idx]
        end_t = times[end_idx]
        duration = end_t - start_t

        if not merged_ranges:
            merged_ranges.append((start_idx, end_idx))
            continue

        if duration < min_scene_duration:
            prev_start, prev_end = merged_ranges[-1]
            merged_ranges[-1] = (prev_start, end_idx)
        else:
            merged_ranges.append((start_idx, end_idx))

    if not merged_ranges:
        return []

    # ----- compute per-frame intensity (for scene intensity) -----
    motions_n = norm(motions_arr)
    edges_density_n = norm(edge_density_arr)
    bright_n = norm(brightness_arr)

    # fixed internal weights for intensity (do not affect scene count)
    im_w_motion, im_w_edge, im_w_bright = 0.5, 0.3, 0.2
    frame_intensity = im_w_motion * motions_n + im_w_edge * edges_density_n + im_w_bright * bright_n

    # ----- aggregate intensity per scene -----
    scene_scores: List[float] = []
    scene_times: List[tuple[float, float]] = []

    for start_idx, end_idx in merged_ranges:
        scores = frame_intensity[start_idx : end_idx + 1]
        if scores.size == 0:
            continue
        score = float(scores.mean())
        scene_scores.append(score)
        scene_times.append((times[start_idx], times[end_idx]))

    if not scene_scores:
        return []

    scene_scores_arr = np.array(scene_scores)
    scene_scores_norm = norm(scene_scores_arr)

    # classify into low/medium/high based on quantiles (relative)
    if len(scene_scores_norm) >= 3:
        q_low, q_high = np.quantile(scene_scores_norm, [0.33, 0.66])
    else:
        q_low, q_high = 0.33, 0.66

    def level(score_norm: float) -> IntensityLevel:
        if score_norm <= q_low:
            return "low"
        elif score_norm <= q_high:
            return "medium"
        else:
            return "high"

    scenes: List[SceneInfo] = []
    for idx, ((start_t, end_t), score_norm) in enumerate(zip(scene_times, scene_scores_norm)):
        scenes.append(
            SceneInfo(
                index=idx,
                start_time=start_t,
                end_time=end_t,
                duration=end_t - start_t,
                intensity_score=float(score_norm),
                intensity_level=level(score_norm),
            )
        )

    return scenes


def analyze_on_static_scenes(
    video_path: str,
    time_step: float = 0.3,  # analyze every time_step seconds
    scene_duration_threshold: float = 2,  # minimum scene duration in seconds to accept into result
    scale: float = 0.5,  # downscale for speed
    STATIC_THRESHOLD: float = 0.01,  # <2% frame change = static
    MOTION_CUT_THRESHOLD: float = 0.15,  # >15% change = strong change
    HARD_CUT_THRESHOLD: float = 0.2,  # >15% hist diff = hard cut
) -> List[SceneInfo]:

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError("Cannot open video")

    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    frame_idx = 0
    frame_step = int(fps * time_step)

    prev_gray = None
    prev_hist = None

    scenes: List[SceneInfo] = []
    scene_start_t = 0.0
    scene_is_static = True  # assume static first
    scene_counter = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % frame_step != 0:
            frame_idx += 1
            continue

        t = frame_idx / fps

        # --- preprocessing ---
        frame_small = cv2.resize(frame, (0, 0), fx=scale, fy=scale)
        gray = cv2.cvtColor(frame_small, cv2.COLOR_BGR2GRAY)

        # histogram on gray gives best speed
        hist = cv2.calcHist([gray], [0], None, [32], [0, 256])
        cv2.normalize(hist, hist)

        if prev_gray is None:
            # first frame → start scene
            prev_gray = gray
            prev_hist = hist
            frame_idx += 1
            continue

        # movement metric
        diff = float(np.mean(np.abs(gray.astype(float) - prev_gray.astype(float))))
        diff_norm = diff / 255.0

        # histogram diff (hard cuts)
        hist_diff = float(cv2.compareHist(prev_hist, hist, cv2.HISTCMP_BHATTACHARYYA))

        # --- classify frame ---
        if hist_diff > HARD_CUT_THRESHOLD and diff_norm > MOTION_CUT_THRESHOLD:
            frame_type = "hard_cut"
        elif diff_norm < STATIC_THRESHOLD:
            frame_type = "static"
        else:
            frame_type = "changing"

        # --- detect scene boundary ---
        should_split = False

        if frame_type == "hard_cut":
            should_split = True

        else:
            # transitions between static ↔ changing
            if frame_type == "static" and scene_is_static is False:
                should_split = True
            if frame_type == "changing" and scene_is_static is True:
                should_split = True

        duration = t - scene_start_t
        if should_split and duration >= scene_duration_threshold:
            # close previous scene
            scenes.append(
                SceneInfo(
                    index=scene_counter,
                    start_time=scene_start_t,
                    end_time=t,
                    duration=duration,
                    is_static=scene_is_static,
                    intensity_level="low",
                    intensity_score=0,
                    hist_diff=hist_diff,
                    diff_norm=diff_norm,
                )
            )
            scene_counter += 1

            # start new scene
            scene_start_t = t
            scene_is_static = frame_type == "static"

        # update previous frame
        prev_gray = gray
        prev_hist = hist
        frame_idx += 1

    # close last scene
    scenes.append(
        SceneInfo(
            index=scene_counter,
            start_time=scene_start_t,
            end_time=frame_idx / fps,
            duration=frame_idx / fps - scene_start_t,
            is_static=scene_is_static,
            intensity_level="low",
            intensity_score=0,
            hist_diff=hist_diff,
            diff_norm=diff_norm,
        )
    )

    cap.release()
    return scenes


@dataclass
class VideoFileDetails:
    duration: float  # seconds
    resolution: tuple[int, int]
    fps: int


def video_details(path):
    cap = cv2.VideoCapture(path)

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)

    duration = frame_count / fps if fps > 0 else 0

    cap.release()

    return VideoFileDetails(duration=duration, resolution=(width, height), fps=fps)
