"""Reescala el fondo con Tk y la biblioteca estándar; no necesita Pillow."""
from functools import lru_cache
import tkinter as tk


class Wallpaper:
    def __init__(self, master, path):
        source = tk.PhotoImage(master=master, file=str(path), format="png")
        data = source.tk.call(str(source), "data", "-format", "ppm")
        header, dimensions, maximum, self.pixels = data.split(b"\n", 3)
        if header != b"P6" or maximum != b"255":
            raise ValueError("Formato de fondo no admitido.")
        self.width, self.height = map(int, dimensions.split())

    @lru_cache(maxsize=3)
    def resized(self, width, height):
        # Ajuste de tipo cover: conserva la proporción y recorta el sobrante.
        scale = max(width/self.width, height/self.height)
        visible_w, visible_h = width/scale, height/scale
        offset_x, offset_y = (self.width-visible_w)/2, (self.height-visible_h)/2
        indices = [min(self.width-1, int(offset_x+x/scale))*3 for x in range(width)]
        rows = {}
        output = []
        stride = self.width*3
        for y in range(height):
            sy = min(self.height-1, int(offset_y+y/scale))
            if sy not in rows:
                row = self.pixels[sy*stride:(sy+1)*stride]
                rows[sy] = b"".join(row[x:x+3] for x in indices)
            output.append(rows[sy])
        return f"P6\n{width} {height}\n255\n".encode()+b"".join(output)

    def image(self, master, width, height):
        return tk.PhotoImage(master=master, data=self.resized(max(1,width),max(1,height)), format="ppm")
