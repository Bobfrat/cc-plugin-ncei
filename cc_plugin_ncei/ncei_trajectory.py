#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
cc_plugin_ncei/ncei_trajectory.py
'''

from compliance_checker.base import Result, BaseCheck, score_group
from cc_plugin_ncei.ncei_base import NCEIBaseCheck, TestCtx
from cc_plugin_ncei import util


class NCEITrajectory(NCEIBaseCheck):
    register_checker = True
    _cc_spec = 'ncei-trajectory'
    _cc_spec_version = '1.1'
    _cc_description = '''This test checks the selected file against the NCEI netCDF trajectory Incomplete template version 1.1 (found at https://www.nodc.noaa.gov/data/formats/netcdf/v1.1/trajectoryIncomplete.cdl). The NCEI version 1.1 templates are based on “feature types”, as identified by Unidata and CF, and conform to ACDD version 1.0 and CF version 1.6. You can find more information about the version 1.1 templates at https://www.nodc.noaa.gov/data/formats/netcdf/v1.1/. This test is specifically for the trajectory feature type in an Incomplete multidimensional array representation. This representation is typically used for a series of data points along a path through space with monotonically increasing times.'''
    _cc_url = 'http://www.nodc.noaa.gov/data/formats/netcdf/v1.1/trajectoryIncomplete.cdl'
    _cc_authors = 'Luke Campbell, Dan Maher'
    _cc_checker_version = '2.1.0'

    valid_templates = [
        "NODC_NetCDF_Trajectory_Template_v1.1"
    ]

    valid_feature_types = [
        'trajectory',
        'trajectory_id'
    ]

    @classmethod
    def beliefs(cls):
        '''
        Not applicable for gliders
        '''
        return {}

    def check_dimensions(self, dataset):
        '''
        Checks that the feature types of this dataset are consitent with a trajectory dataset
        '''
        results = []
        required_ctx = TestCtx(BaseCheck.HIGH, 'All geophysical variables are trajectory feature types')

        message = ("{} must be a valid trajectory feature type. It must have dimensions of (trajectoryID, time)."
                   " And all coordinates must have dimensions (trajectoryID, time)")
        for variable in util.get_geophysical_variables(dataset):
            is_valid = util.is_cf_trajectory(dataset, variable)
            is_valid = is_valid or util.is_single_trajectory(dataset, variable)
            required_ctx.assert_true(
                is_valid,
                message.format(variable)
            )
        results.append(required_ctx.to_result())
        return results

    def check_required_attributes(self, dataset):
        '''
        Verifies that the dataset contains the NCEI required and highly recommended global attributes
        '''
        results = []
        required_ctx = TestCtx(BaseCheck.HIGH, 'Required Global Attributes for Trajectory dataset')
        required_ctx.assert_true(
            getattr(dataset, 'nodc_template_version', '').lower() == self.valid_templates[0].lower(),
            'nodc_template_version attribute must be {}'.format(self.valid_templates[0])
        )
        required_ctx.assert_true(
            getattr(dataset, 'cdm_data_type', '') == 'Trajectory',
            'cdm_data_type attribute must be set to Trajectory'
        )
        required_ctx.assert_true(
            getattr(dataset, 'featureType', '') == 'trajectory',
            'featureType attribute must be set to trajectory'
        )
        results.append(required_ctx.to_result())
        return results

    def check_trajectory_id(self, dataset):
        '''
        Checks that if a variable exists for the trajectory id it has the appropriate attributes
        '''
        results = []
        exists_ctx = TestCtx(BaseCheck.MEDIUM, 'Variable defining "trajectory_id" exists')
        trajectory_ids = dataset.get_variables_by_attributes(cf_role='trajectory_id')
        # No need to check
        exists_ctx.assert_true(trajectory_ids, 'variable defining cf_role="trajectory_id" exists')
        if not trajectory_ids:
            return exists_ctx.to_result()
        results.append(exists_ctx.to_result())
        test_ctx = TestCtx(BaseCheck.MEDIUM, 'Recommended attributes for the {} variable'.format(trajectory_ids[0].name))
        test_ctx.assert_true(
            getattr(trajectory_ids[0], 'long_name', '') != "",
            "long_name attribute should exist and not be empty"
        )
        results.append(test_ctx.to_result())
        return results

