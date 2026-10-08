from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush
from PyQt6.QtWidgets import QWidget

class LineChartWidget(QWidget):
    """Custom widget to draw real-time line charts for CPU/RAM history"""
    def __init__(self, title, color, parent=None):
        super().__init__(parent)
        self.title = title
        self.color = color
        self.data_history = [0.0] * 30
        self.setMinimumHeight(150)

    def update_data(self, new_value):
        self.data_history.append(new_value)
        if len(self.data_history) > 30:
            self.data_history.pop(0)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()

        painter.setBrush(QBrush(QColor("#11111b")))
        painter.setPen(QPen(QColor("#313244"), 1))
        painter.drawRoundedRect(QRectF(0, 0, width, height), 8, 8)

        painter.setPen(QColor("#cdd6f4"))
        painter.setFont(self.font())
        painter.drawText(15, 25, f"{self.title}: {self.data_history[-1]:.1f}%")

        if len(self.data_history) < 2:
            return

        painter.setPen(QPen(QColor("#313244"), 1, Qt.PenStyle.DashLine))
        painter.drawLine(15, 50, width - 15, 50)
        painter.drawLine(15, height - 30, width - 15, height - 30)

        path_pen = QPen(self.color, 2)
        painter.setPen(path_pen)

        step_x = (width - 30) / max(1, len(self.data_history) - 1)
        max_val = 100.0
        graph_height = height - 80

        for i in range(len(self.data_history) - 1):
            x1 = 15 + i * step_x
            y1 = (height - 30) - (self.data_history[i] / max_val) * graph_height
            
            x2 = 15 + (i + 1) * step_x
            y2 = (height - 30) - (self.data_history[i+1] / max_val) * graph_height
            
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))