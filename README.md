# PhIDO

PhIDO (Photonics Intelligent Design and Optimization) is a Streamlit application for photonic circuit design. It uses LLMs to interpret design intent, select photonic components, generate a circuit DSL, produce layouts with GDSFactory, and simulate circuits with SAX-based models.

This working copy has been adjusted to run more cleanly on Windows with `uv`, modern OpenAI SDK usage, and a more executable directional coupler example.

## What This Repo Does

PhIDO supports two usage modes:

- Automatic workflow: prompt to layout in one guided flow.
- Step-by-step workflow: entity extraction, component selection, DSL generation, layout, simulation, and DRC as separate stages.

At a high level, the pipeline is:

1. Parse a natural-language photonic design request.
2. Match requested devices against the local photonic component library.
3. Build a circuit DSL describing instances, ports, edges, and placements.
4. Convert the DSL into a GDSFactory netlist.
5. Generate a layout and simulate S-parameters with SAX.
6. Optionally run DRC with KLayout.

## Current Status Of This Working Copy

The following improvements were made in this copy:

- `uv` environment setup was fixed for Windows, including `pygraphviz`.
- OpenAI model handling was modernized:
  - deprecated `o1-preview` is remapped to `o1`
  - default reasoning model is configurable and set to `o3`
  - structured output model is configurable
- missing runtime dependencies used by imports were added to `pyproject.toml`
- Windows Graphviz DLL loading was made more reliable
- the directional coupler component was made more executable:
  - `gap` is now an actual cell parameter
  - its default simulation backend now uses the analytic model so geometry changes affect simulation

## Important Files

- `PhotonicsAI/Photon/webapp.py`
  - Main Streamlit application and workflow orchestration.
- `PhotonicsAI/Photon/llm_api.py`
  - LLM provider integrations and structured output parsing.
- `PhotonicsAI/Photon/utils.py`
  - DOT parsing, placements, plotting, and simulation helpers.
- `PhotonicsAI/Photon/DemoPDK.py`
  - Loads the local component library into a GDSFactory PDK and creates GDS/SAX circuits.
- `PhotonicsAI/KnowledgeBase/DesignLibrary/`
  - Local photonic component library and device models.
- `PhotonicsAI/Photon/drc/`
  - KLayout DRC integration.
- `GETTING_STARTED.md`
  - Longer workflow walkthrough and troubleshooting notes.

## Agent Handoff

If another agent is going to continue work here, these are the most important facts:

- The repo root is the Python project root.
- The environment is expected to be managed with `uv`.
- Recommended Python version is `3.11` to `3.13`.
- `3.14` is not usable here because the locked `torch` wheels do not support it.
- The app can start without API keys, but any LLM-backed workflow step needs credentials.
- Current git remote only points at the upstream repo:
  - `https://github.com/JPPhotonics/PhIDO-Release.git`
- A personal GitHub repo remote is not configured in this workspace yet.
- Directional coupler example outputs already exist under `build/`.

## Environment

### Prerequisites

Linux:

```bash
sudo apt-get update
sudo apt-get install graphviz libgraphviz-dev pkg-config klayout
sudo apt-get install -y build-essential python3-dev swig
```

Windows:

- Install Graphviz
- Install Visual Studio 2022 Build Tools with the C++ workload
- Install KLayout if you want DRC

### Python Setup

```bash
uv sync --python 3.12
```

Activate the environment if needed:

PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

## Configuration

Create a `.env` file in the repo root if you want to use LLM-backed steps:

```bash
OPENAI_API_KEY='your-openai-api-key'
ANTHROPIC_API_KEY='your-anthropic-api-key'
GOOGLEGENAI_API_KEY='your-google-api-key'
DEEPSEEK_API_KEY='your-deepseek-api-key'
NVIDIA_API_KEY='your-nvidia-nim-api-key'

OPENAI_CHAT_MODEL='gpt-4o'
OPENAI_REASONING_MODEL='o3'
OPENAI_STRUCTURED_MODEL='gpt-4o'
```

Notes:

- `OPENAI_API_KEY` is still required even if you use other providers, because structured parsing paths use OpenAI.
- The app defaults to `o3` for reasoning tasks in this working copy.

## Run The App

```bash
streamlit run PhotonicsAI/Photon/webapp.py
```

Or:

```bash
make run
```

## Directional Coupler Example

The most basic executable example generated in this working copy is a single directional coupler.

Outputs are in `build/`:

- `directional_coupler_requested.gds`
- `directional_coupler_requested.layout.png`
- `directional_coupler_requested.spectrum.png`
- `directional_coupler_5050_baseline.gds`
- `directional_coupler_5050_baseline.layout.png`
- `directional_coupler_5050_baseline.spectrum.png`
- `directional_coupler_summary.json`

Current result summary:

- Requested case:
  - `length=2.0`
  - `gap=0.2`
  - at `1.55 um`, power split is about `0.067 / 0.933`
- 50:50 baseline case:
  - `length=6.0`
  - `gap=0.2`
  - at `1.55 um`, power split is about `0.5 / 0.5`

This is based on the current analytic coupler model in:

- `PhotonicsAI/KnowledgeBase/DesignLibrary/_directional_coupler.py`

## Simulation Backend

There are two separate ideas in this repo:

1. Live external FDTD integration
2. Local simulation models actually used by the current executable flow

What the current code actually uses for layout-time circuit simulation:

- SAX circuit models
- many components load precomputed `.npz` response data through `model_from_npz(...)`
- some components use simple analytic surrogate models

For the directional coupler in this working copy:

- default simulation path is now the analytic model
- the old FDTD path still exists as a precomputed `.npz` loader

So the short answer is:

- It is not currently running live Lumerical FDTD.
- It is not currently running live Tidy3D FDTD in the executed path either.
- It mostly uses precomputed response data plus analytic surrogates inside SAX.

There is evidence of optional Tidy3D support in dependencies:

- `gplugins[sax,tidy3d]` in `pyproject.toml`
- `tidy3d` in `requirements.txt`

And `GETTING_STARTED.md` notes:

- FDTD integration is available only on the `tidy3d_integration` branch.

## Known Gaps

- Personal GitHub remote is not configured here yet.
- DRC path discovery is still Linux-centric in `PhotonicsAI/Photon/drc/drc.py`.
- The Streamlit UI can launch without keys, but automatic LLM workflows cannot complete without provider credentials.
- Some device models remain approximate or disconnected from geometry-specific EM data.

## Suggested Next Steps

- Add your personal GitHub repo as a new remote and push this branch there.
- If you want full Windows DRC, update `PhotonicsAI/Photon/drc/drc.py` to locate the KLayout executable on Windows.
- If you want true EM-backed coupler sweeps, replace the analytic coupler model with geometry-indexed precomputed data or a live solver workflow.
