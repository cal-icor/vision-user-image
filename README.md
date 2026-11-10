# vision-user-image

A single-user server image for 2D/3D computer vision coursework on Cal-ICOR and
CloudBank Jupyterhubs.

See this repository's
[CONTRIBUTING.md](https://github.com/cal-icor/vision-user-image/blob/main/CONTRIBUTING.md)
for instructions.

## What's in it

This is `base-user-image` with the R/RStudio stack and the C++ kernel removed,
and the vision stack added.

| Library | Use |
| --- | --- |
| `open3d` (CPU build) | point clouds, voxel grids, ICP/RANSAC registration, surface reconstruction |
| `trimesh` | triangle meshes, ray casting, watertight checks, format conversion |
| `pycolmap` | structure from motion, camera models, bundle adjustment |
| `opencv` 4.x | features, matching, camera calibration, epipolar geometry, stereo |
| `scikit-image`, `imageio` | image processing and I/O |
| `transformers`, `pytorch` | pretrained models, e.g. monocular depth |

### This is a CPU image, on purpose

Nothing in the stack above needs a GPU for the work these courses do:

- `trimesh` is pure Python over numpy. It has no GPU path at all.
- `open3d`'s legacy `o3d.geometry` API — the one every tutorial uses — is
  CPU-only. CUDA is opt-in through the tensor API (`o3d.core.Device("CUDA:0")`).
  We install `open3d-cpu`, which has the same import name and the same API as
  `open3d` but is 105MB instead of 400MB, because it omits the bundled CUDA
  libraries nothing here would call.
- `pycolmap`'s PyPI wheel is a CPU build — the package reports `has_cuda = False`.
  COLMAP's dense MVS (patch-match stereo) requires CUDA and is **not available**
  here. Sparse reconstruction — feature extraction, matching, incremental SfM —
  runs on CPU. conda-forge does publish CUDA builds of `pycolmap`, but they skip
  Python 3.13 (311/312/314 only) and need `libsqlite >= 3.54`, so they can't go
  in this image as pinned.

Moving to a GPU image would mean T4 nodes, two students per node, and a much
longer cold start, in exchange for nothing the current stack can use. If a
course moves into learned 3D (NeRF, Gaussian splatting, PointNet, deep feature
matching) that calculation changes and it should be a separate GPU image.

### AVX512

`libOpen3D`, `libopencv_core` and `pycolmap`'s `_core` all contain AVX512
instructions, but all three carry runtime CPU dispatch (multiple ISA variants
plus `cpuid` checks) — the same shape as `libtorch_cpu.so`, which the base image
already ships and which runs on the hubs today. This is not the pattern that
broke the GPU image, where ggml was compiled with `GGML_NATIVE=ON` and had no
runtime check at all.

### Known rough edge: the Open3D "build recommended" popup

`open3d` declares a hard dependency on `dash`, and `dash` ships a JupyterLab
extension as source rather than as a prebuilt labextension. JupyterLab notices
this at startup and offers to build it. The popup is cosmetic — kernels,
notebooks and plotting all work — and clicking "Build" fails rather than doing
anything, because Node isn't in the image. There is no upstream fix: the Open3D
issue is closed as "not planned".

## Building the image locally

Use [repo2docker](https://repo2docker.readthedocs.io/en/latest/) to build and
test the image on your own device before you push and create a PR. CI pins
`jupyter-repo2docker==2025.12.0`; use the same version locally so apt package
names resolve against the same Ubuntu release.

``` bash
repo2docker . # <--- the path to the repo
```

If you are using an ARM CPU (Apple M* silicon) you must pass `linux/amd64`.
`open3d-cpu` publishes no `aarch64` wheel, so a native ARM build will fail at
the pip step:

``` bash
jupyter-repo2docker --user-id=1000 --user-name=jovyan \
  --Repo2Docker.platform=linux/amd64 \
  --target-repo-dir=/home/jovyan/.cache \
  -e PLAYWRIGHT_BROWSERS_PATH=/srv/conda \
  . # <--- the path to the repo
```

Add `--no-run` (before the final `.`) to build without launching the server.

## Running the image tests locally

``` bash
jupyter-repo2docker --no-run --image-name vision-user-image:local \
  --Repo2Docker.platform=linux/amd64 .

docker run --rm -v "$PWD":/work -w /work vision-user-image:local \
  bash -c "pip install -r image-tests/requirements.txt && \
           pytest -c image-tests/pytest.ini image-tests/ -v"
```
