#!/usr/bin/env python
'''
The MIT License (MIT)

Copyright (c) 2015 Yusuke Miura, kokufu.ym@gmail.com

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
# standard library
import os
import sys
import optparse
import gettext
import subprocess
# local library
import inkex

class Density:
    def __init__(self, name, scale):
        self.name = name
        self.scale = scale

    def get_res_dir(self, prefix):
        p = prefix if prefix else ""
        return p + self.name

class AndroidIcons(inkex.Effect):
    densities = [Density("ldpi", 0.5),
                 Density("mdpi", 1),
                 Density("hdpi", 1.5),
                 Density("xhdpi", 2),
                 Density("xxhdpi", 3),
                 Density("xxxhdpi", 4)]

    def __init__(self):
        inkex.Effect.__init__(self)
        self.OptionParser.add_option("--output_png",
                                     action="store",
                                     type="string",
                                     dest="output_png",
                                     metavar="FILE",
                                     help="Output png file name")
        self.OptionParser.add_option("--output_png_width",
                                     action="store",
                                     type="int",
                                     dest="output_png_width",
                                     metavar="NUM",
                                     help="Output icon width for mdpi (px)")
        self.OptionParser.add_option("--output_png_height",
                                     action="store",
                                     type="int",
                                     dest="output_png_height",
                                     metavar="NUM",
                                     help="Output icon height for mdpi (px)")
        self.OptionParser.add_option("--dir",
                                     action="store",
                                     type="string",
                                     dest="dir",
                                     metavar="DIR",
                                     help="Directory path to export")
        self.OptionParser.add_option("--create_dir",
                                     action="store",
                                     type="inkbool",
                                     metavar="True/False",
                                     dest="create_dir",
                                     default=False,
                                     help="Create directory, if it does not exists")
        self.OptionParser.add_option("--dir_prefix",
                                     action="store",
                                     type="string",
                                     metavar="PREFIX",
                                     dest="dir_prefix",
                                     help="Directory prefix i.e.) drawable- or mipmap")
        # Add Density Group
        group = optparse.OptionGroup(self.OptionParser, "Select densities to export")
        for density in self.densities:
            group.add_option("--%s" % density.name,
                             action="store",
                             type="inkbool",
                             dest="%s" % density.name,
                             metavar="True/False",
                             default=False,
                             help="x %s" % density.scale)
        self.OptionParser.add_option_group(group)

    def effect(self):
        if not self.validate_inputs():
            return

        exported = False
        for density in self.densities:
            if getattr(self.options, density.name):
                output_dir = os.path.join(self.options.dir, density.get_res_dir(self.options.dir_prefix))
                if not AndroidIcons.check_dir(output_dir, True):
                    return
                output_png = os.path.join(output_dir, self.options.output_png)
                width = self.options.output_png_width * density.scale
                height = self.options.output_png_height * density.scale
                if not AndroidIcons.export_img(self.svg_file, output_png, width, height):
                    return
                exported = True
        if not exported:
            error = _("No Densities are selected")
            inkex.errormsg(error)
            return
        return

    def validate_inputs(self):
        # The user must supply a directory to export:
        if self.options.dir is None:
            error = _('You must give a directory to export the icons.')
            inkex.errormsg(error)
            return False
        # No directory separator at the path end:
        if self.options.dir[-1] == '/' or self.options.dir[-1] == '\\':
            self.options.dir = self.options.dir[0:-1]
        # Test if the directory exists:
        return AndroidIcons.check_dir(self.options.dir, self.options.create_dir)

    @staticmethod
    def check_dir(dir, create_dir):
        if not os.path.exists(dir):
            if create_dir:
                # Try to create it:
                try:
                    os.makedirs(dir)
                except Exception, e:
                    error = _('Can\'t create the directory "%s".' % dir)
                    inkex.errormsg(error)
                    inkex.errormsg(_('Error: %s') % e)
                    return False
            else:
                error = _('The directory "%s" does not exists.') % dir
                inkex.errormsg(error)
                return False
        return True

    @staticmethod
    def export_img(input_svg, output_png, output_png_width, output_png_height):
        p = subprocess.Popen([
                            "inkscape",
                            '--file=%s' % input_svg,
                            '--export-png=%s' % output_png,
                            "--without-gui",
                            "--export-area-page",
                            "--export-width=%d" % output_png_width,
                            "--export-height=%d" % output_png_height
                          ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout_data, stderr_data) = p.communicate()
        if p.returncode != 0:
            error = _(stderr_data)
            inkex.errormsg(error)
            return False
        return True

# Start
try:
    inkex.localize()
except Exception, e:
    _ = gettext.gettext

if __name__ == '__main__':
    effect = AndroidIcons()
    error = effect.affect(output=False)
