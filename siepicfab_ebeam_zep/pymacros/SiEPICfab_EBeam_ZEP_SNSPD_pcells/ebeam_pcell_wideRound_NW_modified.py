# Waveguide Bragg grating
# imported from SiEPIC_EBeam_PDK.  Model does not exist. Layout only.

from . import *
import pya
from pya import *
import math
class ebeam_pcell_wideRound_NW_modified(pya.PCellDeclarationHelper):
  def __init__(self):
    super(ebeam_pcell_wideRound_NW_modified , self).__init__()

    from SiEPIC.utils import get_technology_by_name
    self.technology_name = 'SiEPICfab_EBeam_ZEP'
    TECHNOLOGY = get_technology_by_name(self.technology_name)
    self.TECHNOLOGY = TECHNOLOGY

    # Override NbTiN to hardcoded 1/69
    self.param("layer", self.TypeLayer, "Layer - NW", default=pya.LayerInfo(1, 69))
    self.param("pinrec", self.TypeLayer, "PinRec Layer", default=TECHNOLOGY['PinRec'])
    self.param("devrec", self.TypeLayer, "DevRec Layer", default=TECHNOLOGY['DevRec'])
    self.param("w", self.TypeDouble, "NW width (microns)", default = 0.03)
    self.param("l", self.TypeDouble, "NW length (microns)", default = 100)
    self.param("bend_w", self.TypeDouble, "Bend Width (microns)", default = 0.03)
    self.param("radius", self.TypeDouble, "radius (microns)", default = 0.175)
    self.param("n_vertices", self.TypeInt, "Vertices of a hole", default = 128)
    

  def coerce_parameters_impl(self):
    pass
    
  def display_text_impl(self):
    return "NbTiNnanowire(w" + ('%.3f' % int(self.w)) +"_r"+('%.3f' % int(self.radius))+ "_l" + ('%.3f' % int(self.l)) + ")"
    
  def can_create_from_shape(self, layout, shape, layer):
    return False
    
  def produce_impl(self):
    dbu = self.layout.dbu
    ly = self.layout
    from math import pi, cos, sin

    LayerSiN = ly.layer(self.layer)
    LayerPinRecN = ly.layer(self.pinrec)
    LayerDevRecN = ly.layer(self.devrec)
    LayerMetal = ly.layer(11, 0)  # Ti/Au layer

    w = self.w / dbu
    l = self.l / dbu
    radius = self.radius / dbu
    bend_w = self.bend_w / dbu
    n_vertices = self.n_vertices

    shapes = self.cell.shapes

    W = radius + 0.0005 / dbu + w
    W_2 = radius + 0.0005 / dbu
    Y = l / 2 - radius - bend_w

    # Rectangle: full body
    square1 = Region(Box(-W, -l/2, W, l/2))

    # Rectangle: vertical center cutout
    square2 = Region(Box(-W_2, -l/2, W_2, Y))

    # Arch: half-circle cutout at top
    theta = 2 * pi / n_vertices
    arc_pts = [
        Point.from_dpoint(DPoint(radius * cos(i * theta), radius * sin(i * theta) + Y))
        for i in range(n_vertices)
    ]
    arch_poly = Polygon(arc_pts)
    curve = Region(arch_poly)

    # Tapers
    taper1_poly = Polygon([
        Point(-W, -l/2),
        Point(-W + w, -l/2),
        Point(-W + w - 2 / dbu, -l/2 - 10 / dbu),
        Point(-W - 7 / dbu, -l/2 - 10 / dbu)
    ])
    taper2_poly = Polygon([
        Point(W, -l/2),
        Point(W - w, -l/2),
        Point(W - w + 2 / dbu, -l/2 - 10 / dbu),
        Point(W + 7 / dbu, -l/2 - 10 / dbu)
    ])
    tapers = Region()
    tapers.insert(taper1_poly)
    tapers.insert(taper2_poly)

    # Final shape
    wire_shape = square1 - square2 - curve + tapers
    shapes(LayerSiN).insert(wire_shape)

    # Metal overlap
    metal1 = Polygon([
        Point(-W - 0.02 / dbu, -l/2),
        Point(-W + w + 0.02 / dbu, -l/2),
        Point(-W + w - 2 / dbu, -l/2 - 10 / dbu),
        Point(-W - 7 / dbu, -l/2 - 10 / dbu)
    ])
    metal2 = Polygon([
        Point(W + 0.02 / dbu, -l/2),
        Point(W - w - 0.02 / dbu, -l/2),
        Point(W - w + 2 / dbu, -l/2 - 10 / dbu),
        Point(W + 7 / dbu, -l/2 - 10 / dbu)
    ])
    shapes(LayerMetal).insert(metal1)
    shapes(LayerMetal).insert(metal2)

    # Pins
    pin1 = Path([Point(-W + w/2 - 4.5 / dbu, -l/2 - 10 / dbu + w),
                 Point(-W + w/2 - 4.5 / dbu, -w - l/2 - 10 / dbu)],
                w + 5 / dbu)
    shapes(LayerPinRecN).insert(pin1)
    shapes(LayerPinRecN).insert(Text("pin2", Trans(Trans.R270, -W + w/2 - 4.5 / dbu, -l/2 - 10 / dbu))).text_size = 0.4 / dbu

    pin2 = Path([Point(W - w/2 + 4.5 / dbu, -l/2 - 10 / dbu + w),
                 Point(W - w/2 + 4.5 / dbu, -w - l/2 - 10 / dbu)],
                w + 5 / dbu)
    shapes(LayerPinRecN).insert(pin2)
    shapes(LayerPinRecN).insert(Text("pin1", Trans(Trans.R270, W - w/2 + 4.5 / dbu, -l/2 - 10 / dbu))).text_size = 0.4 / dbu

    # DevRec
    devrec_box = [
        Point(-2 * (radius + 2 * w), -l / 2),
        Point(2 * (radius + 2 * w), -l / 2),
        Point(2 * (radius + 2 * w), l / 2),
        Point(-2 * (radius + 2 * w), l / 2)
    ]
    shapes(LayerDevRecN).insert(Polygon(devrec_box))

    # Text
    t = Trans(Trans.R270, radius, l / 4)
    label = Text('NbTiNnanowire:w=%.3fu r=%.3fu l=%.3fu' % (int(self.w) * 1000, int(self.radius) * 1000, int(self.l) * 1000), t)
    shapes(LayerDevRecN).insert(label).text_size = 0.5 / dbu
