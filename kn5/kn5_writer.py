# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import struct


ENCODING = 'utf-8'


class KN5Writer():
    def __init__(self, file):
        self.file = file

    def write_string(self, string):
        string_bytes = string.encode(ENCODING)
        self.write_uint(len(string_bytes))
        self.file.write(string_bytes)

    def write_blob(self, blob):
        self.write_uint(len(blob))
        self.file.write(blob)

    def write_uint(self, int_val):
        self.file.write(struct.pack("I", int_val))

    def write_int(self, int_val):
        self.file.write(struct.pack("i", int_val))

    def write_ushort(self, short):
        self.file.write(struct.pack("H", short))

    def write_byte(self, byte):
        self.file.write(struct.pack("B", byte))

    def write_bool(self, bool_val):
        if str(bool_val)=='true':
            bool_val = True
        self.file.write(struct.pack("?", bool_val))

    def write_float(self, f):
        self.file.write(struct.pack("f", f))

    def write_vector2(self, vector2):
        self.file.write(struct.pack("2f", *vector2))

    def write_vector3(self, vector3):
        self.file.write(struct.pack("3f", *vector3))

    def write_vector11(self, a3, b3, c2, d3):
        self.file.write(struct.pack("3f3f2f3f", *a3, *b3, *c2, *d3))

    def write_vector44(self, a3, b3, c2, d3, e3, f3, g2, h3, i3, j3, k2, l3, m3, n3, o2, p3):
        self.file.write(struct.pack("3f3f2f3f3f3f2f3f3f3f2f3f3f3f2f3f", *a3, *b3, *c2, *d3, *e3, *f3, *g2, *h3, *i3, *j3, *k2, *l3, *m3, *n3, *o2, *p3))

    def write_vector88(self, a3, b3, c2, d3, e3, f3, g2, h3, i3, j3, k2, l3, m3, n3, o2, p3, aa3, ab3, ac2, ad3, ae3, af3, ag2, ah3, ai3, aj3, ak2, al3, am3, an3, ao2, ap3):
        self.file.write(struct.pack("3f3f2f3f3f3f2f3f3f3f2f3f3f3f2f3f3f3f2f3f3f3f2f3f3f3f2f3f3f3f2f3f", *a3, *b3, *c2, *d3, *e3, *f3, *g2, *h3, *i3, *j3, *k2, *l3, *m3, *n3, *o2, *p3, *aa3, *ab3, *ac2, *ad3, *ae3, *af3, *ag2, *ah3, *ai3, *aj3, *ak2, *al3, *am3, *an3, *ao2, *ap3))

    def write_vector16(self, a3, b3, c2, d3, e3, f3, g2, h3, i3, j3, k2, l3, m3, n3, o2, p3, aa3, ab3, ac2, ad3, ae3, af3, ag2, ah3, ai3, aj3, ak2, al3, am3, an3, ao2,
                            ap3,bba3,bbb3,bbc2,bbd3,bbe3,bbf3,bbg2,bbh3,bbi3,bbj3,bbk2,bbl3,bbm3,bbn3,bbo2,bbp3,bbaa3,bbab3,bbac2,bbad3,bbae3,bbaf3,bbag2,bbah3,bbai3,bbaj3,bbak2,bbal3,bbam3,bban3,bbao2,bbap3):
        self.file.write(struct.pack("3f3f2f3f3f3f2f3f3f3f2f3f3f3f2f3f3f3f2f3f3f3f2f3f3f3f2f3f3f3f2f3f3f3f2f3f3f3f2f3f3f3f2f3f3f3f2f3f3f3f2f3f3f3f2f3f3f3f2f3f3f3f2f3f",
                                    *a3, *b3, *c2, *d3, *e3, *f3, *g2, *h3, *i3, *j3, *k2, *l3, *m3, *n3, *o2, *p3, *aa3, *ab3, *ac2, *ad3, *ae3, *af3, *ag2, *ah3, *ai3, *aj3, *ak2, *al3, *am3, *an3, *ao2, *ap3,
                                    *bba3,*bbb3,*bbc2,*bbd3,*bbe3,*bbf3,*bbg2,*bbh3,*bbi3,*bbj3,*bbk2,*bbl3,*bbm3,*bbn3,*bbo2,*bbp3,*bbaa3,*bbab3,*bbac2,*bbad3,*bbae3,*bbaf3,*bbag2,*bbah3,*bbai3,*bbaj3,*bbak2,*bbal3,*bbam3,*bban3,*bbao2,*bbap3))

    def write_vector4(self, vector4):
        self.file.write(struct.pack("4f", *vector4))

    def write_matrix(self, matrix):
        for row in range(4):
            for col in range(4):
                self.write_float(matrix[col][row])
