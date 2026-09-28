import pcbnew
print("PM_* in module:", [n for n in dir(pcbnew) if n.startswith("PM_")])
print()
print("BooleanIntersection methods:", [n for n in dir(pcbnew.SHAPE_POLY_SET) if "Bool" in n or "Intersect" in n or "Collide" in n or "Area" in n or "Fracture" in n or "Simplify" in n])
print()
try:
    print("POLYGON_MODE:", [n for n in dir(pcbnew.POLYGON_MODE) if not n.startswith("_")])
except Exception as e:
    print("no POLYGON_MODE:", e)
print()
import inspect
print(pcbnew.SHAPE_POLY_SET.BooleanIntersection.__doc__)
