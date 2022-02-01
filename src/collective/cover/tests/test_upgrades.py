# -*- coding: utf-8 -*-
from collective.cover.testing import INTEGRATION_TESTING
from plone import api

import unittest


class UpgradeTestCaseBase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self, from_version, to_version):
        self.portal = self.layer["portal"]
        self.setup = self.portal["portal_setup"]
        self.profile_id = u"collective.cover:default"
        self.from_version = from_version
        self.to_version = to_version

    def _create_cover(self, **kwargs):
        with api.env.adopt_roles(["Manager"]):
            return api.content.create(self.portal, "collective.cover.content", **kwargs)

    def _get_upgrade_step(self, title):
        """Get one of the upgrade steps.

        Keyword arguments:
        title -- the title used to register the upgrade step
        """
        self.setup.setLastVersionForProfile(self.profile_id, self.from_version)
        upgrades = self.setup.listUpgrades(self.profile_id)
        steps = [s for s in upgrades[0] if s["title"] == title]
        return steps[0] if steps else None

    def _do_upgrade_step(self, step):
        """Execute an upgrade step.

        Keyword arguments:
        step -- the step we want to run
        """
        request = self.layer["request"]
        request.form["profile_id"] = self.profile_id
        request.form["upgrades"] = [step["id"]]
        self.setup.manage_doUpgrades(request=request)

    def _how_many_upgrades_to_do(self):
        self.setup.setLastVersionForProfile(self.profile_id, self.from_version)
        upgrades = self.setup.listUpgrades(self.profile_id)
        return len(upgrades[0])


# FIXME: This class is just an example of an upgrade step test.
# Must be removed when a first test is created.
class Upgrade31to30TestCase(UpgradeTestCaseBase):
    def setUp(self):
        UpgradeTestCaseBase.setUp(self, u"31", u"30")

    def test_upgrade_step_1(self):
        pass


#    def test_registrations(self):
#        version = self.setup.getLastVersionForProfile(self.profile_id)[0]
#        self.assertGreaterEqual(int(version), int(self.to_version))
#        self.assertEqual(self._how_many_upgrades_to_do(), 1)

#    def test_upgrade_step_2(self):
#        title = u"Upgrade"
#        step = self._get_upgrade_step(title)
#        self.assertIsNotNone(step)
