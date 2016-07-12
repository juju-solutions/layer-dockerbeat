#!/usr/bin/python3

import amulet
import unittest

seconds = 1100


class TestDockerbeat(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Perform a one time setup for this class including a deployment."""
        cls.deployment = amulet.Deployment(series='xenial')

        cls.deployment.add('cs:~lazypower/docker-22')
        cls.deployment.add('dockerbeat')
        # This line will test the relation to a regular charm.
        cls.deployment.relate('docker:juju-info', 'dockerbeat:beats-host')

        try:
            cls.deployment.setup(timeout=seconds)
            cls.deployment.sentry.wait()
        except amulet.helpers.TimeoutError:
            message = "The deploy did not setup in {0} seconds".format(seconds)
            amulet.raise_status(amulet.SKIP, msg=message)
        except:
            raise
        cls.unit = cls.deployment.sentry['dockerbeat'][0]

    def test_dockerbeat_binary(self):
        """Verify that the dockerbeat binary is installed, on the path and is
        functioning properly for this architecture."""
        # dockerbeat -version
        output, code = self.unit.run('dockerbeat -h')
        print(output)
        if code != 0:
            message = 'Dockerbeat unable to return help message.'
            amulet.raise_status(amulet.FAIL, msg=message)
        # dockerbeat -devices
        output, code = self.unit.run('dockerbeat -version')
        print(output)
        if code != 0:
            message = 'Dockerbeat unable to return version.'
            amulet.raise_status(amulet.FAIL, msg=message)


if __name__ == '__main__':
    unittest.main()
