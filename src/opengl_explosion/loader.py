import pyassimp
from OpenGL.GL import *  # type: ignore
import numpy as np
import numpy.typing as npt


class Mesh:
    def __init__(
        self,
        vertices: npt.NDArray[np.float32],
        normals: npt.NDArray[np.float32],
        indices: npt.NDArray[np.uint32],
    ) -> None:
        self.vertices = vertices
        self.normals = normals
        self.indices = indices
        self.vao = glGenVertexArrays(1)
        self.vbo_v = glGenBuffers(1)
        self.vbo_n = glGenBuffers(1)
        self.ebo = glGenBuffers(1)

        glBindVertexArray(self.vao)

        # vertices
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_v)
        glBufferData(
            GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW
        )
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(0)

        # normals
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_n)
        glBufferData(GL_ARRAY_BUFFER, self.normals.nbytes, self.normals, GL_STATIC_DRAW)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(1)

        # indices
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(
            GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_STATIC_DRAW
        )

        glBindVertexArray(0)
        self.index_count = len(self.indices)

    def draw(self) -> None:
        glBindVertexArray(self.vao)
        glDrawElements(GL_TRIANGLES, self.index_count, GL_UNSIGNED_INT, None)
        glBindVertexArray(0)


class Model:
    def __init__(self, path: str) -> None:
        self.meshes: list[Mesh] = []
        self.load_model(path)

    def load_model(self, path: str) -> None:
        print(f"Loading model from {path}...")
        try:
            with pyassimp.load(path) as scene:
                all_vertices = []
                for mesh in scene.meshes:
                    verts = np.array(mesh.vertices, dtype=np.float32)
                    all_vertices.append(verts)

                all_vertices = np.vstack(all_vertices)

                min_v = np.min(all_vertices, axis=0)
                max_v = np.max(all_vertices, axis=0)
                center = (min_v + max_v) * 0.5

                for mesh in scene.meshes:
                    vertices = np.array(mesh.vertices, dtype=np.float32)
                    vertices -= center

                    if len(mesh.normals) > 0:
                        normals = np.array(mesh.normals, dtype=np.float32)
                    else:
                        # dummy normals if not present
                        normals = np.zeros_like(vertices, dtype=np.float32)
                        normals[:, 1] = 1.0

                    indices = np.array(mesh.faces, dtype=np.uint32).flatten()
                    self.meshes.append(Mesh(vertices, normals, indices))
            print(f"Loaded {len(self.meshes)} meshes.")
        except Exception as e:
            print(f"Failed to load model {path}: {e}")

    def draw(self) -> None:
        for mesh in self.meshes:
            mesh.draw()
