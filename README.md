# Geometry Shader Explosion Simulator in OpenGL

A PyQt6 and OpenGL desktop app for loading 3D models and previewing customizable explosion animations.

## Requirements

- Python 3.14 or newer
- A graphics card and driver that support OpenGL 4.0

## Setup and run

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then run these commands from the project directory:

```sh
uv sync
uv run view-model objects/cube.obj
```

To load a different model, replace `objects/cube.obj` with its path. You can also choose **Select Model...** in the viewer.

## Controls

- **Explode** starts the animation; **Play/Pause** toggles playback; **Reset** returns it to the start.
- Move the mouse to rotate the camera.
- Use **W/A/S/D** or the arrow keys to move horizontally; **Q/E** move down/up.
- Press **T** to toggle UI mode and release the mouse for panel interaction.
- Use the sliders to adjust the explosion and animation parameters.

Sample models are in the `objects` directory.