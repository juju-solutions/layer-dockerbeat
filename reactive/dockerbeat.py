from charms.reactive import when
from charms.reactive import when_any
from charms.reactive import when_not
from charms.reactive import set_state
from charms.reactive import remove_state

from charmhelpers.core.hookenv import config
from charmhelpers.core.hookenv import resource_get
from charmhelpers.core.hookenv import status_set
from charmhelpers.core.host import lsb_release
from charmhelpers.core.host import service_restart
from charmhelpers.core.templating import render
from charmhelpers.fetch.archiveurl import ArchiveUrlFetchHandler

from elasticbeats import render_without_context
from elasticbeats import push_beat_index

from shlex import split
from subprocess import check_call

import os


@when_not('dockerbeat.installed')
def install_dockerbeat():
    ''' Installs dockerbeat from resources, with a fallback option
    to try to fetch over the network, for 1.25.5 hosts'''

    try:
        bin_path = resource_get('dockerbeat')
    except NotImplementedError:
        # Attempt to fetch and install from configured uri with validation
        bin_path = download_from_upstream()

    full_beat_path = '/usr/local/bin/dockerbeat'

    if not bin_path:
        status_set('blocked', 'Missing dockerbeat binary')
        return

    install(bin_path, full_beat_path)
    os.chmod(full_beat_path, 0o755)

    codename = lsb_release()['DISTRIB_CODENAME']

    # render the apropriate init systems configuration
    if codename == 'trusty':
        render('upstart', '/etc/init/dockerbeat.conf', {})
    else:
        render('systemd', '/etc/systemd/system/dockerbeat.service', {})

    set_state('dockerbeat.installed')


@when('beat.render')
@when_any('elasticsearch.available', 'logstash.available')
def render_beat_template():
    beat_dir = '/etc/dockerbeat'
    if not os.path.exists(beat_dir):
        os.makedirs(beat_dir, exist_ok=True)
    render_without_context('dockerbeat.yml', '/etc/dockerbeat/dockerbeat.yml')
    remove_state('beat.render')
    service_restart('dockerbeat')
    status_set('active', 'Dockerbeat ready')


@when('elasticsearch.available')
@when_not('dockerbeat.index.pushed')
def push_dockerbeat_index(elasticsearch):
    ''' Push the index to ElasticSearch so its easier to aggregate
    the data '''
    render_without_context('dockerbeat.template.json',
                           '/etc/dockerbeat/dockerbeat.template.json')
    hosts = elasticsearch.list_unit_data()
    for host in hosts:
        host_string = "{}:{}".format(host['host'], host['port'])
    push_beat_index(host_string, 'dockerbeat')
    set_state('dockerbeat.index.pushed')


def download_from_upstream():
    if not config('fallback_url') or not config('fallback_sum'):
        status_set('blocked', 'Missing configuration: ')
        return None
    client = ArchiveUrlFetchHandler()
    return client.download_and_validate(config('fallback_url'),
                                        config('fallback_sum'))


def install(src, tgt):
    ''' This method wraps the bash "install" command '''
    return check_call(split('install {} {}'.format(src, tgt)))
