import numpy as np
import librosa
from numpy.linalg import norm


class IntensityBand:
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class BeatTrend:
    """
    Describes trending intensity.

    For example:

    t0->t1

    IF t0.intensity = medium and t1.intensity = low THEN t0.trend = down

    IF t0.intensity = medium and t1.intensity = hight THEN t0.trend = up

    IF t0.intensity = medium and t1.intensity = medium THEN t0.trend = flat
    """

    UP = "up"
    FLAT = "flat"
    DOWN = "down"


class BeatSegment:
    def __init__(
        self,
        index: int,
        start_time: float,
        energy: float,
        intensity_band: str,
        energy_delta: float,
        trend: str,
        similar_group: int,
        reverse_candidate: bool,
    ):
        self.index = index
        self.start_time = start_time
        self.end_time = None
        self.energy = energy
        self.intensity_band = intensity_band
        self.energy_delta = energy_delta
        self.trend = trend
        self.similar_group = similar_group
        self.reverse_candidate = reverse_candidate
        self.next: BeatSegment | None = None
        self.duration = 0

    @staticmethod
    def create_default():
        return BeatSegment(
            index=0,
            start_time=0,
            energy=0,
            intensity_band=IntensityBand.LOW,
            energy_delta=0,
            reverse_candidate=False,
            similar_group=0,
            trend=BeatTrend.FLAT,
        )

    def set_end_time(self, end_time):
        self.end_time = end_time
        self.duration = end_time - self.start_time

    def to_json(self):
        return {
            "index": self.index,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "energy": self.energy,
            "intensity_band": self.intensity_band,
            "energy_delta": self.energy_delta,
            "trend": self.trend,
            "similar_group": self.similar_group,
            "reverse_candidate": self.reverse_candidate,
        }

    @staticmethod
    def from_json(value: dict):
        segment = BeatSegment(
            index=value["index"],
            start_time=value["start_time"],
            energy=value["energy"],
            intensity_band=value["intensity_band"],
            energy_delta=value["energy_delta"],
            trend=value["trend"],
            similar_group=value["similar_group"],
            reverse_candidate=value["reverse_candidate"],
        )
        segment.set_end_time(end_time=value["end_time"])
        return segment


class BeatGrid:
    def __init__(self, beats: list[float], half: list[float], double: list[float]):
        self.beats = beats
        self.half = half
        self.double = double

    def to_json(self):
        return {
            "beats": self.beats,
            "half": self.half,
            "double": self.double,
        }

    @staticmethod
    def from_json(value: dict):
        return BeatGrid(beats=value["beats"], double=value["double"], half=value["half"])


class AudioAnalyzeResult:
    def __init__(self, sample_rate: int, duration: float, tempo: float, grid: BeatGrid, beat_segments: list[BeatSegment]):
        self.sample_rate = sample_rate
        self.duration = duration
        self.tempo = tempo
        self.grid = grid
        self.beat_segments = beat_segments

    def to_json(self):
        return {
            "sample_rate": self.sample_rate,
            "duration": self.duration,
            "tempo": self.tempo,
            "grid": self.grid.to_json(),
            "beat_segments": [b.to_json() for b in self.beat_segments],
        }

    @staticmethod
    def from_json(value: dict):
        return AudioAnalyzeResult(
            sample_rate=value["sample_rate"],
            duration=value["duration"],
            tempo=value["tempo"],
            grid=BeatGrid.from_json(value["grid"]),
            beat_segments=[BeatSegment.from_json(b) for b in value["beat_segments"]],
        )


def subdivide_beats(beat_times: np.ndarray, subdivision: int = 2) -> np.ndarray:
    """Create sub-beat grid between beats (for double-time, etc.)."""
    if len(beat_times) < 2:
        return beat_times.copy()

    grid = []
    for i in range(len(beat_times) - 1):
        start = beat_times[i]
        end = beat_times[i + 1]
        step = (end - start) / subdivision
        for s in range(subdivision):
            grid.append(start + s * step)
    grid.append(beat_times[-1])
    return np.array(grid)


def analyze_music_for_editing(
    audio_path: str, hop_length: int = 512, n_mfcc: int = 5, similarity_threshold: float = 0.8
) -> AudioAnalyzeResult:
    # 1. Load
    y, sr = librosa.load(audio_path, sr=None)
    duration = librosa.get_duration(y=y, sr=sr)

    # 2. Beat / rhythm grid
    onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_length)
    tempo, beat_frames = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr, hop_length=hop_length)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr, hop_length=hop_length)

    # 3. Energy + simple timbre features per frame
    rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]
    mfcc = librosa.feature.mfcc(y=y, sr=sr, hop_length=hop_length, n_mfcc=n_mfcc)

    frame_times = librosa.frames_to_time(np.arange(len(onset_env)), sr=sr, hop_length=hop_length)

    # 4. Sample features at each beat (nearest frame)
    feat_per_beat = []
    per_beat_energy = []
    for t in beat_times:
        idx = int(np.argmin(np.abs(frame_times - t)))
        # raw energy at this beat
        e = rms[idx] if idx < len(rms) else rms[-1]
        per_beat_energy.append(e)

        # feature vector for similarity (onset + energy + MFCCs)
        f = [onset_env[idx], e]
        if idx < mfcc.shape[1]:
            f.extend(mfcc[:, idx])
        else:
            f.extend(mfcc[:, -1])
        feat_per_beat.append(f)

    per_beat_energy = np.array(per_beat_energy)
    feat_per_beat = np.array(feat_per_beat)

    # 5. Normalize energy and features
    if per_beat_energy.max() > per_beat_energy.min():
        energy_norm = (per_beat_energy - per_beat_energy.min()) / (per_beat_energy.max() - per_beat_energy.min())
    else:
        energy_norm = np.zeros_like(per_beat_energy)

    # z-score features for similarity
    feat_mean = feat_per_beat.mean(axis=0)
    feat_std = feat_per_beat.std(axis=0) + 1e-8
    feat_norm = (feat_per_beat - feat_mean) / feat_std

    # 6. Energy deltas & trends (for reverse candidates)
    energy_delta = np.zeros_like(energy_norm)
    energy_delta[:-1] = energy_norm[1:] - energy_norm[:-1]

    def classify_trend(d, eps=0.05):
        if d > eps:
            return BeatTrend.UP
        elif d < -eps:
            return BeatTrend.DOWN
        else:
            return BeatTrend.FLAT

    trends = [classify_trend(d) for d in energy_delta]

    # 7. Intensity bands: low / medium / high
    low_thr = 0.33
    high_thr = 0.66

    def band(e):
        if e < low_thr:
            return IntensityBand.LOW
        elif e < high_thr:
            return IntensityBand.MEDIUM
        else:
            return IntensityBand.HIGH

    intensity_bands = [band(e) for e in energy_norm]

    # 8. Very simple grouping for duplication (similar beats)
    n_beats = len(beat_times)
    group_ids = [-1] * n_beats
    current_group = 0

    for i in range(n_beats):
        if group_ids[i] != -1:
            continue
        group_ids[i] = current_group
        vi = feat_norm[i]
        for j in range(i + 1, n_beats):
            vj = feat_norm[j]
            sim = float(np.dot(vi, vj) / (norm(vi) * norm(vj) + 1e-8))
            if sim >= similarity_threshold:
                group_ids[j] = current_group
        current_group += 1

    # 9. Reverse candidates: strong up-down or down-up changes
    reverse_candidates = []
    for i in range(1, n_beats - 1):
        # big local bump or dip
        if (energy_delta[i - 1] > 0.2 and energy_delta[i] < -0.2) or (energy_delta[i - 1] < -0.2 and energy_delta[i] > 0.2):
            reverse_candidates.append(True)
        else:
            reverse_candidates.append(False)
    # pad edges
    reverse_candidates = [False] + reverse_candidates + [False]

    # 10. Build beat objects
    beats = [BeatSegment.create_default()]

    for i, t in enumerate(beat_times):
        descriptor = BeatSegment(
            index=(i + 1),
            start_time=float(t),
            energy=float(energy_norm[i]),
            intensity_band=intensity_bands[i],  # low / medium / high
            energy_delta=float(energy_delta[i]),  # to next beat
            trend=trends[i],  # up / down / flat
            similar_group=int(group_ids[i] + 1),  # group for duplication
            reverse_candidate=bool(reverse_candidates[i]),
        )
        beats[-1].next = descriptor
        beats[-1].set_end_time(descriptor.start_time)
        beats.append(descriptor)

    if len(beats) > 0:
        beats[-1].set_end_time(duration)

    # 11. Multi-resolution grids
    grid_beat = [0] + beat_times
    grid_double = [0] + subdivide_beats(beat_times, subdivision=2)
    grid_half = [0] + beat_times[::2] if len(beat_times) > 1 else beat_times

    return AudioAnalyzeResult(
        sample_rate=int(sr),
        duration=float(duration),
        tempo=float(tempo),
        beat_segments=beats,
        grid=BeatGrid(half=grid_half.tolist(), beats=grid_beat.tolist(), double=grid_double.tolist()),
    )
