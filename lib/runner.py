import ansible_runner

from config import configuration


def _get_ext_args(**kwargs):
    """
    Assemble kwargs into ansible CLI options
    :param kwargs: keyword arguments for ansible arguments
    :return: formatted "-e" string
    """
    payload = ""

    for arg in kwargs:
        payload += "-e " + str(arg) + "=" + str(kwargs.get(arg)) + " "

    return payload.lstrip()


r = ansible_runner.run(
    private_data_dir="automation/",
    playbook="install.yml",
    rotate_artifacts=1,
    cmdline=_get_ext_args(
        ansible_port=34553,
        ansible_ssh_private_key_file="ssh-key",
        ansible_user="root",

        asn=configuration["asn"],
        ipv4_prefix=configuration["ipv4_prefix"],
        ipv6_prefix=configuration["ipv6_prefix"]
    ),
)

# print("{}: {}".format(r.status, r.rc))
# # successful: 0
# for each_host_event in r.events:
#     print(each_host_event["event"])
print("Final status:")
print(r.stats)
