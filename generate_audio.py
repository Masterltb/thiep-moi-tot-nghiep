import os
import re
import subprocess
import numpy as np
import wave
import imageio_ffmpeg

SR = 44100

def ks_string(freq, duration, decay=0.992, volume=0.3):
    n = max(2, int(SR / freq))
    buf = np.random.uniform(-1, 1, n).astype(np.float32)
    length = int(SR * duration)
    out = np.zeros(length, dtype=np.float32)
    idx = 0
    # vectorized/accelerated KS or loop
    for i in range(length):
        out[i] = buf[idx]
        nxt = (idx + 1) % n
        buf[idx] = (buf[idx] + buf[nxt]) * 0.5 * decay
        idx = nxt
    return out * volume

def ukulele_chord(notes, duration, downstroke=True, spread_ms=25):
    total_len = int(SR * duration)
    chord_buf = np.zeros(total_len, dtype=np.float32)
    notes_ordered = notes if downstroke else notes[::-1]
    delay_samples = int(SR * (spread_ms / 1000.0) / len(notes))
    for i, freq in enumerate(notes_ordered):
        offset = i * delay_samples
        if offset >= total_len:
            break
        note_dur = duration - (offset / SR)
        pluck = ks_string(freq, note_dur, decay=0.993, volume=0.22)
        chord_buf[offset:offset + len(pluck)] += pluck
    return chord_buf

def synth_ukulele_bgm(total_duration=18.0):
    total_samples = int(SR * total_duration)
    bgm = np.zeros(total_samples, dtype=np.float32)
    
    # Chords: C (261.6, 329.6, 392.0, 523.3), G (246.9, 293.7, 392.0, 493.9), 
    # Am (220.0, 261.6, 329.6, 440.0), F (220.0, 261.6, 349.2, 440.0)
    chords = {
        'C': [261.6, 329.6, 392.0, 523.3],
        'G': [246.9, 293.7, 392.0, 493.9],
        'Am': [220.0, 261.6, 329.6, 440.0],
        'F': [220.0, 261.6, 349.2, 440.0],
        'Em': [246.9, 329.6, 392.0, 493.9],
        'C_high': [261.6, 329.6, 392.0, 523.3, 659.3]
    }
    progression = ['C', 'G', 'Am', 'F', 'C', 'G', 'F', 'C', 'C', 'G', 'Am', 'F', 'C', 'F', 'G', 'C']
    
    bpm = 118
    beat_dur = 60.0 / bpm  # ~0.508 sec
    bar_dur = beat_dur * 2 # 2 beats per chord switch
    
    current_time = 0.0
    chord_idx = 0
    
    while current_time < total_duration:
        c_name = progression[chord_idx % len(progression)]
        c_notes = chords[c_name]
        
        # Strum pattern: Down, down-up-chick-up
        t1 = current_time
        t2 = current_time + beat_dur * 0.5
        t3 = current_time + beat_dur * 1.0
        t4 = current_time + beat_dur * 1.5
        
        for t, is_down, vol_mul in [(t1, True, 1.0), (t2, False, 0.65), (t3, True, 0.85), (t4, False, 0.7)]:
            if t < total_duration:
                s_idx = int(t * SR)
                strum_len = min(0.6, total_duration - t)
                if strum_len > 0.05:
                    strum = ukulele_chord(c_notes, strum_len, downstroke=is_down, spread_ms=20) * vol_mul
                    end_idx = min(total_samples, s_idx + len(strum))
                    bgm[s_idx:end_idx] += strum[:end_idx - s_idx]
        
        current_time += bar_dur
        chord_idx += 1
        
    # Gentle fade out at the end
    fade_len = int(SR * 0.8)
    if total_samples > fade_len:
        fade = np.linspace(1.0, 0.0, fade_len, dtype=np.float32)
        bgm[-fade_len:] *= fade
        
    return bgm * 0.45

def synth_gavel_bang():
    # Wooden block strike + comic thud
    dur = 0.55
    length = int(SR * dur)
    t = np.linspace(0, dur, length, False)
    # Low thud with pitch drop
    freq_sweep = 160 * np.exp(-t * 22) + 55
    thud = np.sin(2 * np.pi * freq_sweep * t) * np.exp(-t * 12)
    # Wood click
    click = np.random.uniform(-1, 1, length) * np.exp(-t * 80)
    # Wood resonance harmonics
    res = np.sin(2 * np.pi * 320 * t) * np.exp(-t * 25) * 0.4 + np.sin(2 * np.pi * 640 * t) * np.exp(-t * 35) * 0.2
    bang = (thud * 0.7 + click * 0.5 + res * 0.3)
    return bang.astype(np.float32) * 0.9

def synth_pop(pitch=800):
    dur = 0.12
    length = int(SR * dur)
    t = np.linspace(0, dur, length, False)
    f = np.linspace(pitch, pitch * 2.2, length)
    pop = np.sin(2 * np.pi * f * t) * np.exp(-t * 35)
    click = np.random.uniform(-1, 1, length) * np.exp(-t * 120) * 0.3
    return (pop + click).astype(np.float32) * 0.65

def synth_stamp_slam():
    dur = 0.7
    length = int(SR * dur)
    t = np.linspace(0, dur, length, False)
    # Heavy low sub boom
    boom = np.sin(2 * np.pi * (80 * np.exp(-t * 15) + 38) * t) * np.exp(-t * 7)
    # Crisp paper smack
    smack = np.random.uniform(-1, 1, length) * np.exp(-t * 45)
    # Comic reverberation
    reverb = np.sin(2 * np.pi * 220 * t) * np.exp(-t * 18) * 0.3
    slam = (boom * 0.8 + smack * 0.6 + reverb * 0.3)
    return slam.astype(np.float32) * 0.95

def synth_confetti_burst():
    dur = 1.4
    length = int(SR * dur)
    t = np.linspace(0, dur, length, False)
    # Party pop snap
    snap = np.sin(2 * np.pi * 500 * np.exp(-t * 40) * t) * np.exp(-t * 25)
    burst = np.random.uniform(-1, 1, length) * np.exp(-t * 18) * 0.5
    # Sparkle chime arpeggio (C6, E6, G6, C7, E7)
    chimes = np.zeros(length, dtype=np.float32)
    pitches = [1046.5, 1318.5, 1567.9, 2093.0, 2637.0]
    for i, p in enumerate(pitches):
        delay = int(SR * (0.05 + i * 0.06))
        rem = length - delay
        if rem > 0:
            t_sub = np.linspace(0, rem / SR, rem, False)
            tone = np.sin(2 * np.pi * p * t_sub) * np.exp(-t_sub * 4) * 0.18
            chimes[delay:] += tone
    party = (snap * 0.6 + burst * 0.4 + chimes * 0.8)
    return party.astype(np.float32) * 0.85

def load_audio_file(filepath):
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    out_wav = filepath + '.tmp.wav'
    subprocess.run([ffmpeg_exe, '-y', '-i', filepath, '-ar', str(SR), '-ac', '1', out_wav],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    with wave.open(out_wav, 'rb') as wf:
        n = wf.getnframes()
        data = wf.readframes(n)
        samples = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
    try:
        os.remove(out_wav)
    except:
        pass
    return samples

def main():
    total_sec = 18.0
    total_samples = int(SR * total_sec)
    master = np.zeros(total_samples, dtype=np.float32)

    print("Synthesizing ukulele background track...")
    bgm = synth_ukulele_bgm(total_sec)
    master += bgm

    print("Adding sound effects...")
    def add_sfx(sound, at_sec, gain=1.0):
        start = int(at_sec * SR)
        end = min(total_samples, start + len(sound))
        master[start:end] += sound[:end - start] * gain

    # SFX 1: Gavel BANG at 0.4s
    add_sfx(synth_gavel_bang(), 0.38, gain=1.0)

    # SFX 2: Polaroid pops during montage
    add_sfx(synth_pop(700), 4.35, gain=0.9)
    add_sfx(synth_pop(850), 5.4, gain=0.9)
    add_sfx(synth_pop(1000), 6.5, gain=0.9)
    add_sfx(synth_pop(1150), 7.6, gain=0.9)

    # SFX 3: Giant Stamp SLAM at 11.2s
    add_sfx(synth_stamp_slam(), 11.2, gain=1.1)

    # SFX 4: Confetti explosion at 13.8s
    add_sfx(synth_confetti_burst(), 13.8, gain=1.0)

    print("Adding dialogue voice lines...")
    # Voice 1: Shot 1 at 0.75s
    v1 = load_audio_file('shot1.mp3')
    add_sfx(v1, 0.75, gain=1.35)

    # Voice 2: Shot 2 at 4.4s
    v2 = load_audio_file('shot2.mp3')
    add_sfx(v2, 4.4, gain=1.35)

    # Voice 3: Shot 3 at 9.1s
    v3 = load_audio_file('shot3.mp3')
    add_sfx(v3, 9.1, gain=1.35)

    # Voice 4: Shot 4 at 14.2s
    v4 = load_audio_file('shot4.mp3')
    add_sfx(v4, 14.2, gain=1.35)

    # Normalize audio cleanly without clipping
    max_val = np.max(np.abs(master))
    if max_val > 0.95:
        master = master * (0.95 / max_val)

    os.makedirs('assets', exist_ok=True)
    out_wav_path = os.path.join('assets', 'master_audio.wav')
    int_samples = (master * 32767).astype(np.int16)

    with wave.open(out_wav_path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(int_samples.tobytes())

    print(f"Master audio generated: {out_wav_path} (Duration: {total_sec}s)")

if __name__ == '__main__':
    main()
