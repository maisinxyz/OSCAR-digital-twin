# INPUTS.md — filled from Vince's Lab 1 report, Lab 2 manual, TA simulator and exported CSVs

(Claude Code: this file and `data/DATA_MANIFEST.md` SUPERSEDE the defaults in the master prompt wherever they differ. Items marked **[ASK]** are unknown — ask the student in Phase 0; never invent them.)

## 1. Team / course

- Student: Vince Ong, SFU Mechatronic Systems Engineering, MSE 281 (Modelling of Mechatronic Systems), Instructor Farid Golnaraghi, TA Ali Al-Baidhani.
- Lab section/group (from Lab 1 cover): "Lab 2, group 7" (4 students). Project group members: **[Vince O, Sam P, Andrea O, William W]**
- Project due: Week 12 (about Nov 27, 2026) — **[ASK] confirm on Canvas**
- Instructor/TA approval of a web app instead of MATLAB/Simulink: **[Yes] pending** (student will paste it into docs/APPROVAL.md)
- Experiment dates: Lab 1 = Oct 1, 2026 (report submitted Oct 8).

## 2. Physical OSCAR (real hardware, from Lab 1)

- Apparatus: OSCAR V2, ESP32 + MATLAB/Simulink logging, position sensor (displacement in mm).
- **OSCAR ID / unit number: [sam as group number]** (not stated in the Lab 1 report)
- Spring sets used: "small springs" and "medium springs" (part numbers/stiffness not recorded). Dampers: none installed.
- Moving mass: "load attached to the cart" = 600 / 800 / 1200 g. **Whether the cart's own mass is included is [no]**. Per-disk mass and which disks make each load: **[per is iirc 250g]**
- **k0 was never measured.** Indicative estimate (derived, student must be able to explain it): fitting 1/ωn² = (m_load + m_extra)/k over the three small-spring runs gives k ≈ 420 N/m and m_extra ≈ 0.175 kg (cart + effective spring mass); medium springs then ≈ 950 N/m. Label these "estimated from Lab 1 frequencies, 3-point fit", never "measured".
- Safe PWM limit, PWM amplitudes, Part 0 calibration table: **no real Lab 2 data exists** (see §3). PWM→displacement: not available.

### Lab 1 results as reported (real OSCAR; peak readings only)

| Config                              | ωd (rad/s) | ωn reported (rad/s) | ζ reported                        | ζ if offset removed (indicative)     |
| ----------------------------------- | ---------- | ------------------- | --------------------------------- | ------------------------------------ |
| 600 g, small                        | 23.27      | 23.37               | 0.092 (not stated in report body) | 0.127                                |
| 800 g, small                        | 20.60      | 20.64               | 0.0645                            | 0.100                                |
| 1200 g, small                       | 17.45      | 17.49               | 0.0643                            | 0.103                                |
| 1200 g, medium (B2)                 | 26.18      | 26.26               | 0.0804                            | 0.173                                |
| 1200 g, medium (D1, 23.9 mm peak)   | 26.18      | 26.25               | 0.0713                            | 0.128                                |
| 1200 g, medium (D2, larger release) | 26.18      | 26.18 (reported ωd) | 0.0508 as reported                | **conflicting source data — see §6** |

- Periods (ωd) are trustworthy: they do not depend on the sensor offset. **Reported ζ values were computed from raw sensor peaks, not peaks measured from the rest position (the report says so itself), so they are biased low.** The twin must show both numbers and mark ζ0 as "equivalent viscous value, offset not removed".
- First peak = exactly 41.08 mm in three runs, probably sensor clipping → treat those first peaks as unreliable.
- Default digital-twin configuration (student may change): **1200 g, medium springs** — it has three repeat releases with consistent ωd = 26.18 rad/s and unclipped peaks. All other configurations are selectable presets. Use k0 = m·ωn², c0 = 2mζ0ωn (manual formulas) with m = total moving mass the student confirms.
- **Raw Lab 1 time series: [dont have]** — if the MATLAB/Simulink logs or scope exports still exist, add them to `data/lab1/`; the project rubric needs time-domain data and right now only peaks exist.

## 3. Lab 2 data = TA IDEALIZED SIMULATION, NOT OSCAR HARDWARE

Source: `docs/reference/TA_lab2_simulator.html` ("TA reference · idealized theoretical simulation… not actual OSCAR data"). Every CSV carries `data_source = idealized_simulation_not_OSCAR`. Sample rate 1000 Hz, units SI (m, m/s, m/s², N). Full file list, true parameters and expected analysis results: `data/DATA_MANIFEST.md`.

- Part A (direct-force step, fixed anchors, F0 = 4 N at t = 1 s): trial 1 c = 4 (ζ = 0.2236, underdamped), trial 2 c = 20 (ζ = 1.118, overdamped). m = 1 kg, k1 = k2 = 40 N/m.
- Part B (Case C, motor/cable coupling): m = 1, k0 = 40, km = 40 N/m, c0 = 0.8, cm = 1.2 N·s/m, A = 10 mm. Raw files at 1–6 Hz; summary table also has 1.25, 1.5, 1.75 Hz fine points (no raw files for those).
- No PWM column exists anywhere, so **X/U cannot be computed from this data**.

## 4. Data rules for the app (mandatory)

1. Importer must keep `data_source` and show a persistent banner "SIMULATED DATA — not OSCAR hardware" on any plot/table using Lab 2 files; real Lab 1 data gets "REAL OSCAR V2 (peak readings)".
2. Simulator data has **known ground truth**. Use it to test identification accuracy ("did the app recover the true ωn, ζ?"), NOT to claim agreement with the real OSCAR.
3. Lab 2 "FRF" row of the §9 table = simulated X/Yₘ in mm/mm (Case C, motor displacement as reference). The "X/U (mm per PWM)" cell stays "not available — no PWM data". Never overlay X/Yₘ and X/U.
4. Part A is a direct-force step (Case A). In the twin's engaged model reproduce it with kc·ym = F0 and cm = 0 (no velocity jump). Trial 2 is overdamped: report "PO / ζ₁ / ωd₁ not applicable — no overshoot", and note it is not a repeat of trial 1 (different c).
5. The simulator's Case C has coupling damping cm = 1.2; the rubric's required engaged model has none. Implement cm as an **optional, clearly labelled "Lab 2 Case C extension"** so the twin can reproduce the sweep exactly (expected ωn1 = 8.944 rad/s = 1.4235 Hz, ζ1 = 0.1118; peak gain ≈ 2.0 at 1.5 Hz). With cm = 0 the phase will not match: record it as model–experiment discrepancy #1 (cable damping omitted). Discrepancy #2: the real OSCAR has dry friction (Lab 1 amplitude-dependent ζ) while the simulator has none unless the friction switch is on; discrepancy #3: parameter sets differ (real k ≈ 420–950 N/m vs simulator 80 N/m).
6. Adjust/evaluate split (editable): Lab 2 — adjust on Part A trial 1, evaluate on Part A trial 2 and the Part B sweep. Lab 1 — adjust on release B2, evaluate on D1/D2 (same configuration, different release).
7. Fine-frequency points (1.25, 1.5, 1.75 Hz) exist only as summary rows; mark them "summary only, no raw waveform" and never recompute them.
8. Peaks-only Lab 1 data: importer needs a "peak-pair" format (x1, x2, t1, t2, optional rest level). Offset-corrected values must be shown beside raw ones.
9. Do not commit student numbers or the Lab 1 PDF (private repo only). Do not fabricate any measurement.

## 5. Tech / delivery

- Stack: Vite + React + TypeScript + three.js (default) — student has not objected. **[ASK] hosting** (GitHub Pages / Netlify / Vercel / local).
- UI style: student reviewed boards A–L; preferred style letter **[ASK]**.
- MATLAB available for Sonnet's reference scripts? **[ASK]** (Octave as fallback; the student's profile shows prior MATLAB use).
- Claude Code access to Opus 5.5 + Sonnet 5.5: **[ASK]**

## 6. Known problems in the Lab 1 report — flag, do not hide, do not silently "fix"

- Peaks measured from sensor zero (not rest level) → ζ biased low (see table).
- Part D trial 2: Appendix 4 uses peaks 50.00 / 36.32 mm (ζ = 0.0508), but the Fig 9 caption lists return peaks 38.58 / 22.95 / 14.336 mm. Using those gives ζ ≈ 0.082 (raw) or ≈ 0.111 (offset removed). Which is correct is for the student to decide from the original scope trace.
- Table 1 lists trial order 600/800/1200 g but Appendix 5 lists 800/1200/600 g; Appendix 2/3 hand calculations are labelled differently from the body (e.g. Appendix 3 "Part C" uses the 1200 g medium-spring data).
- k never measured; each configuration run once.
