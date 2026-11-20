# DATA_MANIFEST — every file, its provenance, true parameters and expected analysis results
All Lab 2 files: `data_source = idealized_simulation_not_OSCAR` (TA simulator, docs/reference/TA_lab2_simulator.html). 1 kHz sampling, SI units. Columns: time_s, phase_rad, force_N, motor_displacement_m, motor_velocity_m_s, displacement_m, velocity_m_s, acceleration_m_s2, mass_kg, k1_or_km_N_m, k2_or_k0_N_m, c_or_c0_N_s_m, cm_N_s_m, motor_amplitude_m, frequency_Hz, step_force_N, step_onset_s, dry_friction_enabled (0 in all files) and others.

## Lab 1 — REAL OSCAR V2
`lab1/lab1_peaks_transcribed.csv` — peak pairs transcribed from the Lab 1 report. No time series. Raw sensor-zero readings + rest level. See INPUTS.md §2 and §6.

## Lab 2 Part A — direct-force step (Case A), m = 1 kg, k1 = k2 = 40 N/m, F0 = 4 N at t_s = 1 s, x0 = v0 = 0, friction off
| file | run | c (N·s/m) | rows / duration | true ωn | true ζ | x_static | expected results from the data (verified) |
|---|---|---|---|---|---|---|---|
| partA_step_trial1_c4.csv | 36 | 4 | 11038 / 11.04 s | 8.944 rad/s | 0.2236 | 50.000 mm | x_peak 74.320 mm at t = 1.360 s; PO 48.64 % (formula 48.640 %); Td 0.721 s; ωd 8.7145; recovered ζ1 0.2236, ωn1 8.941; 10–90 % rise 0.137 s; 2 % settling ≈ 1.89 s after onset; a(1.001 s) = 4.0 m/s² = F0/m |
| partA_step_trial2_c20.csv | 37 | 20 | 9020 / 9.02 s | 8.944 rad/s | 1.118 (overdamped) | 50.000 mm | no overshoot, monotonic; 10–90 % rise 0.442 s; 2 % settling ≈ 0.79 s after onset; PO / ζ₁ / ωd₁ NOT applicable |
Note: trial 2 is not a repeat of trial 1 (different c).

## Lab 2 Part B — Case C motor/cable coupling: m = 1, k0 = 40, km = 40 N/m, c0 = 0.8, cm = 1.2 N·s/m, A = 10 mm (yₘ = A sin ωt), friction off
Engaged: k1 = k0 + km = 80 N/m, c1 = c0 + cm = 2.0, ωn1 = 8.944 rad/s (1.4235 Hz), ζ1 = 0.1118. Disengaged-only (k0, c0): ωn0 = 6.325 rad/s, ζ0 = 0.0632.
Raw waveforms (coarse): partB_caseC_{1..6}Hz_raw.csv (runs 11, 19, 20, 22, 23, 24; no hand dragging, no contacts, one setup segment). Max |x|: 1 Hz 11.48 mm, 2 Hz 8.27, 3 Hz 3.76, 4 Hz 2.65, 5 Hz 1.96, 6 Hz 1.52.
Summary table `partB_caseC_sweep_summary.csv` (9 points: 1, 1.25, 1.5, 1.75, 2, 3, 4, 5, 6 Hz), gain in mm/mm relative to yₘ, phase relative to yₘ (negative = lag). Windows: last 5 cycles after ≥ 5 s discard, sine-fit residual < 1 %.
Verified against X/Yₘ = √(km² + (cm ω)²) / √((k1 − mω²)² + (c1 ω)²), φ = atan2(cm ω, km) − atan2(c1 ω, k1 − mω²):
| f (Hz) | gain measured | gain theory | phase measured (°) | phase theory (°) |
|---|---|---|---|---|
| 1 | 0.9607 | 0.9594 | −6.56 | −6.55 |
| 1.25 | 1.7034 | 1.7032 | −27.37 | −27.36 |
| 1.5 | 2.0012 | 1.9972 | −99.33 | −99.30 |
| 1.75 | 0.9077 | 0.9070 | −133.46 | −133.48 |
| 2 | 0.5222 | 0.5222 | −141.47 | −141.47 |
| 3 | 0.1654 | 0.1654 | −142.71 | −142.72 |
| 4 | 0.0905 | 0.0904 | −137.78 | −137.78 |
| 5 | 0.0605 | 0.0605 | −132.73 | −132.73 |
| 6 | 0.0450 | 0.0450 | −128.27 | −128.27 |
Interior peak: ≈ 1.5 Hz (gain ≈ 2.0, repeatable across 1.25–1.75 Hz); measurement extends to 6 Hz beyond the peak. Phase passes −90° between 1.25 and 1.5 Hz (at −90° ωn ≈ ω and ζ = 1/(2M) only for the idealised second-order form — Case C has a numerator zero, so the pointwise estimator must carry a validity note).
Missing: raw waveforms for 1.25 / 1.5 / 1.75 Hz; any PWM data; any real OSCAR Lab 2 measurement.
