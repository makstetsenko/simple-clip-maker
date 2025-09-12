import numpy as np
import scipy.signal
import librosa


# Adjust values for specific music file 
hop_length = 512
peaks_height = [0, 1]
peaks_distance = 20
peaks_prominence = 0.2


def get_energy(y):
    frame_length = 2048
    
    energy = np.array([
        np.sum(np.abs(y[i:i+frame_length]**2))
        for i in range(0, len(y), hop_length)
    ])
    energy = np.array(energy)
    
    return energy


def get_norimized_energy(energy):
    norm_energy = (energy - energy.min()) / (energy.max() - energy.min())
    return norm_energy


def get_peaks_with_sample_rate_with_normalized_energy_with_amplitude_values(audio_file_path):
    
    amplitude_values, sample_rate = librosa.load(audio_file_path, sr=None)
    
    energy = get_energy(amplitude_values)
    
    norm_energy = (energy - energy.min()) / (energy.max() - energy.min())
    
    peaks, _ = scipy.signal.find_peaks(norm_energy, height=peaks_height, distance=peaks_distance, prominence=peaks_prominence)  # distance avoids close double-peaks
    
    return (peaks, sample_rate, norm_energy, amplitude_values)