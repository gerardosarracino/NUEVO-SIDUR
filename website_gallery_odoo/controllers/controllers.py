# -*- coding: utf-8 -*-

from openerp import http
from openerp.http import request


class Gallery(http.Controller):
    @http.route(['/gallery'], type='http', auth="public", website=True)
    def gallery(self, **kwargs):
        domain = ('website_published', '=', True)
        gallery_images = request.env['website.gallery'].sudo().search([domain])
        return request.render("website_gallery_odoo.gallery_template",
                              {
                                  'gallery_images': gallery_images,
                              })
