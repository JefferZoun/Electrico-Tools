"""Posiciones del escritorio: límites visibles y preferencias JSON tolerantes."""
import json
import math
from pathlib import Path

DEFAULT_POSITIONS={"resistencias":(28,38),"fuentes":(28,180),"formulas":(28,322),"pong":(156,38),"pinball":(156,180),"flappy":(156,322)}


class IconLayout:
    def __init__(self,path):
        self.path=Path(path)
        self.positions=dict(DEFAULT_POSITIONS)
        try:
            data=json.loads(self.path.read_text(encoding="utf-8"))
            if isinstance(data,dict):
                for key,point in data.items():
                    if key in self.positions and isinstance(point,list) and len(point)==2:
                        if all(isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v) for v in point):
                            self.positions[key]=tuple(point)
        except (OSError,ValueError,TypeError):
            pass

    def visible(self,key,width,height):
        x,y=self.positions[key]
        return (max(14,min(x,max(14,width-102))),max(10,min(y,max(10,height-108))))

    def move(self,key,x,y,width,height):
        self.positions[key]=(x,y)
        self.positions[key]=self.visible(key,width,height)
        return self.positions[key]

    def save(self):
        try:
            self.path.parent.mkdir(parents=True,exist_ok=True)
            temporary=self.path.with_suffix(".tmp")
            temporary.write_text(json.dumps(self.positions,ensure_ascii=False,indent=2),encoding="utf-8")
            temporary.replace(self.path)
            return True
        except OSError:
            return False
