from odoo import models, api



class InheritAccountReport(models.Model):
    _inherit = 'account.report'

    def _init_options_partner(self, options, previous_options):
        if not self.filter_partner:
            return
        options['partner'] = True
        previous_partner_ids = previous_options.get('partner_ids') or []
        options['partner_categories'] = previous_options.get('partner_categories') or []

        selected_partner_ids = [int(partner) for partner in previous_partner_ids]
        # search instead of browse so that record rules apply and filter out the ones the user does not have access to
        selected_partners = selected_partner_ids and self.env['res.partner'].with_context(active_test=False).search([('id', 'in', selected_partner_ids)]) or self.env['res.partner']
        options['selected_partner_ids'] = selected_partners.mapped('name')
        options['partner_ids'] = selected_partners.ids
        options['invoice_user_ids'] = []

        selected_partner_category_ids = [int(category) for category in options['partner_categories']]
        selected_partner_categories = selected_partner_category_ids and self.env['res.partner.category'].browse(selected_partner_category_ids) or self.env['res.partner.category']
        options['selected_partner_categories'] = selected_partner_categories.mapped('name')

    @api.model
    def _get_options_partner_domain(self, options):
        """
        add user id in domain for filter
        """
        domain = []
        if options.get('partner_ids'):
            partner_ids = [int(partner) for partner in options['partner_ids']]
            domain.append(('partner_id', 'in', partner_ids))
        if options.get('partner_categories'):
            partner_category_ids = [int(category) for category in options['partner_categories']]
            domain.append(('partner_id.category_id', 'in', partner_category_ids))
        if options.get('invoice_user_ids'):
            user_ids = [int(user) for user in options['invoice_user_ids']]
            domain.append(('move_id.invoice_user_id', 'in', user_ids))
        return domain

    def get_options(self, previous_options):
        """
        extend the get_options function
        set salesperson id in option list
        return : option(dict)
        """

        self.ensure_one()

        initializers_in_sequence = self._get_options_initializers_in_sequence()

        options = {}

        if previous_options.get('_running_export_test'):
            options['_running_export_test'] = True

        # We need report_id to be initialized. Compute the necessary options to check for reroute.
        for reroute_initializer_index, initializer in enumerate(initializers_in_sequence):
            initializer(options, previous_options=previous_options)

            # pylint: disable=W0143
            if initializer == self._init_options_report_id:
                break

        # Stop the computation to check for reroute once we have computed the necessary information
        if (not self.root_report_id or (self.use_sections and self.section_report_ids)) and options['report_id'] != self.id:
            # Load the variant/section instead of the root report
            variant_options = {**previous_options}
            for reroute_opt_key in ('selected_variant_id', 'selected_section_id', 'variants_source_id', 'sections_source_id'):
                opt_val = options.get(reroute_opt_key)
                if opt_val:
                    variant_options[reroute_opt_key] = opt_val

            return self.env['account.report'].browse(options['report_id']).get_options(variant_options)

        # No reroute; keep on and compute the other options
        for initializer_index in range(reroute_initializer_index + 1, len(initializers_in_sequence)):
            initializer = initializers_in_sequence[initializer_index]
            initializer(options, previous_options=previous_options)

        # Sort the buttons list by sequence, for rendering
        options_companies = self.env['res.company'].browse(self.get_report_company_ids(options))
        if not options_companies._all_branches_selected():
            for button in filter(lambda x: not x.get('branch_allowed'), options['buttons']):
                button['disabled'] = True

        options['buttons'] = sorted(options['buttons'], key=lambda x: x.get('sequence', 90))
        if previous_options.get('invoice_user_ids'):
            options.update({'invoice_user_ids': previous_options['invoice_user_ids']})
        return options