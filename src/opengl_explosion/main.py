import sys
import time
from typing import Any, Set

import glm
from OpenGL.GL import *  # type: ignore
from PyQt6.QtCore import QPointF, Qt, QTimer
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtGui import QSurfaceFormat

from opengl_explosion.camera import Camera, Direction
from opengl_explosion.loader import Model
from opengl_explosion.shader import ShaderProgram


class FloatSlider(QWidget):
    def __init__(
        self,
        label_text: str,
        min_val: float,
        max_val: float,
        initial_val: float,
        callback: Any,
    ):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel(label_text)
        self.label.setMinimumWidth(100)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(1000)

        self.min_val = min_val
        self.max_val = max_val
        self.callback = callback

        self.val_label = QLabel()
        self.val_label.setMinimumWidth(50)

        self.set_value(initial_val)
        self.slider.valueChanged.connect(self.on_value_changed)

        layout.addWidget(self.label)
        layout.addWidget(self.slider)
        layout.addWidget(self.val_label)

    def set_value(self, val: float) -> None:
        ratio = (val - self.min_val) / (self.max_val - self.min_val)
        self.slider.setValue(int(ratio * 1000))
        self.val_label.setText(f"{val:.2f}")

    def on_value_changed(self, val: int) -> None:
        ratio = val / 1000.0
        actual_val = self.min_val + ratio * (self.max_val - self.min_val)
        self.val_label.setText(f"{actual_val:.2f}")
        self.callback(actual_val)


class IntSlider(QWidget):
    def __init__(
        self,
        label_text: str,
        min_val: int,
        max_val: int,
        initial_val: int,
        callback: Any,
    ):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel(label_text)
        self.label.setMinimumWidth(100)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(min_val)
        self.slider.setMaximum(max_val)
        self.callback = callback

        self.val_label = QLabel()
        self.val_label.setMinimumWidth(50)

        self.set_value(initial_val)
        self.slider.valueChanged.connect(self.on_value_changed)

        layout.addWidget(self.label)
        layout.addWidget(self.slider)
        layout.addWidget(self.val_label)

    def set_value(self, val: int) -> None:
        self.slider.setValue(val)
        self.val_label.setText(f"{val}")

    def on_value_changed(self, val: int) -> None:
        self.val_label.setText(f"{val}")
        self.callback(val)


class GLWidget(QOpenGLWidget):
    def __init__(self, parent: Any = None):
        super().__init__(parent)
        self.camera = Camera((0.0, 0.0, 5.0))
        self.keys_pressed: Set[int] = set()
        self.last_mouse_pos: QPointF | None = None

        self.ui_mode = False
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.BlankCursor)

        self.model_path = ""
        self.model: Model | None = None
        self.shader_program: ShaderProgram | None = None

        self.gravity = 25.0
        self.intensity = 20
        self.explosion_origin = [0.0, -0.2, 0.0]
        self.explosion_dir = [10.0, 2.0, 0.0]
        self.noise_strength = 0.4
        self.radial_ratio = 0.0
        self.cycle_delay = 3.0
        self.animation_speed = 1.0
        self.fragmentation = 1

        self.last_frame_time = time.time()
        self.elapsed_time = 0.0
        self.delta_time = 0.0

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(16)  # ~60 fps

    def load_model(self, path: str) -> None:
        self.model_path = path
        # if context is already initialized, load model immediately
        if self.context():
            self.makeCurrent()
            self.model = Model(self.model_path)
            self.doneCurrent()

    def initializeGL(self) -> None:
        glEnable(GL_DEPTH_TEST)
        self.shader_program = ShaderProgram.from_files(
            "explosion.vert",
            "explosion.geom",
            "explosion.frag",
        )
        if self.model_path:
            self.model = Model(self.model_path)

    def resizeGL(self, w: int, h: int) -> None:
        glViewport(0, 0, w, h)

    def paintGL(self) -> None:
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # type: ignore

        if not self.shader_program or not self.model:
            return

        w, h = self.width(), self.height()
        aspect = w / h if h > 0 else 1.0
        projection = glm.perspective(glm.radians(45.0), aspect, 0.1, 1000.0)
        view = self.camera.get_view_matrix()
        model_matrix = glm.mat4(1.0)

        self.shader_program.use()
        self.shader_program.set_projection(projection)
        self.shader_program.set_view(view)
        self.shader_program.set_model(model_matrix)

        self.shader_program.set_gravity(self.gravity)
        self.shader_program.set_intensity(self.intensity)
        self.shader_program.set_explosion_origin(tuple(self.explosion_origin))
        self.shader_program.set_explosion_dir(tuple(self.explosion_dir))
        self.shader_program.set_noise_strength(self.noise_strength)
        self.shader_program.set_radial_ratio(self.radial_ratio)
        self.shader_program.set_int("u_fragmentation", self.fragmentation)

        cycle_time = self.elapsed_time % 6.0
        time_with_delay = max(0.0, cycle_time - self.cycle_delay)
        self.shader_program.set_time(time_with_delay)

        self.model.draw()

    def update_frame(self) -> None:
        current_time = time.time()
        self.delta_time = current_time - self.last_frame_time
        self.last_frame_time = current_time
        self.elapsed_time += self.delta_time * self.animation_speed

        self.process_input()
        self.update()  # trigger paintGL

    def process_input(self) -> None:
        if Qt.Key.Key_W in self.keys_pressed or Qt.Key.Key_Up in self.keys_pressed:
            self.camera.process_keyboard(Direction.FORWARD, self.delta_time)
        if Qt.Key.Key_S in self.keys_pressed or Qt.Key.Key_Down in self.keys_pressed:
            self.camera.process_keyboard(Direction.BACKWARD, self.delta_time)
        if Qt.Key.Key_A in self.keys_pressed or Qt.Key.Key_Left in self.keys_pressed:
            self.camera.process_keyboard(Direction.LEFT, self.delta_time)
        if Qt.Key.Key_D in self.keys_pressed or Qt.Key.Key_Right in self.keys_pressed:
            self.camera.process_keyboard(Direction.RIGHT, self.delta_time)
        if Qt.Key.Key_Q in self.keys_pressed:
            self.camera.process_keyboard(Direction.DOWN, self.delta_time)
        if Qt.Key.Key_E in self.keys_pressed:
            self.camera.process_keyboard(Direction.UP, self.delta_time)

    def keyPressEvent(self, event: Any) -> None:  # type: ignore[override]
        if event.key() == Qt.Key.Key_T:
            self.ui_mode = not self.ui_mode
            if self.ui_mode:
                self.setCursor(Qt.CursorShape.ArrowCursor)
                self.setMouseTracking(False)
            else:
                self.setCursor(Qt.CursorShape.BlankCursor)
                self.setMouseTracking(True)
                self.last_mouse_pos = None
        else:
            self.keys_pressed.add(event.key())

    def keyReleaseEvent(self, event: Any) -> None:  # type: ignore[override]
        if event.key() in self.keys_pressed:
            self.keys_pressed.remove(event.key())

    def mouseMoveEvent(self, event: Any) -> None:  # type: ignore[override]
        if self.ui_mode:
            return

        current_pos = event.position()
        center = QPointF(self.rect().center())

        if current_pos == center:
            self.last_mouse_pos = center
            return

        if self.last_mouse_pos is not None:
            xoffset = current_pos.x() - self.last_mouse_pos.x()
            yoffset = self.last_mouse_pos.y() - current_pos.y()  # reversed
            self.camera.process_mouse_movement(xoffset, yoffset)

        from PyQt6.QtGui import QCursor

        QCursor.setPos(self.mapToGlobal(self.rect().center()))
        self.last_mouse_pos = center


class MainWindow(QMainWindow):
    def __init__(self, initial_model_path: str):
        super().__init__()
        self.setWindowTitle("OpenGL Explosion Viewer")
        self.resize(1280, 720)

        self.gl_widget = GLWidget(self)
        self.setCentralWidget(self.gl_widget)
        self.gl_widget.load_model(initial_model_path)

        self._setup_ui(initial_model_path)

    def _setup_ui(self, initial_model_path: str) -> None:
        overlay_layout = QHBoxLayout(self.gl_widget)
        overlay_layout.setContentsMargins(0, 20, 20, 0)
        overlay_layout.setSpacing(0)
        overlay_layout.addStretch()  # push panel to the right

        ui_panel = QWidget()
        ui_panel.setFixedWidth(350)
        ui_panel.setObjectName("UIPanel")
        ui_panel.setStyleSheet("""
            #UIPanel {
                background-color: rgba(20, 20, 20, 200);
                border: 1px solid rgba(255, 255, 255, 30);
                border-radius: 10px;
            }
            QLabel {
                color: white;
            }
        """)
        ui_layout = QVBoxLayout(ui_panel)
        ui_layout.setContentsMargins(20, 20, 20, 20)

        help_label = QLabel(
            "<b>Controls:</b><br>Press 'T' to toggle UI mode<br>Mouse: Rotate Camera<br>W/A/S/D/Q/E: Move Camera"
        )
        ui_layout.addWidget(help_label)

        btn_select = QPushButton("Select Model...")
        btn_select.clicked.connect(self.select_model)
        ui_layout.addWidget(btn_select)

        self.lbl_model = QLabel(f"Current: {initial_model_path or 'None'}")
        self.lbl_model.setWordWrap(True)
        ui_layout.addWidget(self.lbl_model)

        btn_reset_cam = QPushButton("Reset Camera Position")
        btn_reset_cam.clicked.connect(self.reset_camera)
        ui_layout.addWidget(btn_reset_cam)

        ui_layout.addWidget(
            FloatSlider("Gravity", 0.0, 100.0, self.gl_widget.gravity, self.set_gravity)
        )
        ui_layout.addWidget(
            IntSlider("Intensity", 1, 100, self.gl_widget.intensity, self.set_intensity)
        )

        ui_layout.addWidget(QLabel("<b>Explosion Origin</b>"))
        ui_layout.addWidget(
            FloatSlider(
                "Origin X",
                -10.0,
                10.0,
                self.gl_widget.explosion_origin[0],
                lambda v: self.set_origin(0, v),
            )
        )
        ui_layout.addWidget(
            FloatSlider(
                "Origin Y",
                -10.0,
                10.0,
                self.gl_widget.explosion_origin[1],
                lambda v: self.set_origin(1, v),
            )
        )
        ui_layout.addWidget(
            FloatSlider(
                "Origin Z",
                -10.0,
                10.0,
                self.gl_widget.explosion_origin[2],
                lambda v: self.set_origin(2, v),
            )
        )

        ui_layout.addWidget(QLabel("<b>Explosion Direction</b>"))
        ui_layout.addWidget(
            FloatSlider(
                "Dir X",
                -20.0,
                20.0,
                self.gl_widget.explosion_dir[0],
                lambda v: self.set_dir(0, v),
            )
        )
        ui_layout.addWidget(
            FloatSlider(
                "Dir Y",
                -20.0,
                20.0,
                self.gl_widget.explosion_dir[1],
                lambda v: self.set_dir(1, v),
            )
        )
        ui_layout.addWidget(
            FloatSlider(
                "Dir Z",
                -20.0,
                20.0,
                self.gl_widget.explosion_dir[2],
                lambda v: self.set_dir(2, v),
            )
        )

        ui_layout.addWidget(
            FloatSlider(
                "Noise Strength",
                0.0,
                2.0,
                self.gl_widget.noise_strength,
                self.set_noise,
            )
        )
        ui_layout.addWidget(
            FloatSlider(
                "Radial Ratio", 0.0, 1.0, self.gl_widget.radial_ratio, self.set_radial
            )
        )
        ui_layout.addWidget(
            FloatSlider(
                "Cycle Delay", 0.0, 10.0, self.gl_widget.cycle_delay, self.set_delay
            )
        )
        ui_layout.addWidget(
            FloatSlider(
                "Anim Speed", 0.0, 5.0, self.gl_widget.animation_speed, self.set_speed
            )
        )
        ui_layout.addWidget(
            IntSlider(
                "Multiplication", 1, 10, self.gl_widget.fragmentation, self.set_fragmentation
            )
        )

        ui_layout.addStretch()

        overlay_layout.addWidget(
            ui_panel, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight
        )

    def select_model(self):
        filters = "Model Files (*.obj *.fbx *.gltf *.glb *.dae *.stl *.blend *.3ds *.ply);;All Files (*)"
        path, _ = QFileDialog.getOpenFileName(self, "Choose Model", ".", filters)
        if path:
            self.lbl_model.setText(f"Current: {path}")
            self.gl_widget.load_model(path)
            self.gl_widget.setFocus()

    def reset_camera(self):
        self.gl_widget.camera = Camera((0.0, 0.0, 5.0))
        self.gl_widget.setFocus()

    def set_gravity(self, val):
        self.gl_widget.gravity = val

    def set_intensity(self, val):
        self.gl_widget.intensity = val

    def set_origin(self, idx, val):
        self.gl_widget.explosion_origin[idx] = val

    def set_dir(self, idx, val):
        self.gl_widget.explosion_dir[idx] = val

    def set_noise(self, val):
        self.gl_widget.noise_strength = val

    def set_radial(self, val):
        self.gl_widget.radial_ratio = val

    def set_delay(self, val):
        self.gl_widget.cycle_delay = val

    def set_speed(self, val):
        self.gl_widget.animation_speed = val

    def set_fragmentation(self, val):
        self.gl_widget.fragmentation = val


def main() -> None:
    model_path = ""
    if len(sys.argv) >= 2:
        model_path = sys.argv[1]

    fmt = QSurfaceFormat()
    fmt.setVersion(4, 0)
    fmt.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
    QSurfaceFormat.setDefaultFormat(fmt)

    # enable high-DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)

    window = MainWindow(model_path)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
