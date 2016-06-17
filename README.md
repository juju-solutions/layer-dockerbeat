# Dockerbeat

A lightweight, open source shipper for docker daemon data. Dockerbeat polls
the Docker Engine daemon, and sends cpu, network, memory, and host
information to Logstash for further parsing and enrichment or to Elasticsearch
for centralized storage and analysis.

## Usage

Dockerbeat can be added to any principal charm thanks to the wonders of being
a subordinate charm. The following usage example will deploy the elk stack,
so we can visualize our container data once we've established the link between
dockerbeat and Logstash

    juju deploy ~containers/bundle/elk-stack
    juju deploy ~containers/swarm-core
    juju deploy ~containers/trusty/dockerbeat
    juju add-relation dockerbeat:beats-host swarm
    juju add-relation dockerbeat logstash


### Deploying the minimal Beats formation

If you do not need data buffering and alternate transforms on your data thats
being shipped to ElasticSearch you can simply deploy the 'beats-core' bundle
which stands up Elasticsearch, Kibana, and the three known working Beats
subordinate services.

    juju deploy ~containers/bundle/beats-core
    juju deploy ~containers/bundle/swarm-core
    juju deploy ~containers/trusty/dockerbeat
    juju add-relation filebeat:beats-host swarm
    juju add-relation topbeat:beats-host swarm
    juju add-relation packetbeat:beats-host swarm
    juju add-relation dockerbeat:beats-host swarm

### A note about the beats-host relationship

The Beats suite of charms leverage the implicit "juju-info" relation interface
which is special and unique in the context of subordinates. This is what allows
us to relate the beat to any host, but may have some display oddities in the
juju-gui. Until this is resolved, it's recommended to relate beats to their
principal services using the CLI


## Testing the deployment

The services provide extended status reporting to indicate when they are ready:

    juju status --format=tabular

This is particularly useful when combined with watch to track the on-going
progress of the deployment:

    watch -n 0.5 juju status --format=tabular

The message for each unit will provide information about that unit's state.
Once they all indicate that they are ready, you can navigate to the kibana
url and view the streamed log data from the Ubuntu host.

    juju status kibana --format=yaml | grep public-address

  open http://&lt;kibana-ip&gt;/ in a browser and begin creating your dashboard
  visualizations

## Scale Out Usage

This bundle was designed to scale out. To increase the amount of log storage and
indexers, you can add-units to elasticsearch.

    juju add-unit elasticsearch

You can also increase in multiples, for example: To increase the number of
Logstash parser/buffer/shipping services:

    juju add-unit -n 2 logstash

To monitor additional hosts, simply relate the Dockerbeat subordinate

    juju add-relation dockerbeat:beats-host my-charm


## Contact information

- Charles Butler &lt;charles.butler@canonical.com&gt;

# Need Help?

- [DockerBeat Upstream](https://github.com/ingensi/dockerbeat)
- [Juju mailing list](https://lists.ubuntu.com/mailman/listinfo/juju)
- [Juju Community](https://jujucharms.com/community)
