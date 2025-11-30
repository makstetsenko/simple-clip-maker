import numpy as np
import scipy.signal
import librosa


class GetPeaksCriteria:
    def __init__(
        self,
        hop_length: int = 128,
        peaks_height: list[float] = [0, 1],
        peaks_distance: int = 20,
        peaks_prominence: float = 0.2,
    ):
        self.hop_length = hop_length
        self.peaks_height = peaks_height
        self.peaks_distance = peaks_distance
        self.peaks_prominence = peaks_prominence


class GetPeaksResponse:
    def __init__(self, peaks, sample_rate, norm_energy, amplitude_values):
        self.peaks = peaks
        self.sample_rate = sample_rate
        self.norm_energy = norm_energy
        self.amplitude_values = amplitude_values


def get_energy(y, hop_length):
    frame_length = 1024

    energy = np.array([np.sum(np.abs(y[i : i + frame_length] ** 2)) for i in range(0, len(y), hop_length)])
    energy = np.array(energy)

    return energy


def get_norimized_energy(energy):
    norm_energy = (energy - energy.min()) / (energy.max() - energy.min())
    return norm_energy


def get_peaks_with_sample_rate_with_normalized_energy_with_amplitude_values(
    audio_file_path, criteria: GetPeaksCriteria
) -> GetPeaksResponse:

    amplitude_values, sample_rate = librosa.load(audio_file_path, sr=None)

    energy = get_energy(amplitude_values, criteria.hop_length)

    norm_energy = (energy - energy.min()) / (energy.max() - energy.min())

    peaks, _ = scipy.signal.find_peaks(
        norm_energy,
        height=criteria.peaks_height,
        distance=criteria.peaks_distance,
        prominence=criteria.peaks_prominence,
    )  # distance avoids close double-peaks

    return GetPeaksResponse(peaks, sample_rate, norm_energy, amplitude_values)
