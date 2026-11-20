# MSE 281 — OSCAR Digital Twin Web App: Claude Code Master Prompt

> Paste everything below the line into Claude Code, run from the repo root that contains `docs/rubric/` and `assets/`.
> Before pasting: complete `docs/INPUTS.md` (see "Before you start" in the chat message / bottom of this file).

---

## 0. Models and orchestration (follow exactly)

- **Main agent: Claude Opus 5.5** (`claude-opus-5-5`). Owns architecture, all numerical/physics code, 3D integration, integration testing, and final review of everything the subagent produces.
- **Exactly ONE subagent: Claude Sonnet 5.5** (`claude-sonnet-5-5`). Create it once as `.claude/agents/matlab-verifier.md` (frontmatter `name: matlab-verifier`, `model: sonnet`, tools: Read, Write, Edit, Bash). Do NOT spawn any other subagent. Re-use the same one via follow-up messages.
- **Sonnet's job (independence is the point):** it receives ONLY `docs/EQUATIONS.md` (the spec you write in Phase 1) — NOT the TypeScript source — and writes:
  1. `matlab/` reference implementation using `ode45` for every subsystem (readable, commented, one function per equation),
  2. `matlab/verify_*.m` scripts that dump reference trajectories/FRFs to `verification/*.csv`,
  3. `docs/MATLAB_README.md` (how to run).
  Opus then compares the app's output to the MATLAB output (tolerances in §9). This gives the rubric's required *independent verification* of one time-domain simulation and one FRF.
- Opus must **read and critically review** every Sonnet artifact before accepting it. Log accepted/rejected items in `docs/DESIGN_LOG.md`.

## 1. Mission

Build a web-based digital twin of the OSCAR (Oscillating Smart Cart And Rail) teaching rig for SFU **MSE 281**. It must satisfy **every** item in the project rubric PDF in `docs/rubric/` (project + syllabus). The student must be able to explain every equation, every design decision, and every file — so code must be clean, commented, and every decision recorded.

**Step 1 (before any code):** extract text from both PDFs in `docs/rubric/`, and write `docs/REQUIREMENTS_TRACE.md`: a table with one row per rubric requirement (success criteria, Checkpoints 1–4, §5–§9, the 5 deliverables, the 100-mark breakdown, "not required" list, the Appendix A caveat, syllabus §11 AI rules). Columns: `ID | Rubric text (short quote ≤15 words or paraphrase) | Page/Section | Implemented in (file/function) | Test | Status`. **Where my checklist below disagrees with the PDF, the PDF wins — list every discrepancy at the top of the trace file.** Keep this file current; it is the main evidence for the professor. Nothing may be "TBD" at completion.

## 2. Deliverable-risk gate (resolve first)

The syllabus calls the project a "MATLAB/Simulink digital twin" and allows instructor-approved alternatives with comparable objectives. Therefore:
- Ship the **web app as the primary interface** AND the **MATLAB reference code** (Sonnet, §0) so the MATLAB deliverable is also met.
- Create `docs/APPROVAL.md` template for the student to paste instructor/TA approval of a web implementation. Do not mark "Interface" complete in the trace until the student confirms approval exists.

## 3. Tech stack (unless `docs/INPUTS.md` overrides)

Vite + React + TypeScript (strict), three.js via `@react-three/fiber` + `@react-three/drei`, a plain canvas/SVG or uPlot/Plotly for plots, Vitest for tests, no backend (static site; deployable to GitHub Pages/Netlify/Vercel). Persist nothing remotely. **All physics lives in `src/physics/` as pure TypeScript with zero UI imports and zero ODE/numerics libraries.**

## 4. Physics and numerics spec (write verbatim into `docs/EQUATIONS.md`, with state definitions, units, and derivations the student can read aloud)

**4.1 Solver (required):** implement your own adaptive Dormand–Prince RK45 (`ode45` equivalent: rtol/atol/maxStep/initialStep options, dense/fixed output sampling, event/termination safety) in `src/physics/solver.ts`, plus a fixed-step RK4 for comparison. **Forbidden:** any library step/impulse/ODE routine, `scipy`, `numeric.js`, `odex`, etc. Unit-test the solver against closed-form solutions (§9).

**4.2 Free mass–spring–damper (Lab 1 model):** `m x'' + c0 x' + k0 x = 0`; `ωn0 = √(k0/m)`, `ζ0 = c0/(2√(m k0))`; states `x1 = x`, `x2 = x'`. Show underdamped, critically damped (ζ=1) and overdamped demos with presets. Handle ζ=1 and ζ→0 without division issues.

**4.3 Engaged compliant-coupling model (prescribed motor-side displacement `ym`):** `m x'' + c0 x' + (k0 + kc) x = kc ym`. No cable damping in the required model. Inputs: free (ym=0, initial conditions), step in ym, sinusoid in ym (amplitude, frequency, phase), optional user-defined array. Effective `ωn = √((k0+kc)/m)`, `ζ = c0/(2√(m(k0+kc)))`.

**4.4 Frequency response:** `H(jω) = 1/(1 − r² + j2ζr)`, `r = ω/ωn`. Plot magnitude (dB and linear toggle) and phase (deg) on a log-frequency axis plus the **s-plane pole plot** (poles `−ζωn ± jωn√(1−ζ²)`, real poles for ζ≥1). Provide both the analytic FRF and an **empirical FRF from simulated/imported sinusoidal data** (steady-state amplitude and phase extraction via least-squares sine fit or lock-in; discard transients; document the method).

**4.5 Pointwise estimates from a single (ω, M, φ) point, `M=|H|`, `φ=∠H`:** `a = cosφ/M`, `b = −sinφ/M`; `ωn_est = ω/√(1−a)`; `ζ_est = b/(2√(1−a))`. **Validity guard:** if `1−a ≤ 0` return "not valid" with reason. Special case at φ = −90°: `ωn = ω`, `ζ = 1/(2M)`. Warn that low-frequency estimates are noise-sensitive. UI: **click any point on the FRF plot** → show frequency (Hz and rad/s), normalized magnitude, phase, estimated ζ and ωn, and validity note. Do not infer system order from phase alone: show a "likely order" hypothesis **with the evidence used and its limits** (e.g., high-frequency asymptote slope/phase trend, presence/absence of a resonance peak), and always label it a hypothesis.

**4.6 Friction:** ON/OFF toggle plus adjustable magnitude. Required implementation: **equivalent viscous damping** (state how magnitude maps to `c`). Optional extension (only after everything else works, behind a clearly labelled flag): smooth Coulomb friction `Fc·tanh(v/ε)`. **Log decrement:** compute from successive peaks (δ = ln(x_n/x_{n+k})/k, ζ from δ), and **show why it is not amplitude-independent with dry friction** (peaks decay linearly, not exponentially) via a side-by-side viscous vs Coulomb demo. Friction must visibly change *true cart motion*.

**4.7 Virtual accelerometer (sensor model):** `z'' + 2ζa ωa z' + ωa² z = −x''`, output `â = −ωa² z`. States `z, z'`; it is driven by cart acceleration from the main model (obtain `x''` from the main model's state derivative, not by finite-differencing noisy data). Parameters ωa, ζa editable. Changing these must change **only the reported acceleration, not the cart motion** (this is a required demonstration, together with the friction one — build a "Demo: what changes the cart vs what changes the reading" panel with a before/after overlay).

**4.8 RC filter:** `RC vf' + vf = va`, `ωc = 1/(RC)`, `fc = ωc/2π`; input `va` = accelerometer output (scaled to volts with a documented, editable gain). R, C editable with units (kΩ/µF). Show raw vs filtered, plus the filter's own magnitude/phase.

**4.9 Motor module (independent subsystem):** first-order speed model `τ ω' + ω = K u`, angle by numerical integration `θ' = ω` (state `[ω, θ]`). It is NOT a position servo. Inputs: step/PWM-like duty (0–1 or %) — document scaling. Its angle may optionally drive the crank animation; if ym is derived from crank geometry, state the assumption and keep it labelled as such.

**4.10 Lab 2 X/U:** a PWM-to-displacement gain `X/U` (units e.g. mm per % duty, state them). **It is not X/F and not X/Ym.** Do NOT claim quantitative PWM→cart prediction from the prescribed-`ym` model — show this warning in the UI wherever X/U appears.

**4.11 "Not reliably identifiable":** the app and any export must be able to output `not reliably identifiable` (with reason) instead of a number — e.g., no resonance peak, too few cycles, SNR too low, 1−a ≤ 0, non-oscillatory (overdamped) data. A missing resonance peak is a legitimate result.

**4.12 Time-domain parameter identification from Lab 1 free-response data:** estimate ωd (peak/zero-crossing spacing), ωn, ζ, k0 (given m) and c0 via log decrement and a second independent method (e.g., envelope fit or linear regression on peaks); report both and their difference. For Lab 2 step data: rise/settling/overshoot-based ζ, ωn estimates, plus the X/U steady-state gain. Show each result's evidence and limitation.

**4.13 Appendix A caution:** the rubric's Appendix A numbers (ωn=125.7 rad/s, ζ=0.06, m=1 kg, k0=400, c=8, kc=800, ωa=800, ζa=0.02, R=10 kΩ, C=1 µF, fc≈15.9 Hz) are **illustrative only**. They may appear as a clearly labelled "Illustrative preset (Appendix A) — not a measurement" and **must never be presented as OSCAR results or default measured values**.

## 5. Application requirements (rubric §8.4 — every item is mandatory)

Each subsystem must be **independently runnable** (own page/tab, own Run button, no hidden dependency on other tabs). Subsystems: (1) Free MSD, (2) Engaged coupling + inputs, (3) FRF/s-plane/ID, (4) Friction + log decrement, (5) Virtual accelerometer, (6) RC filter, (7) Motor module, (8) Lab data import/compare, (9) §9 parameter-comparison table, (10) Validation.

Panels (map each to a trace row):
1. **Physical OSCAR:** the 3D model (§6) animating from solver state, with **engaged / disengaged selector** (engaged adds the coupling spring `kc` and crank drive; disengaged = free).
2. **Controls:** subsystem picker, parameter editors with units and bounds, friction ON/OFF + magnitude, input selector (free/step/sine/PWM/array), Run (and Reset) button, solver tolerances (advanced).
3. **Digital displays:** live displacement and acceleration readouts with units.
4. **Time signals:** true displacement, true acceleration, virtual accelerometer output, filtered output, with **overlay of lab data**.
5. **Frequency plots:** magnitude, phase, selected-frequency readout, likely-order hypothesis and validity note.
6. **Pole plot:** s-plane.
7. **Import/export:** load own lab CSV; preserve frequency, units, provenance (OSCAR ID, configuration, date, operator, source file, release conditions); export results + provenance as CSV/JSON; export plot PNG. Schema in `docs/DATA_SCHEMA.md`.
8. **§9 parameter-comparison table** — rows: Lab 1 free, Lab 2 step, ideal FRF, Lab 2 FRF, selected digital-twin model; columns: ωn, ζ, evidence, limitations. Auto-filled where data exist, "not reliably identifiable" otherwise; exportable.
9. **Validation page:** use one lab data set to adjust the model and a **different** one to evaluate; show residuals/RMSE/NRMSE and the explanation fields for **at least 2 model–experiment discrepancies** (editable text, prefilled with prompts, not invented conclusions).
10. **Teaching mode:** short "what governs this?" explanation per subsystem (the governing ODE, the states, the assumptions), because the demonstration includes explaining each ODE and its states.

Explicitly **not required** (do not build, do not claim): physical encoder, cable-stiffness measurement, elaborate CAD, automatic nonlinear fitting, detailed digital sensor electronics, a perfect model-data match. Optional extensions only after everything above passes and is logged.

## 6. Blender model integration (`assets/oscar.glb`, units: root node scaled 0.01 so geometry is cm→m, +Y up)

Facts about the asset (read `blender/oscar_model.py` for details):
- **There is no physics in the Blender file.** It is geometry + materials only. All motion comes from your solver. (The 3D model was authored procedurally in Blender; it contains separated, named parts so the web app can animate them.)
- Named nodes: `frame`, `tall_support`, `bracket_left`, `bracket_right`, `rail_assembly`, `ruler`, `motor`, `motor_crank` (pivot at crank axis), `kc_tab` (right spring anchor), `estop_body`, `estop_collar`, `estop_dome`, `cart` (parent of `cart_body`, `thumbscrew_L/R`, `stack_L/M/R` — each stack holds individually named mass disks `disk_<L|M|R>_<n>`), and empty anchors `anchor_k0_wall`, `anchor_kc_tab`, `hook_cart_left`, `hook_cart_right`, `crank_pin`, `motor_axis`.
- **Springs and the crank link are NOT in the GLB** (they must stretch). Generate them procedurally every frame (helix tube between `anchor_k0_wall` ↔ `hook_cart_left` and `hook_cart_right` ↔ `kc_tab`; coil count conserved, pitch changes) and a thin link rod from `crank_pin` to `kc_tab`.
- Cart displacement `x` (m, from equilibrium) → `cart.position.x` along the rail axis (Blender X). Scale visualization with an explicit **"visual exaggeration" slider** (default 1×) and label it, because real amplitudes are millimetres; never confuse the exaggerated animation with the plotted data.
- Crank angle θ (from the motor module) → rotate `motor_crank` about its pivot (vertical axis); `kc_tab` position follows the documented ym relationship.
- Mass disks: user can add/remove disks (per stack: L≤3, M≤2, R≤3, as built) → recomputes total `m` (editable per-disk mass, default from `docs/INPUTS.md`). E-stop is decorative but must be hoverable and labelled. Hover/click any part → tooltip with part name, role in the model, and the parameter it affects.
- View switcher: **Focus** (3D large) / **Split** (3D + plots) / **Data** (plots large, 3D minimized) plus camera presets (hero, cart close-up, right, motor) matching `assets/renders/*.webp`; use the WebP renders as the loading placeholder/fallback when WebGL is unavailable.
- Performance: target 60 fps on a mid laptop; instance repeated meshes, cap pixel ratio at 2, pause rendering when tab hidden. Provide a graceful no-WebGL fallback (static render + all plots still work).
- Do not re-model the apparatus. If a part is wrong/missing, record it in `docs/KNOWN_GAPS.md` and tell the student; the student can re-run `blender/oscar_model.py --export 1 --out assets/oscar.glb` (needs `pip install bpy`).

## 7. Design / UX

Compact, not overloaded, "3D medium-poly with light cartoon feel" per the student's earlier UI boards (`docs/ui-reference/` if provided; style letter in `docs/INPUTS.md`). Keyboard accessible, color-blind-safe plot palette, units on every number, consistent decimals, responsive down to a 1280×720 laptop. Every plot: axis labels with units, legend, hover readout, PNG export. A persistent banner on every screen reminding what is simulated vs measured vs illustrative.

## 8. Edge cases (each needs a unit/UI test or a documented handling)

Units: rad/s vs Hz, mm vs m, kΩ/µF, % vs fraction duty — all conversions in one module with tests. Data: empty file, header-only, non-numeric cells, NaN/Inf, duplicate or non-monotonic timestamps, non-uniform sampling (resample/interpolate with disclosure), very short records, huge files (≥1e6 rows: decimate for plotting, keep full for math), mixed delimiters/decimal commas, BOM, missing units (ask, never guess), clock offsets, DC offset/drift (detrend with disclosure), clipping/saturation, noise (smoothing must be optional and logged). Identification: <2 peaks, overdamped (no peaks), ζ≥1 branches, phase wrapping at ±180°, 1−a ≤ 0, φ≈0 or −180°, ω ≪ ωn, resonance absent, aliasing when f > fs/2, transients not decayed, amplitude-dependent friction. Numerics: stiff parameter ranges (ωa=800 vs ωn=125 → watch step count), zero/negative m, k, c (reject), ζ=0 (undamped, bounded growth in step size), absurd tolerances, max-step/step-count guard with user message, long runs (progressive rendering, abortable Run), determinism (same inputs → same outputs). UI: simultaneous Run clicks, switching subsystem mid-run, NaN displays, window resize, no-WebGL, reduced-motion preference. Provenance: exports must round-trip (export → import → identical numbers).

## 9. Testing and verification (all automated with Vitest + the MATLAB comparison)

- Solver vs analytic: underdamped/critical/overdamped free responses (error < 1e-6 relative at rtol 1e-9), step response, steady-state sinusoid amplitude/phase vs `H(jω)`.
- FRF pointwise estimator: round-trip (choose ωn, ζ → compute H at ω → estimator recovers ωn, ζ within 1e-9), incl. φ=−90° special case and guard failures.
- Log decrement recovers ζ for viscous; demonstrably fails/varies for Coulomb.
- Accelerometer and RC: analytic step/steady-state checks; RC corner −3 dB at fc.
- Friction demo: cart trace changes; accelerometer-param demo: cart trace identical (bitwise) while reading changes.
- **Independent verification:** `verification/` holds MATLAB-generated CSVs (Sonnet). A test asserts app output vs MATLAB: time-domain max error < 1e-4 relative at matched tolerances; FRF magnitude/phase error < 1e-6. Document exact tolerances and results in `docs/VERIFICATION.md` with plots.
- E2E smoke test (Playwright if allowed): load app, run each subsystem, import sample CSV, click an FRF point, export table.
- Provide `docs/sample-data/` with **synthetic, clearly labelled** CSVs for testing only (never presented as OSCAR measurements).

## 10. Report-support artifacts (the student writes the report from these)

Maintain throughout: `docs/DESIGN_LOG.md` (dated entries: decision, alternatives considered, why, rubric row it serves, who made it — Opus/Sonnet/student), `docs/EQUATIONS.md`, `docs/REQUIREMENTS_TRACE.md`, `docs/VERIFICATION.md`, `docs/KNOWN_GAPS.md`, `docs/AI_USE_DISCLOSURE.md` (syllabus §11 requires AI use be stated in lab/project reports: list tools, models — Opus 5.5 main/Sonnet 5.5 subagent — what each generated, what the student reviewed/changed; leave a "student modifications" section for them to fill), `docs/DEMO_SCRIPT.md` (run each subsystem; explain one FRF point; answer governing-equation questions), `docs/QA_CHEATSHEET.md` (likely professor questions with short, correct answers, including: why log decrement fails with dry friction, why X/U ≠ X/F ≠ X/Ym, why order can't be inferred from phase alone, what 1−a ≤ 0 means, why Appendix A values aren't results), and `docs/REPORT_OUTLINE.md` mapping report sections to the 4 checkpoints and the 100-mark rubric (modelling & numerics 20; lab data & time-domain ID 20; FRF/order/ID 25; friction/accelerometer/RC 15; interface 10; validation/report/demo 10).

**Academic-integrity guardrail:** the syllabus forbids using AI to complete the project *on the student's behalf* and requires disclosure. Therefore: write code comments and `docs/` explanations so the student can learn and defend them; add an `docs/STUDENT_UNDERSTANDING_CHECKLIST.md` of 20+ questions the student must be able to answer without the AI. Do not fabricate lab data or measurements anywhere.

## 11. Workflow phases (stop and summarise at the end of each; wait for my "continue")

0. Read PDFs → `REQUIREMENTS_TRACE.md` skeleton + discrepancy list + `docs/INPUTS.md` gap check (stop and ask me for anything missing).
1. Write `EQUATIONS.md`; create the Sonnet subagent; hand it the spec; meanwhile Opus builds `src/physics/` + tests.
2. Subsystem pages + UI shell (no 3D yet) + import/export + §9 table.
3. 3D integration (GLB, procedural springs, view switcher, hover).
4. Verification against MATLAB; edge-case pass; accessibility/performance.
5. Docs pack + demo script + final trace audit (every row "Done" with evidence) + a final adversarial self-review listing anything weak.

## 12. Definition of done

Every trace row is Done with a file and a test; all tests pass; MATLAB comparison passes; app runs from `npm install && npm run dev` and builds statically; no ready-made ODE/step/impulse routines anywhere (`grep` audit recorded); no Appendix A value is presented as a result; `KNOWN_GAPS.md` is honest; docs pack complete.
