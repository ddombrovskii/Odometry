from PyQt5.QtCore import pyqtSignal, QFileInfo, QPoint, QSize, Qt
from PyQt5.QtGui import (QColor, QImage, QMatrix4x4, QOpenGLShader,
                         QOpenGLShaderProgram, QOpenGLTexture, QOpenGLVersionProfile)
from PyQt5.QtWidgets import QOpenGLWidget


class TexturizedCubeWidget(QOpenGLWidget):
    xRotationChanged = pyqtSignal(int)
    yRotationChanged = pyqtSignal(int)
    zRotationChanged = pyqtSignal(int)
    PROGRAM_VERTEX_ATTRIBUTE, PROGRAM_TEXCOORD_ATTRIBUTE = range(2)

    vsrc = """
attribute highp vec4 vertex;
attribute mediump vec4 texCoord;
varying mediump vec4 texc;
uniform mediump mat4 matrix;
void main(void)
{
    gl_Position = matrix * vertex;
    texc = texCoord;
}
"""

    fsrc = """
uniform sampler2D texture;
varying mediump vec4 texc;
void main(void)
{
    gl_FragColor = texture2D(texture, texc.st);
}
"""

    coords = (
        ((+1, -1, -1), (-1, -1, -1), (-1, +1, -1), (+1, +1, -1)),
        ((+1, +1, -1), (-1, +1, -1), (-1, +1, +1), (+1, +1, +1)),
        ((+1, -1, +1), (+1, -1, -1), (+1, +1, -1), (+1, +1, +1)),
        ((-1, -1, -1), (-1, -1, +1), (-1, +1, +1), (-1, +1, -1)),
        ((+1, -1, +1), (-1, -1, +1), (-1, -1, -1), (+1, -1, -1)),
        ((-1, -1, +1), (+1, -1, +1), (+1, +1, +1), (-1, +1, +1))
    )

    def __init__(self, parent=None):
        super(TexturizedCubeWidget, self).__init__(parent)

        self.clearColor = QColor(Qt.black)
        self.xRot = 0
        self.yRot = 0
        self.zRot = 0
        self.program = None

        self.lastPos = QPoint()

    def minimumSizeHint(self):
        return QSize(50, 50)

    def sizeHint(self):
        return QSize(400, 400)

    def setXRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.xRot:
            self.xRot = angle
            self.xRotationChanged.emit(angle)
            self.update()

    def setYRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.yRot:
            self.yRot = angle
            self.yRotationChanged.emit(angle)
            self.update()

    def setZRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.zRot:
            self.zRot = angle
            self.zRotationChanged.emit(angle)
            self.update()

    def rotateBy(self, xAngle, yAngle, zAngle):
        self.xRot += xAngle
        self.yRot += yAngle
        self.zRot += zAngle
        self.update()

    def setClearColor(self, color):
        self.clearColor = color
        self.update()

    def initializeGL(self):
        version_profile = QOpenGLVersionProfile()
        version_profile.setVersion(2, 0)
        self.gl = self.context().versionFunctions(version_profile)
        self.gl.initializeOpenGLFunctions()

        self.makeObject()

        self.gl.glEnable(self.gl.GL_DEPTH_TEST)
        self.gl.glEnable(self.gl.GL_CULL_FACE)

        vshader = QOpenGLShader(QOpenGLShader.Vertex, self)
        vshader.compileSourceCode(self.vsrc)

        fshader = QOpenGLShader(QOpenGLShader.Fragment, self)
        fshader.compileSourceCode(self.fsrc)

        self.program = QOpenGLShaderProgram()
        self.program.addShader(vshader)
        self.program.addShader(fshader)
        self.program.bindAttributeLocation('vertex',
                                           self.PROGRAM_VERTEX_ATTRIBUTE)
        self.program.bindAttributeLocation('texCoord',
                                           self.PROGRAM_TEXCOORD_ATTRIBUTE)
        self.program.link()

        self.program.bind()
        self.program.setUniformValue('texture', 0)

        self.program.enableAttributeArray(self.PROGRAM_VERTEX_ATTRIBUTE)
        self.program.enableAttributeArray(self.PROGRAM_TEXCOORD_ATTRIBUTE)
        self.program.setAttributeArray(self.PROGRAM_VERTEX_ATTRIBUTE,
                                       self.vertices)
        self.program.setAttributeArray(self.PROGRAM_TEXCOORD_ATTRIBUTE,
                                       self.texCoords)

    def paintGL(self):
        self.gl.glClearColor(self.clearColor.redF(), self.clearColor.greenF(),
                             self.clearColor.blueF(), self.clearColor.alphaF())
        self.gl.glClear(
            self.gl.GL_COLOR_BUFFER_BIT | self.gl.GL_DEPTH_BUFFER_BIT)

        m = QMatrix4x4()
        m.ortho(-0.5, 0.5, 0.5, -0.5, 4.0, 15.0)
        m.translate(0.0, 0.0, -10.0)
        m.rotate(self.xRot / 16.0, 1.0, 0.0, 0.0)
        m.rotate(self.yRot / 16.0, 0.0, 1.0, 0.0)
        m.rotate(self.zRot / 16.0, 0.0, 0.0, 1.0)

        self.program.setUniformValue('matrix', m)

        for i, texture in enumerate(self.textures):
            texture.bind()
            self.gl.glDrawArrays(self.gl.GL_TRIANGLE_FAN, i * 4, 4)

    def resizeGL(self, width, height):
        side = min(width, height)
        self.gl.glViewport((width - side) // 2, (height - side) // 2, side, side)

    def mousePressEvent(self, event):
        self.lastPos = event.pos()

    def mouseMoveEvent(self, event):
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()

        if event.buttons() & Qt.LeftButton:
            self.rotateBy(8 * dy, 8 * dx, 0)
        elif event.buttons() & Qt.RightButton:
            self.rotateBy(8 * dy, 0, 8 * dx)

        self.lastPos = event.pos()

    def makeObject(self):
        self.textures = []
        self.texCoords = []
        self.vertices = []

        root = QFileInfo(__file__).absolutePath()

        for i in range(6):
            self.textures.append(
                QOpenGLTexture(
                    QImage(root + ('/images/side%d.png' % (i + 1))).mirrored()))

            for j in range(4):
                self.texCoords.append(((j == 0 or j == 3), (j == 0 or j == 1)))

                x, y, z = self.coords[i][j]
                self.vertices.append((0.2 * x, 0.2 * y, 0.2 * z))

    def normalizeAngle(self, angle):
        while angle < 0:
            angle += 360 * 16
        while angle > 360 * 16:
            angle -= 360 * 16
        return angle
