
import RefGrid

#"Feature Set" MGRS 100M_GRID "D:\Workspace\ArcGIS Defense Templates\ClrOps-GRG_SEPT2017\scratch.gdb/output_grid" NO_LARGE_GRIDS

f = r"D:\Workspace\scratch\WesternUS.shp"
g = 'MGRS'
s = '100000M_GRID'
o = r"D:\Workspace\ArcGIS Defense Templates\ClrOps-GRG_SEPT2017\scratch.gdb\output_grid"
n = "NO_LARGE_GRIDS"

RG = RefGrid.ReferenceGrid(f, g, s, n)
out_grid = RG.Build(o)

print(out_grid)