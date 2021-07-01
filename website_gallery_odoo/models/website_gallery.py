# -*- coding: utf-8 -*-

from openerp import models, fields, api, tools
import os


def getSize(filename):
    st = os.stat(filename)
    return st.st_size


class WebsiteGallery(models.Model):
    _name = 'website.gallery'
    _description = 'Website gallery'

    name = fields.Char(string="Name of image", required=True)
    alt = fields.Char(string="Alt text of image")
    image = fields.Binary("Image", help="Uploading image", required=True)
    image_resizned = fields.Binary("Image",
                                   help="It is automatically resized as a 'px' value mentiond in pixel aspect ratio mentioned.")
    pixels_width = fields.Float("Pixels width")
    pixels_height = fields.Float("Pixels height")
    size = fields.Char("Size", compute='_get_image_size')
    active = fields.Boolean(default=True)
    website_published = fields.Boolean(default=True)
    description = fields.Text("Description", required=True, help="'alt' text in website gallery view")

    @api.one
    @api.depends('image')
    def _get_image_size(self):
        if self.image:
            self.size = self.image

    @api.multi
    def website_publish_button(self):
        self.ensure_one()
        # if self.env.user.has_group('website.group_website_publisher') and self.website_url != '#':
        #     return self.open_website_url()
        return self.write({'website_published': not self.website_published})

    #     @api.depends('value')
    #     def _value_pc(self):
    #         self.value2 = float(self.value) / 100
    #             image = tools.image_resize_image_big(value)

    # Todo: compress/resize image to specific aspect ratio.
    # @api.one
    # @api.depends('image')
    # def _compute_images(self):
    #     if self._context.get('bin_size'):
    #         self.image = self.image_variant
    #     else:
    #         resized_images = tools.image_get_resized_images(self.image_variant, return_big=True,
    #                                                         avoid_resize_medium=True)
    #         self.image = resized_images['image']

    # @api.one
    # def _set_image_value(self):
    #     # image = tools.image_resize_image_big(self.image_variant)
    #     # print(image)
    #     resized_images = tools.image_get_resized_images(self.image, return_big=True, avoid_resize_medium=True)
    #     print(resized_images)
    #     self.image = resized_images['image']
