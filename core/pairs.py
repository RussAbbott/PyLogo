
from __future__ import annotations

from functools import lru_cache

import math

import core.gui as gui
import core.utils as utils


class XY(tuple):

    def __add__(self, xy: XY):
        xx = self[0] + xy[0]
        yy = self[1] + xy[1]
        return self.restore_type(xx, yy)

    def __truediv__(self, scalar):
        return self * (1/scalar)

    def __mul__(self, scalar):
        xx = self.x * scalar
        yy = self.y * scalar
        return self.restore_type(xx, yy)

    def __str__(self):
        clas_string = utils.extract_class_name(self.__class__)
        return f'{clas_string}{(self.x, self.y)}'

    def __sub__(self, xy: XY):
        xx = self[0] - xy[0]
        yy = self[1] - xy[1]
        return self.restore_type(xx, yy)

    def as_int(self):
        return self.restore_type(int(self.x), int(self.y))

    def restore_type(self, xx, yy):
        cls = type(self)
        return cls((xx, yy))

    def round(self, prec=0):
        clas = type(self)
        return clas((round(self.x, prec), round(self.y, prec)))

    def wrap3(self, x_limit, y_limit):
        xx = self.x % x_limit
        yy = self.y % y_limit
        return self.restore_type(xx, yy)

    @property
    def x(self):
        return self[0]

    @property
    def y(self):
        return self[1]


class Pixel_xy(XY):

    # Will be set to Pixel_xy(0, 0) after the Pixel_xy class is defined.
    pixel_xy_00 = None

    def __str__(self):
        return f'Pixel_xy{self.x, self.y}'

    def closest_block(self, blocks, wrap=True):
        closest =  min(blocks, key=lambda block: self.distance_to(block.center_pixel.x, wrap))
        return closest

    def distance_to(self, other, wrap):
        # Try all ways to get there including wrapping around.
        # wrap = not World.THE_WORLD.get_gui_value('bounce')
        # Can't do this directly since importing World would be circular
        end_pts = [(self, other)]
        if wrap:
            screen_width = gui.SCREEN_PIXEL_WIDTH()
            screen_height = gui.SCREEN_PIXEL_HEIGHT()
            wrapped_end_pts = [((self+a+b).wrap3(screen_width, screen_height),
                                (other+a+b).wrap3(screen_width, screen_height))
                               for a in [Pixel_xy.pixel_xy_00, Pixel_xy((screen_width/2, 0))]
                               for b in [Pixel_xy.pixel_xy_00, Pixel_xy((0, screen_height/2))]
                               ]
            end_pts += wrapped_end_pts
        dist = min(math.hypot(start.x - end.x, start.y - end.y) for (start, end) in end_pts)
        return dist

    def heading_toward(self, to_pixel: Pixel_xy):
        """ The heading to face from the from_pixel to the to_pixel """
        # Make the default heading 0 if from_pixel == to_pixel.
        if self == to_pixel:
            return 0
        delta_x = to_pixel.x - self.x
        delta_y = to_pixel.y - self.y
        new_heading = utils.dxdy_to_heading(delta_x, delta_y, default_heading=0)
        return new_heading

    def pixel_to_row_col(self: Pixel_xy):
        """
        Get the patch RowCol for this pixel
       """
        row = self.y // gui.BLOCK_SPACING()
        col = self.x // gui.BLOCK_SPACING()
        return RowCol((int(row), int(col)))

    def wrap(self):
        screen_rect = gui.SCREEN.get_rect()
        # Must wrap at screen_rect.w-1 and screen_rect.h-1 because the screen
        # is one pixel larger than the grid of patches.
        wrapped = self.wrap3(screen_rect.w-1, screen_rect.h-1)
        return wrapped


Pixel_xy.pixel_xy_00 = Pixel_xy((0, 0))


class RowCol(XY):

    def __str__(self):
        return f'RowCol{self.row, self.col}'

    @property
    def col(self):
        return int(self.y)

    @property
    def row(self):
        return int(self.x)

    def patch_to_center_pixel(self) -> Pixel_xy:
        """
        Get the center_pixel position for this RowCol.
        Leave a border of 1 pixel at the top and left of the patches
        """
        pv = Pixel_xy((1 + gui.BLOCK_SPACING() * self.col + gui.HALF_PATCH_SIZE(),
                       1 + gui.BLOCK_SPACING() * self.row + gui.HALF_PATCH_SIZE()))
        return pv

    def wrap(self):
        wrapped = self.wrap3(gui.PATCH_ROWS, gui.PATCH_COLS)
        return wrapped


class Velocity(XY):

    velocity_00 = None

    def __str__(self):
        return f'Velocity{self.dx, self.dy}'

    # The @property decorator allows you to call the function without parentheses:
    # v = Velocity(3, 4)
    # v.dx => 3
    @property
    def dx(self):
        return self.x

    @property
    def dy(self):
        return self.y


Velocity.velocity_00 = Velocity((0, 0))


def center_pixel():
    rect = gui.SCREEN.get_rect()
    cp = Pixel_xy((rect.centerx, rect.centery))
    return cp


def heading_and_speed_to_velocity(heading, speed) -> Velocity:
    unit_dxdy = heading_to_unit_dxdy(heading)
    velocity = unit_dxdy * speed
    return velocity


@lru_cache(maxsize=512)
def heading_to_unit_dxdy(heading) -> Velocity:
    """ Convert a heading to a (dx, dy) pair as a unit velocity """
    angle = utils.heading_to_angle(heading)
    dx = utils.cos(angle)
    # The -1 accounts for the y-axis being inverted.
    dy = (-1) * utils.sin(angle)
    vel = Velocity((dx, dy))
    return vel


if __name__ == "__main__":

    # Various tests and experiments
    print('\n-----XY-----')
    tuple_3_4 = (3, 4)
    print(f'tuple_3_4: {tuple_3_4}')
    xy_3_4 = XY((3, 4))
    print(f'xy_3_4: {xy_3_4}')
    print(f'Can you explain why this is the case?  tuple_3_4 == xy_3_4: {tuple_3_4 == xy_3_4}!')

    print(f'tuple_3_4 + tuple_3_4: {tuple_3_4 + tuple_3_4}')
    print(f'xy_3_4 + xy_3_4: {xy_3_4 + xy_3_4}')
    concat_3_4_5 = tuple_3_4 * 5
    print(f'concat_3_4_5: {concat_3_4_5}')
    product_3_4_5 = xy_3_4 * 5
    print(f'product_3_4_5: {product_3_4_5}')
    product_5_3_4 = 5 * xy_3_4
    print(f'product_5_3_4: {product_5_3_4}')
    # print('\n-----Pixel_xy-----')
    # a = Pixel_xy((3, 4))
    # print(f'a: {a}')
    # print(f'a+a: {a+a}')
    # print(f'a-a: {a-a}')
    #
    # # noinspection PyTypeChecker
    # b: XY = a*3
    # assert isinstance(b, Pixel_xy)
    # print(f'a*3, b: {a*3} {b}')
    # print(f'b = a*3: {b} = {a*3}: ({b}, {a*3})  {f"({b}, {a*3})"}  {(b, a*3)} {str((b, a*3))}')
    # print(f'a-a: {a-a}')
    # print(f'a*(-1): {a*(-1)}')
    # print(f'b.wrap3(2, 5): {b.wrap3(2, 5)}')
    #
    # pv = Pixel_xy((1.234, 5.678))
    # print(pv.round(2))
    #
    # vel = Velocity((1.234, 5.678))
    # print(vel.round(2))
    #
    # print('\n-----RowCol-----')
    # rc = RowCol((3, 4))
    # print(rc)    # , rc.as_tuple(), rc == rc.as_tuple())
    #
    # print('\n-----distance-----')
    # screen_width = gui.SCREEN_PIXEL_WIDTH()
    # screen_height = gui.SCREEN_PIXEL_HEIGHT()
    # v1 = Pixel_xy((1, 1))
    # v2 = Pixel_xy((2, 2))
    # print(v1.distance_to(v2, True))
    # print(v1.distance_to(v2, False))
    # v3 = (v1 - v2).wrap3(screen_width, screen_height)
    # print(v1.round(2), v2.round(2), v3.round(2))
    # print(v1.distance_to(v3, True))
    # print(v1.distance_to(v3, False))
    # print(v3.distance_to(v1, True))
    # print(v3.distance_to(v1, False))
    # print('-----------------------------')
    # v1 = Pixel_xy((1, 1))
    # v02 = Pixel_xy((0, 2))
    # v20 = Pixel_xy((2, 0))
    # v03 = (v1 - v02).wrap3(screen_width, screen_height)
    # print(v1.distance_to(v03, True))
    # print(v1.distance_to(v03, False))
    # v30 = (v1 - v20).wrap3(screen_width, screen_height)
    # print(v1.distance_to(v30, True))
    # print(v1.distance_to(v30, False))
