from enum import Enum, auto
import glm
from typing import Sequence, Union


class Direction(Enum):
    FORWARD = auto()
    BACKWARD = auto()
    LEFT = auto()
    RIGHT = auto()
    UP = auto()
    DOWN = auto()


class Camera:
    def __init__(self, position: Union[Sequence[float], glm.vec3]) -> None:
        self.position = glm.vec3(position)
        self.front = glm.vec3(0.0, 0.0, -1.0)
        self.up = glm.vec3(0.0, 1.0, 0.0)
        self.right = glm.vec3(1.0, 0.0, 0.0)
        self.world_up = glm.vec3(0.0, 1.0, 0.0)
        self.yaw = -90.0
        self.pitch = 0.0
        self.speed = 5.0
        self.sensitivity = 0.1
        self.update_camera_vectors()

    def get_view_matrix(self) -> glm.mat4:
        return glm.lookAt(self.position, self.position + self.front, self.up)

    def process_keyboard(self, direction: Direction, delta_time: float) -> None:
        velocity = self.speed * delta_time
        match direction:
            case Direction.FORWARD:
                self.position += self.front * velocity
            case Direction.BACKWARD:
                self.position -= self.front * velocity
            case Direction.LEFT:
                self.position -= self.right * velocity
            case Direction.RIGHT:
                self.position += self.right * velocity
            case Direction.UP:
                self.position += self.up * velocity
            case Direction.DOWN:
                self.position -= self.up * velocity

    def process_mouse_movement(
        self, xoffset: float, yoffset: float, constrain_pitch: bool = True
    ) -> None:
        xoffset *= self.sensitivity
        yoffset *= self.sensitivity

        self.yaw += xoffset
        self.pitch += yoffset

        if constrain_pitch:
            if self.pitch > 89.0:
                self.pitch = 89.0
            if self.pitch < -89.0:
                self.pitch = -89.0

        self.update_camera_vectors()

    def update_camera_vectors(self) -> None:
        front = glm.vec3()
        front.x = glm.cos(glm.radians(self.yaw)) * glm.cos(glm.radians(self.pitch))
        front.y = glm.sin(glm.radians(self.pitch))
        front.z = glm.sin(glm.radians(self.yaw)) * glm.cos(glm.radians(self.pitch))
        self.front = glm.normalize(front)
        self.right = glm.normalize(glm.cross(self.front, self.world_up))
        self.up = glm.normalize(glm.cross(self.right, self.front))
