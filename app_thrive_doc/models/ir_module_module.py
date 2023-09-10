# -*- coding: utf-8 -*-

from thrive import api, fields, models, modules, tools, _
from thrive.exceptions import UserError
import thrive.release
from thrive.tools import get_lang
from thrive.addons.app_common.models.app_import import app_quick_import


class IrModule(models.Model):
    _inherit = 'ir.module.module'

    base_url_doc = fields.Char(string='Doc Url', help="Help doc url router for current app. you can use http prefix or not")

    def module_go_doc(self):
        # 不用 base_url 的
        # 点击后新开窗口访问 help，无设置就 raise 说无
        # base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        self.ensure_one()
        url = self.base_url_doc
        if not url:
            return self.action_error_notify()
        else:
            # 处理语言
            lang = self.env.user.lang or get_lang(self.env).code
            if lang != 'en_US' and url.find('lang') == -1:
                url = url.replace(thrive.release.serie, '%s/%s' % (thrive.release.serie, lang))
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': '_new',
        }

    @api.model
    def action_xml_go_doc(self, xml_id):
        mod_name = xml_id.split('.')[0]
        mod = self.search([('name', '=', mod_name)], limit=1)
        if mod:
            return mod.module_go_doc()
        else:
            raise UserError(_('Module Not Found: %s' % mod_name))

    @api.model
    def app_quick_import_data(self):
        cr = self.env.cr
        app_quick_import(cr, 'app_thrive_doc/data/ir.module.module.csv')

    @api.model
    def action_error_notify(self):
        message = _("There is currently no help document available for the current topic.")
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'target': 'new',
            'params': {
                'message': message,
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }
