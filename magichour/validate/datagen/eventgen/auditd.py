"""
Manually generate events for auditd.

Example call from auditd_driver.py:
    python auditd_driver.py \
        --auditd \
        -vv \
        -f data/input/audit-ec2-aws-test.log \
        -t data/auditd-minimum.transforms \
        --template-gen logcluster \
        --template-support 1 \
        --event-gen auditd \
        --sort-events-key event
"""
from collections import namedtuple
import re

from magichour.api.local.util.namedtuples import Event

ManualEvent = namedtuple('ManualEvent', ['id', 'template_ids', 'template_regex_pattern', 'template_regex'])

simple_ssh_events = [
    ('ssh.login', r'type=(LOGIN|USER_LOGIN.*? id=\S+)'),
    ('ssh.session.start', r'type=(USER_START)'),
    ('ssh.sesion.cmd', r'type=(USER_CMD)'),
    ('ssh.session.end', r'type=(USER_END)'),
    ('ssh.logout', r'type=(USER_LOGOUT)'),
    ('ssh.session', None),
    ('ssh', None),
    ]


def create_manual_events(manual_events):
    """Create regex patterns to match manual events against templates."""
    result = []
    for name, pattern in manual_events:
        if not pattern:
            # Allow hierarchical events; concat all patterns from events starting with 'name'
            pattern = r'|'.join(p for n, p in manual_events if p and n.startswith(name))
        mevent = ManualEvent(
                id=name,
                template_ids=None,
                template_regex_pattern=pattern,
                template_regex=re.compile(pattern))
        result.append(mevent)
    return result

    
def event_gen(templates, manual_list=simple_ssh_events):
    """Generate events manually against the automatically discovered templates."""
    result = []
    manual_events = create_manual_events(manual_list)
    for mevent in manual_events:
        template_ids = [t.id for t in templates if mevent.template_regex.search(t.raw_str)]
        if template_ids:
            event = Event(id=mevent.id, template_ids=template_ids)
            result.append(event)
    return result


"""
* Time Order: USER-only
ses      pid      ts             auditd_id
543      12333    1455711314.879 29001: node=ec2-aws.example.com type=USER_LOGOUT msg=audit(1455711314.879:29001): pid=12333 uid=0 auid=500 ses=543 msg='op=login id=500 exe="/usr/sbin/sshd" hostname=client.example.net addr=10.11.12.13 terminal=ssh res=success'

544      12369    1455711352.703 29020: node=ec2-aws.example.com type=LOGIN msg=audit(1455711352.703:29020): pid=12369 uid=0 old-auid=-1 auid=500 old-ses=-1 ses=544 res=1
544      12369    1455711352.927 29027: node=ec2-aws.example.com type=USER_LOGIN msg=audit(1455711352.927:29027): pid=12369 uid=0 auid=500 ses=544 msg='op=login id=500 exe="/usr/sbin/sshd" hostname=client.example.net addr=10.11.12.13 terminal=ssh res=success'
544      12397    1455711358.947 29031: node=ec2-aws.example.com type=USER_CMD msg=audit(1455711358.947:29031): pid=12397 uid=500 auid=500 ses=544 msg='cwd="/home/ec2-user" cmd=64617465202B2573 terminal=? res=success'
544      12400    1455711359.955 29039: node=ec2-aws.example.com type=USER_CMD msg=audit(1455711359.955:29039): pid=12400 uid=500 auid=500 ses=544 msg='cwd="/home/ec2-user" cmd=64617465202B2573 terminal=? res=success'
544      12403    1455711364.960 29047: node=ec2-aws.example.com type=USER_CMD msg=audit(1455711364.960:29047): pid=12403 uid=500 auid=500 ses=544 msg='cwd="/home/ec2-user" cmd=64617465202B2573 terminal=? res=success'
544      12406    1455711369.968 29055: node=ec2-aws.example.com type=USER_CMD msg=audit(1455711369.968:29055): pid=12406 uid=500 auid=500 ses=544 msg='cwd="/home/ec2-user" cmd=64617465202B2573 terminal=? res=success'
544      12369    1455711371.516 29063: node=ec2-aws.example.com type=USER_LOGOUT msg=audit(1455711371.516:29063): pid=12369 uid=0 auid=500 ses=544 msg='op=login id=500 exe="/usr/sbin/sshd" hostname=client.example.net addr=10.11.12.13 terminal=ssh res=success'

545      12410    1455711375.044 29082: node=ec2-aws.example.com type=LOGIN msg=audit(1455711375.044:29082): pid=12410 uid=0 old-auid=-1 auid=500 old-ses=-1 ses=545 res=1



* Time Order: All
543      12333    1455711351.895 29008: node=ec2-aws.example.com type=CRYPTO_KEY_USER msg=audit(1455711351.895:29008): pid=12333 uid=0 auid=500 ses=543 msg='op=destroy kind=server fp=18:d5:59:1c:c8:88:5e:d1:1e:45:a4:3b:35:ad:e6:0c direction=? spid=12333 suid=0  exe="/usr/sbin/sshd" hostname=? addr=10.11.12.13 terminal=? res=success'

-1       12370    1455711352.003 29009: node=ec2-aws.example.com type=CRYPTO_KEY_USER msg=audit(1455711352.003:29009): pid=12370 uid=0 auid=-1 ses=-1 msg='op=destroy kind=server fp=70:a2:34:06:1d:e8:70:f3:ec:8d:15:a5:c9:f8:7c:f9 direction=? spid=12370 suid=0  exe="/usr/sbin/sshd" hostname=? addr=10.11.12.13 terminal=? res=success'
-1       12370    1455711352.003 29010: node=ec2-aws.example.com type=CRYPTO_KEY_USER msg=audit(1455711352.003:29010): pid=12370 uid=0 auid=-1 ses=-1 msg='op=destroy kind=server fp=2a:3c:0f:33:24:f5:1b:d9:38:ae:fc:9a:b2:62:0c:65 direction=? spid=12370 suid=0  exe="/usr/sbin/sshd" hostname=? addr=10.11.12.13 terminal=? res=success'
-1       12370    1455711352.003 29011: node=ec2-aws.example.com type=CRYPTO_KEY_USER msg=audit(1455711352.003:29011): pid=12370 uid=0 auid=-1 ses=-1 msg='op=destroy kind=server fp=18:d5:59:1c:c8:88:5e:d1:1e:45:a4:3b:35:ad:e6:0c direction=? spid=12370 suid=0  exe="/usr/sbin/sshd" hostname=? addr=10.11.12.13 terminal=? res=success'
-1       12369    1455711352.083 29012: node=ec2-aws.example.com type=CRYPTO_SESSION msg=audit(1455711352.083:29012): pid=12369 uid=0 auid=-1 ses=-1 msg='op=start direction=from-server cipher=aes128-ctr ksize=128 mac=hmac-sha2-256 pfs=diffie-hellman-group1-sha1 spid=12370 suid=74 rport=56280 laddr=192.168.1.100 lport=22  exe="/usr/sbin/sshd" hostname=? addr=10.11.12.13 terminal=? res=success'
-1       12369    1455711352.083 29013: node=ec2-aws.example.com type=CRYPTO_SESSION msg=audit(1455711352.083:29013): pid=12369 uid=0 auid=-1 ses=-1 msg='op=start direction=from-client cipher=aes128-ctr ksize=128 mac=hmac-sha2-256 pfs=diffie-hellman-group1-sha1 spid=12370 suid=74 rport=56280 laddr=192.168.1.100 lport=22  exe="/usr/sbin/sshd" hostname=? addr=10.11.12.13 terminal=? res=success'
-1       12369    1455711352.703 29014: node=ec2-aws.example.com type=USER_AUTH msg=audit(1455711352.703:29014): pid=12369 uid=0 auid=-1 ses=-1 msg='op=pubkey_auth rport=56280 acct="ec2-user" exe="/usr/sbin/sshd" hostname=? addr=10.11.12.13 terminal=? res=success'
-1       12369    1455711352.703 29015: node=ec2-aws.example.com type=USER_AUTH msg=audit(1455711352.703:29015): pid=12369 uid=0 auid=-1 ses=-1 msg='op=key algo=ssh-rsa size=2048 fp=00:01:02:03:04:05:06:07:08:09:0a:0b:0c:0d:0e:0f rport=56280 acct="ec2-user" exe="/usr/sbin/sshd" hostname=? addr=10.11.12.13 terminal=? res=success'
-1       12369    1455711352.703 29016: node=ec2-aws.example.com type=USER_ACCT msg=audit(1455711352.703:29016): pid=12369 uid=0 auid=-1 ses=-1 msg='op=PAM:accounting grantors=pam_unix,pam_localuser acct="ec2-user" exe="/usr/sbin/sshd" hostname=client.example.net addr=10.11.12.13 terminal=ssh res=success'
-1       12369    1455711352.703 29017: node=ec2-aws.example.com type=CRYPTO_KEY_USER msg=audit(1455711352.703:29017): pid=12369 uid=0 auid=-1 ses=-1 msg='op=destroy kind=session fp=? direction=both spid=12370 suid=74 rport=56280 laddr=192.168.1.100 lport=22  exe="/usr/sbin/sshd" hostname=? addr=10.11.12.13 terminal=? res=success'
-1       12369    1455711352.703 29018: node=ec2-aws.example.com type=USER_AUTH msg=audit(1455711352.703:29018): pid=12369 uid=0 auid=-1 ses=-1 msg='op=success acct="ec2-user" exe="/usr/sbin/sshd" hostname=? addr=10.11.12.13 terminal=ssh res=success'
-1       12369    1455711352.703 29019: node=ec2-aws.example.com type=CRED_ACQ msg=audit(1455711352.703:29019): pid=12369 uid=0 auid=-1 ses=-1 msg='op=PAM:setcred grantors=pam_env,pam_unix acct="ec2-user" exe="/usr/sbin/sshd" hostname=client.example.net addr=10.11.12.13 terminal=ssh res=success'
544      12369    1455711352.703 29020: node=ec2-aws.example.com type=LOGIN msg=audit(1455711352.703:29020): pid=12369 uid=0 old-auid=-1 auid=500 old-ses=-1 ses=544 res=1
544      12369    1455711352.707 29021: node=ec2-aws.example.com type=USER_START msg=audit(1455711352.707:29021): pid=12369 uid=0 auid=500 ses=544 msg='op=PAM:session_open grantors=pam_selinux,pam_loginuid,pam_selinux,pam_namespace,pam_keyinit,pam_keyinit,pam_limits,pam_unix,pam_lastlog acct="ec2-user" exe="/usr/sbin/sshd" hostname=client.example.net addr=10.11.12.13 terminal=ssh res=success'
544      12369    1455711352.707 29022: node=ec2-aws.example.com type=CRYPTO_KEY_USER msg=audit(1455711352.707:29022): pid=12369 uid=0 auid=500 ses=544 msg='op=destroy kind=session fp=? direction=both spid=12369 suid=0 rport=56280 laddr=192.168.1.100 lport=22  exe="/usr/sbin/sshd" hostname=? addr=10.11.12.13 terminal=? res=success'
544      12371    1455711352.707 29023: node=ec2-aws.example.com type=CRYPTO_KEY_USER msg=audit(1455711352.707:29023): pid=12371 uid=0 auid=500 ses=544 msg='op=destroy kind=server fp=70:a2:34:06:1d:e8:70:f3:ec:8d:15:a5:c9:f8:7c:f9 direction=? spid=12371 suid=0  exe="/usr/sbin/sshd" hostname=? addr=10.11.12.13 terminal=? res=success'
544      12371    1455711352.707 29024: node=ec2-aws.example.com type=CRYPTO_KEY_USER msg=audit(1455711352.707:29024): pid=12371 uid=0 auid=500 ses=544 msg='op=destroy kind=server fp=2a:3c:0f:33:24:f5:1b:d9:38:ae:fc:9a:b2:62:0c:65 direction=? spid=12371 suid=0  exe="/usr/sbin/sshd" hostname=? addr=10.11.12.13 terminal=? res=success'
544      12371    1455711352.707 29025: node=ec2-aws.example.com type=CRYPTO_KEY_USER msg=audit(1455711352.707:29025): pid=12371 uid=0 auid=500 ses=544 msg='op=destroy kind=server fp=18:d5:59:1c:c8:88:5e:d1:1e:45:a4:3b:35:ad:e6:0c direction=? spid=12371 suid=0  exe="/usr/sbin/sshd" hostname=? addr=10.11.12.13 terminal=? res=success'
544      12371    1455711352.707 29026: node=ec2-aws.example.com type=CRED_ACQ msg=audit(1455711352.707:29026): pid=12371 uid=0 auid=500 ses=544 msg='op=PAM:setcred grantors=pam_env,pam_unix acct="ec2-user" exe="/usr/sbin/sshd" hostname=client.example.net addr=10.11.12.13 terminal=ssh res=success'
544      12369    1455711352.927 29027: node=ec2-aws.example.com type=USER_LOGIN msg=audit(1455711352.927:29027): pid=12369 uid=0 auid=500 ses=544 msg='op=login id=500 exe="/usr/sbin/sshd" hostname=client.example.net addr=10.11.12.13 terminal=ssh res=success'
544      12369    1455711352.927 29028: node=ec2-aws.example.com type=USER_START msg=audit(1455711352.927:29028): pid=12369 uid=0 auid=500 ses=544 msg='op=login id=500 exe="/usr/sbin/sshd" hostname=client.example.net addr=10.11.12.13 terminal=ssh res=success'
544      12369    1455711352.927 29029: node=ec2-aws.example.com type=CRYPTO_KEY_USER msg=audit(1455711352.927:29029): pid=12369 uid=0 auid=500 ses=544 msg='op=destroy kind=server fp=18:d5:59:1c:c8:88:5e:d1:1e:45:a4:3b:35:ad:e6:0c direction=? spid=12372 suid=500  exe="/usr/sbin/sshd" hostname=? addr=10.11.12.13 terminal=? res=success'
544      12397    1455711358.947 29030: node=ec2-aws.example.com type=SYSCALL msg=audit(1455711358.947:29030): arch=c000003e syscall=59 success=yes exit=0 a0=170e990 a1=170c630 a2=1711970 a3=7ffc383e2520 items=2 ppid=12372 pid=12397 auid=500 uid=500 gid=500 euid=0 suid=0 fsuid=0 egid=500 sgid=500 fsgid=500 tty=(none) ses=544 comm="sudo" exe="/usr/bin/sudo" key="suid-root-exec"
None     None     1455711358.947 29030: node=ec2-aws.example.com type=BPRM_FCAPS msg=audit(1455711358.947:29030): fver=0 fp=0000000000000000 fi=0000000000000000 fe=0 old_pp=0000000000000000 old_pi=0000000000000000 old_pe=0000000000000000 new_pp=0000003fffffffff new_pi=0000000000000000 new_pe=0000003fffffffff
None     None     1455711358.947 29030: node=ec2-aws.example.com type=CWD msg=audit(1455711358.947:29030):  cwd="/home/ec2-user"
None     None     1455711358.947 29030: node=ec2-aws.example.com type=EXECVE msg=audit(1455711358.947:29030): argc=3 a0="sudo" a1="date" a2="+%s"
None     None     1455711358.947 29030: node=ec2-aws.example.com type=PATH msg=audit(1455711358.947:29030): item=0 name="/usr/bin/sudo" inode=407169 dev=ca:01 mode=0104111 ouid=0 ogid=0 rdev=00:00 nametype=NORMAL
None     None     1455711358.947 29030: node=ec2-aws.example.com type=PATH msg=audit(1455711358.947:29030): item=1 name="/lib64/ld-linux-x86-64.so.2" inode=396458 dev=ca:01 mode=0100755 ouid=0 ogid=0 rdev=00:00 nametype=NORMAL
None     None     1455711358.947 29030: node=ec2-aws.example.com type=PROCTITLE msg=audit(1455711358.947:29030): proctitle=7375646F0064617465002B2573
544      12397    1455711358.947 29031: node=ec2-aws.example.com type=USER_CMD msg=audit(1455711358.947:29031): pid=12397 uid=500 auid=500 ses=544 msg='cwd="/home/ec2-user" cmd=64617465202B2573 terminal=? res=success'
544      12397    1455711358.947 29032: node=ec2-aws.example.com type=SYSCALL msg=audit(1455711358.947:29032): arch=c000003e syscall=105 success=yes exit=0 a0=0 a1=7fffffffffffffff a2=555fbb9bbe56 a3=7ff9ad3812e0 items=0 ppid=12372 pid=12397 auid=500 uid=0 gid=500 euid=0 suid=0 fsuid=0 egid=500 sgid=500 fsgid=500 tty=(none) ses=544 comm="sudo" exe="/usr/bin/sudo" key="su-root-activity"
None     None     1455711358.947 29032: node=ec2-aws.example.com type=PROCTITLE msg=audit(1455711358.947:29032): proctitle=7375646F0064617465002B2573
544      12397    1455711358.947 29033: node=ec2-aws.example.com type=CRED_ACQ msg=audit(1455711358.947:29033): pid=12397 uid=0 auid=500 ses=544 msg='op=PAM:setcred grantors=pam_env,pam_unix acct="root" exe="/usr/bin/sudo" hostname=? addr=? terminal=? res=success'
544      12397    1455711358.947 29034: node=ec2-aws.example.com type=USER_START msg=audit(1455711358.947:29034): pid=12397 uid=0 auid=500 ses=544 msg='op=PAM:session_open grantors=pam_keyinit,pam_limits acct="root" exe="/usr/bin/sudo" hostname=? addr=? terminal=? res=success'
544      12398    1455711358.951 29035: node=ec2-aws.example.com type=SYSCALL msg=audit(1455711358.951:29035): arch=c000003e syscall=59 success=yes exit=0 a0=555fbbd24c38 a1=555fbbd1f648 a2=555fbbd28010 a3=6 items=2 ppid=12397 pid=12398 auid=500 uid=0 gid=0 euid=0 suid=0 fsuid=0 egid=0 sgid=0 fsgid=0 tty=(none) ses=544 comm="date" exe="/bin/date" key="su-root-activity"
None     None     1455711358.951 29035: node=ec2-aws.example.com type=CWD msg=audit(1455711358.951:29035):  cwd="/home/ec2-user"
None     None     1455711358.951 29035: node=ec2-aws.example.com type=EXECVE msg=audit(1455711358.951:29035): argc=2 a0="date" a1="+%s"
None     None     1455711358.951 29035: node=ec2-aws.example.com type=PATH msg=audit(1455711358.951:29035): item=0 name="/bin/date" inode=399684 dev=ca:01 mode=0100755 ouid=0 ogid=0 rdev=00:00 nametype=NORMAL
None     None     1455711358.951 29035: node=ec2-aws.example.com type=PATH msg=audit(1455711358.951:29035): item=1 name="/lib64/ld-linux-x86-64.so.2" inode=396458 dev=ca:01 mode=0100755 ouid=0 ogid=0 rdev=00:00 nametype=NORMAL
None     None     1455711358.951 29035: node=ec2-aws.example.com type=PROCTITLE msg=audit(1455711358.951:29035): proctitle=64617465002B2573
544      12397    1455711358.951 29036: node=ec2-aws.example.com type=USER_END msg=audit(1455711358.951:29036): pid=12397 uid=0 auid=500 ses=544 msg='op=PAM:session_close grantors=pam_keyinit,pam_limits acct="root" exe="/usr/bin/sudo" hostname=? addr=? terminal=? res=success'
544      12397    1455711358.951 29037: node=ec2-aws.example.com type=CRED_DISP msg=audit(1455711358.951:29037): pid=12397 uid=0 auid=500 ses=544 msg='op=PAM:setcred grantors=pam_env,pam_unix acct="root" exe="/usr/bin/sudo" hostname=? addr=? terminal=? res=success'
544      12400    1455711359.955 29038: node=ec2-aws.example.com type=SYSCALL msg=audit(1455711359.955:29038): arch=c000003e syscall=59 success=yes exit=0 a0=170e850 a1=170c630 a2=1711970 a3=7ffc383e2520 items=2 ppid=12372 pid=12400 auid=500 uid=500 gid=500 euid=0 suid=0 fsuid=0 egid=500 sgid=500 fsgid=500 tty=(none) ses=544 comm="sudo" exe="/usr/bin/sudo" key="suid-root-exec"
None     None     1455711359.955 29038: node=ec2-aws.example.com type=BPRM_FCAPS msg=audit(1455711359.955:29038): fver=0 fp=0000000000000000 fi=0000000000000000 fe=0 old_pp=0000000000000000 old_pi=0000000000000000 old_pe=0000000000000000 new_pp=0000003fffffffff new_pi=0000000000000000 new_pe=0000003fffffffff
None     None     1455711359.955 29038: node=ec2-aws.example.com type=CWD msg=audit(1455711359.955:29038):  cwd="/home/ec2-user"
None     None     1455711359.955 29038: node=ec2-aws.example.com type=EXECVE msg=audit(1455711359.955:29038): argc=3 a0="sudo" a1="date" a2="+%s"
None     None     1455711359.955 29038: node=ec2-aws.example.com type=PATH msg=audit(1455711359.955:29038): item=0 name="/usr/bin/sudo" inode=407169 dev=ca:01 mode=0104111 ouid=0 ogid=0 rdev=00:00 nametype=NORMAL
None     None     1455711359.955 29038: node=ec2-aws.example.com type=PATH msg=audit(1455711359.955:29038): item=1 name="/lib64/ld-linux-x86-64.so.2" inode=396458 dev=ca:01 mode=0100755 ouid=0 ogid=0 rdev=00:00 nametype=NORMAL
None     None     1455711359.955 29038: node=ec2-aws.example.com type=PROCTITLE msg=audit(1455711359.955:29038): proctitle=7375646F0064617465002B2573
544      12400    1455711359.955 29039: node=ec2-aws.example.com type=USER_CMD msg=audit(1455711359.955:29039): pid=12400 uid=500 auid=500 ses=544 msg='cwd="/home/ec2-user" cmd=64617465202B2573 terminal=? res=success'
544      12400    1455711359.955 29040: node=ec2-aws.example.com type=SYSCALL msg=audit(1455711359.955:29040): arch=c000003e syscall=105 success=yes exit=0 a0=0 a1=7fffffffffffffff a2=55d4aac97e56 a3=7f9b552a72e0 items=0 ppid=12372 pid=12400 auid=500 uid=0 gid=500 euid=0 suid=0 fsuid=0 egid=500 sgid=500 fsgid=500 tty=(none) ses=544 comm="sudo" exe="/usr/bin/sudo" key="su-root-activity"
None     None     1455711359.955 29040: node=ec2-aws.example.com type=PROCTITLE msg=audit(1455711359.955:29040): proctitle=7375646F0064617465002B2573
544      12400    1455711359.955 29041: node=ec2-aws.example.com type=CRED_ACQ msg=audit(1455711359.955:29041): pid=12400 uid=0 auid=500 ses=544 msg='op=PAM:setcred grantors=pam_env,pam_unix acct="root" exe="/usr/bin/sudo" hostname=? addr=? terminal=? res=success'
544      12400    1455711359.955 29042: node=ec2-aws.example.com type=USER_START msg=audit(1455711359.955:29042): pid=12400 uid=0 auid=500 ses=544 msg='op=PAM:session_open grantors=pam_keyinit,pam_limits acct="root" exe="/usr/bin/sudo" hostname=? addr=? terminal=? res=success'
544      12401    1455711359.955 29043: node=ec2-aws.example.com type=SYSCALL msg=audit(1455711359.955:29043): arch=c000003e syscall=59 success=yes exit=0 a0=55d4ab266c38 a1=55d4ab261648 a2=55d4ab26a010 a3=6 items=2 ppid=12400 pid=12401 auid=500 uid=0 gid=0 euid=0 suid=0 fsuid=0 egid=0 sgid=0 fsgid=0 tty=(none) ses=544 comm="date" exe="/bin/date" key="su-root-activity"
None     None     1455711359.955 29043: node=ec2-aws.example.com type=CWD msg=audit(1455711359.955:29043):  cwd="/home/ec2-user"
None     None     1455711359.955 29043: node=ec2-aws.example.com type=EXECVE msg=audit(1455711359.955:29043): argc=2 a0="date" a1="+%s"
None     None     1455711359.955 29043: node=ec2-aws.example.com type=PATH msg=audit(1455711359.955:29043): item=0 name="/bin/date" inode=399684 dev=ca:01 mode=0100755 ouid=0 ogid=0 rdev=00:00 nametype=NORMAL
None     None     1455711359.955 29043: node=ec2-aws.example.com type=PATH msg=audit(1455711359.955:29043): item=1 name="/lib64/ld-linux-x86-64.so.2" inode=396458 dev=ca:01 mode=0100755 ouid=0 ogid=0 rdev=00:00 nametype=NORMAL
None     None     1455711359.955 29043: node=ec2-aws.example.com type=PROCTITLE msg=audit(1455711359.955:29043): proctitle=64617465002B2573
544      12400    1455711359.955 29044: node=ec2-aws.example.com type=USER_END msg=audit(1455711359.955:29044): pid=12400 uid=0 auid=500 ses=544 msg='op=PAM:session_close grantors=pam_keyinit,pam_limits acct="root" exe="/usr/bin/sudo" hostname=? addr=? terminal=? res=success'
544      12400    1455711359.955 29045: node=ec2-aws.example.com type=CRED_DISP msg=audit(1455711359.955:29045): pid=12400 uid=0 auid=500 ses=544 msg='op=PAM:setcred grantors=pam_env,pam_unix acct="root" exe="/usr/bin/sudo" hostname=? addr=? terminal=? res=success'
544      12403    1455711364.960 29046: node=ec2-aws.example.com type=SYSCALL msg=audit(1455711364.960:29046): arch=c000003e syscall=59 success=yes exit=0 a0=170e930 a1=170c630 a2=1711970 a3=7ffc383e2520 items=2 ppid=12372 pid=12403 auid=500 uid=500 gid=500 euid=0 suid=0 fsuid=0 egid=500 sgid=500 fsgid=500 tty=(none) ses=544 comm="sudo" exe="/usr/bin/sudo" key="suid-root-exec"
None     None     1455711364.960 29046: node=ec2-aws.example.com type=BPRM_FCAPS msg=audit(1455711364.960:29046): fver=0 fp=0000000000000000 fi=0000000000000000 fe=0 old_pp=0000000000000000 old_pi=0000000000000000 old_pe=0000000000000000 new_pp=0000003fffffffff new_pi=0000000000000000 new_pe=0000003fffffffff
None     None     1455711364.960 29046: node=ec2-aws.example.com type=CWD msg=audit(1455711364.960:29046):  cwd="/home/ec2-user"
None     None     1455711364.960 29046: node=ec2-aws.example.com type=EXECVE msg=audit(1455711364.960:29046): argc=3 a0="sudo" a1="date" a2="+%s"
None     None     1455711364.960 29046: node=ec2-aws.example.com type=PATH msg=audit(1455711364.960:29046): item=0 name="/usr/bin/sudo" inode=407169 dev=ca:01 mode=0104111 ouid=0 ogid=0 rdev=00:00 nametype=NORMAL
None     None     1455711364.960 29046: node=ec2-aws.example.com type=PATH msg=audit(1455711364.960:29046): item=1 name="/lib64/ld-linux-x86-64.so.2" inode=396458 dev=ca:01 mode=0100755 ouid=0 ogid=0 rdev=00:00 nametype=NORMAL
None     None     1455711364.960 29046: node=ec2-aws.example.com type=PROCTITLE msg=audit(1455711364.960:29046): proctitle=7375646F0064617465002B2573
544      12403    1455711364.960 29047: node=ec2-aws.example.com type=USER_CMD msg=audit(1455711364.960:29047): pid=12403 uid=500 auid=500 ses=544 msg='cwd="/home/ec2-user" cmd=64617465202B2573 terminal=? res=success'
544      12403    1455711364.964 29048: node=ec2-aws.example.com type=SYSCALL msg=audit(1455711364.964:29048): arch=c000003e syscall=105 success=yes exit=0 a0=0 a1=7fffffffffffffff a2=559d5374de56 a3=7f38b81a02e0 items=0 ppid=12372 pid=12403 auid=500 uid=0 gid=500 euid=0 suid=0 fsuid=0 egid=500 sgid=500 fsgid=500 tty=(none) ses=544 comm="sudo" exe="/usr/bin/sudo" key="su-root-activity"
None     None     1455711364.964 29048: node=ec2-aws.example.com type=PROCTITLE msg=audit(1455711364.964:29048): proctitle=7375646F0064617465002B2573
544      12403    1455711364.964 29049: node=ec2-aws.example.com type=CRED_ACQ msg=audit(1455711364.964:29049): pid=12403 uid=0 auid=500 ses=544 msg='op=PAM:setcred grantors=pam_env,pam_unix acct="root" exe="/usr/bin/sudo" hostname=? addr=? terminal=? res=success'
544      12403    1455711364.964 29050: node=ec2-aws.example.com type=USER_START msg=audit(1455711364.964:29050): pid=12403 uid=0 auid=500 ses=544 msg='op=PAM:session_open grantors=pam_keyinit,pam_limits acct="root" exe="/usr/bin/sudo" hostname=? addr=? terminal=? res=success'
544      12404    1455711364.964 29051: node=ec2-aws.example.com type=SYSCALL msg=audit(1455711364.964:29051): arch=c000003e syscall=59 success=yes exit=0 a0=559d5520bc38 a1=559d55206648 a2=559d5520f010 a3=6 items=2 ppid=12403 pid=12404 auid=500 uid=0 gid=0 euid=0 suid=0 fsuid=0 egid=0 sgid=0 fsgid=0 tty=(none) ses=544 comm="date" exe="/bin/date" key="su-root-activity"
None     None     1455711364.964 29051: node=ec2-aws.example.com type=CWD msg=audit(1455711364.964:29051):  cwd="/home/ec2-user"
None     None     1455711364.964 29051: node=ec2-aws.example.com type=EXECVE msg=audit(1455711364.964:29051): argc=2 a0="date" a1="+%s"
None     None     1455711364.964 29051: node=ec2-aws.example.com type=PATH msg=audit(1455711364.964:29051): item=0 name="/bin/date" inode=399684 dev=ca:01 mode=0100755 ouid=0 ogid=0 rdev=00:00 nametype=NORMAL
None     None     1455711364.964 29051: node=ec2-aws.example.com type=PATH msg=audit(1455711364.964:29051): item=1 name="/lib64/ld-linux-x86-64.so.2" inode=396458 dev=ca:01 mode=0100755 ouid=0 ogid=0 rdev=00:00 nametype=NORMAL
None     None     1455711364.964 29051: node=ec2-aws.example.com type=PROCTITLE msg=audit(1455711364.964:29051): proctitle=64617465002B2573
544      12403    1455711364.964 29052: node=ec2-aws.example.com type=USER_END msg=audit(1455711364.964:29052): pid=12403 uid=0 auid=500 ses=544 msg='op=PAM:session_close grantors=pam_keyinit,pam_limits acct="root" exe="/usr/bin/sudo" hostname=? addr=? terminal=? res=success'
544      12403    1455711364.964 29053: node=ec2-aws.example.com type=CRED_DISP msg=audit(1455711364.964:29053): pid=12403 uid=0 auid=500 ses=544 msg='op=PAM:setcred grantors=pam_env,pam_unix acct="root" exe="/usr/bin/sudo" hostname=? addr=? terminal=? res=success'
544      12406    1455711369.968 29054: node=ec2-aws.example.com type=SYSCALL msg=audit(1455711369.968:29054): arch=c000003e syscall=59 success=yes exit=0 a0=170b270 a1=170c630 a2=1711970 a3=7ffc383e2520 items=2 ppid=12372 pid=12406 auid=500 uid=500 gid=500 euid=0 suid=0 fsuid=0 egid=500 sgid=500 fsgid=500 tty=(none) ses=544 comm="sudo" exe="/usr/bin/sudo" key="suid-root-exec"
None     None     1455711369.968 29054: node=ec2-aws.example.com type=BPRM_FCAPS msg=audit(1455711369.968:29054): fver=0 fp=0000000000000000 fi=0000000000000000 fe=0 old_pp=0000000000000000 old_pi=0000000000000000 old_pe=0000000000000000 new_pp=0000003fffffffff new_pi=0000000000000000 new_pe=0000003fffffffff
None     None     1455711369.968 29054: node=ec2-aws.example.com type=CWD msg=audit(1455711369.968:29054):  cwd="/home/ec2-user"
None     None     1455711369.968 29054: node=ec2-aws.example.com type=EXECVE msg=audit(1455711369.968:29054): argc=3 a0="sudo" a1="date" a2="+%s"
None     None     1455711369.968 29054: node=ec2-aws.example.com type=PATH msg=audit(1455711369.968:29054): item=0 name="/usr/bin/sudo" inode=407169 dev=ca:01 mode=0104111 ouid=0 ogid=0 rdev=00:00 nametype=NORMAL
None     None     1455711369.968 29054: node=ec2-aws.example.com type=PATH msg=audit(1455711369.968:29054): item=1 name="/lib64/ld-linux-x86-64.so.2" inode=396458 dev=ca:01 mode=0100755 ouid=0 ogid=0 rdev=00:00 nametype=NORMAL
None     None     1455711369.968 29054: node=ec2-aws.example.com type=PROCTITLE msg=audit(1455711369.968:29054): proctitle=7375646F0064617465002B2573
544      12406    1455711369.968 29055: node=ec2-aws.example.com type=USER_CMD msg=audit(1455711369.968:29055): pid=12406 uid=500 auid=500 ses=544 msg='cwd="/home/ec2-user" cmd=64617465202B2573 terminal=? res=success'
544      12406    1455711369.968 29056: node=ec2-aws.example.com type=SYSCALL msg=audit(1455711369.968:29056): arch=c000003e syscall=105 success=yes exit=0 a0=0 a1=7fffffffffffffff a2=55c18f027e56 a3=7fba917ad2e0 items=0 ppid=12372 pid=12406 auid=500 uid=0 gid=500 euid=0 suid=0 fsuid=0 egid=500 sgid=500 fsgid=500 tty=(none) ses=544 comm="sudo" exe="/usr/bin/sudo" key="su-root-activity"
None     None     1455711369.968 29056: node=ec2-aws.example.com type=PROCTITLE msg=audit(1455711369.968:29056): proctitle=7375646F0064617465002B2573
544      12406    1455711369.968 29057: node=ec2-aws.example.com type=CRED_ACQ msg=audit(1455711369.968:29057): pid=12406 uid=0 auid=500 ses=544 msg='op=PAM:setcred grantors=pam_env,pam_unix acct="root" exe="/usr/bin/sudo" hostname=? addr=? terminal=? res=success'
544      12406    1455711369.968 29058: node=ec2-aws.example.com type=USER_START msg=audit(1455711369.968:29058): pid=12406 uid=0 auid=500 ses=544 msg='op=PAM:session_open grantors=pam_keyinit,pam_limits acct="root" exe="/usr/bin/sudo" hostname=? addr=? terminal=? res=success'
544      12407    1455711369.968 29059: node=ec2-aws.example.com type=SYSCALL msg=audit(1455711369.968:29059): arch=c000003e syscall=59 success=yes exit=0 a0=55c18fe91c38 a1=55c18fe8c648 a2=55c18fe95010 a3=6 items=2 ppid=12406 pid=12407 auid=500 uid=0 gid=0 euid=0 suid=0 fsuid=0 egid=0 sgid=0 fsgid=0 tty=(none) ses=544 comm="date" exe="/bin/date" key="su-root-activity"
None     None     1455711369.968 29059: node=ec2-aws.example.com type=CWD msg=audit(1455711369.968:29059):  cwd="/home/ec2-user"
None     None     1455711369.968 29059: node=ec2-aws.example.com type=EXECVE msg=audit(1455711369.968:29059): argc=2 a0="date" a1="+%s"
None     None     1455711369.968 29059: node=ec2-aws.example.com type=PATH msg=audit(1455711369.968:29059): item=0 name="/bin/date" inode=399684 dev=ca:01 mode=0100755 ouid=0 ogid=0 rdev=00:00 nametype=NORMAL
None     None     1455711369.968 29059: node=ec2-aws.example.com type=PATH msg=audit(1455711369.968:29059): item=1 name="/lib64/ld-linux-x86-64.so.2" inode=396458 dev=ca:01 mode=0100755 ouid=0 ogid=0 rdev=00:00 nametype=NORMAL
None     None     1455711369.968 29059: node=ec2-aws.example.com type=PROCTITLE msg=audit(1455711369.968:29059): proctitle=64617465002B2573
544      12406    1455711369.968 29060: node=ec2-aws.example.com type=USER_END msg=audit(1455711369.968:29060): pid=12406 uid=0 auid=500 ses=544 msg='op=PAM:session_close grantors=pam_keyinit,pam_limits acct="root" exe="/usr/bin/sudo" hostname=? addr=? terminal=? res=success'
544      12406    1455711369.968 29061: node=ec2-aws.example.com type=CRED_DISP msg=audit(1455711369.968:29061): pid=12406 uid=0 auid=500 ses=544 msg='op=PAM:setcred grantors=pam_env,pam_unix acct="root" exe="/usr/bin/sudo" hostname=? addr=? terminal=? res=success'
544      12369    1455711371.516 29062: node=ec2-aws.example.com type=USER_END msg=audit(1455711371.516:29062): pid=12369 uid=0 auid=500 ses=544 msg='op=login id=500 exe="/usr/sbin/sshd" hostname=client.example.net addr=10.11.12.13 terminal=ssh res=success'
544      12369    1455711371.516 29063: node=ec2-aws.example.com type=USER_LOGOUT msg=audit(1455711371.516:29063): pid=12369 uid=0 auid=500 ses=544 msg='op=login id=500 exe="/usr/sbin/sshd" hostname=client.example.net addr=10.11.12.13 terminal=ssh res=success'
542      12299    1455711374.340 29064: node=ec2-aws.example.com type=CRYPTO_KEY_USER msg=audit(1455711374.340:29064): pid=12299 uid=0 auid=500 ses=542 msg='op=destroy kind=session fp=? direction=both spid=12301 suid=500 rport=56274 laddr=192.168.1.100 lport=22  exe="/usr/sbin/sshd" hostname=? addr=10.11.12.13 terminal=? res=success'
542      12299    1455711374.340 29065: node=ec2-aws.example.com type=CRYPTO_KEY_USER msg=audit(1455711374.340:29065): pid=12299 uid=0 auid=500 ses=542 msg='op=destroy kind=server fp=18:d5:59:1c:c8:88:5e:d1:1e:45:a4:3b:35:ad:e6:0c direction=? spid=12301 suid=500  exe="/usr/sbin/sshd" hostname=? addr=10.11.12.13 terminal=? res=success'
542      12299    1455711374.340 29066: node=ec2-aws.example.com type=USER_END msg=audit(1455711374.340:29066): pid=12299 uid=0 auid=500 ses=542 msg='op=PAM:session_close grantors=pam_selinux,pam_loginuid,pam_selinux,pam_namespace,pam_keyinit,pam_keyinit,pam_limits,pam_unix,pam_lastlog acct="ec2-user" exe="/usr/sbin/sshd" hostname=client.example.net addr=10.11.12.13 terminal=ssh res=success'
542      12299    1455711374.340 29067: node=ec2-aws.example.com type=CRED_DISP msg=audit(1455711374.340:29067): pid=12299 uid=0 auid=500 ses=542 msg='op=PAM:setcred grantors=pam_env,pam_unix acct="ec2-user" exe="/usr/sbin/sshd" hostname=client.example.net addr=10.11.12.13 terminal=ssh res=success'
542      12299    1455711374.340 29068: node=ec2-aws.example.com type=CRYPTO_KEY_USER msg=audit(1455711374.340:29068): pid=12299 uid=0 auid=500 ses=542 msg='op=destroy kind=server fp=70:a2:34:06:1d:e8:70:f3:ec:8d:15:a5:c9:f8:7c:f9 direction=? spid=12299 suid=0  exe="/usr/sbin/sshd" hostname=? addr=10.11.12.13 terminal=? res=success'
542      12299    1455711374.340 29069: node=ec2-aws.example.com type=CRYPTO_KEY_USER msg=audit(1455711374.340:29069): pid=12299 uid=0 auid=500 ses=542 msg='op=destroy kind=server fp=2a:3c:0f:33:24:f5:1b:d9:38:ae:fc:9a:b2:62:0c:65 direction=? spid=12299 suid=0  exe="/usr/sbin/sshd" hostname=? addr=10.11.12.13 terminal=? res=success'
542      12299    1455711374.340 29070: node=ec2-aws.example.com type=CRYPTO_KEY_USER msg=audit(1455711374.340:29070): pid=12299 uid=0 auid=500 ses=542 msg='op=destroy kind=server fp=18:d5:59:1c:c8:88:5e:d1:1e:45:a4:3b:35:ad:e6:0c direction=? spid=12299 suid=0  exe="/usr/sbin/sshd" hostname=? addr=10.11.12.13 terminal=? res=success'
-1       12411    1455711374.472 29071: node=ec2-aws.example.com type=CRYPTO_KEY_USER msg=audit(1455711374.472:29071): pid=12411 uid=0 auid=-1 ses=-1 msg='op=destroy kind=server fp=70:a2:34:06:1d:e8:70:f3:ec:8d:15:a5:c9:f8:7c:f9 direction=? spid=12411 suid=0  exe="/usr/sbin/sshd" hostname=? addr=10.11.12.13 terminal=? res=success'
-1       12411    1455711374.472 29072: node=ec2-aws.example.com type=CRYPTO_KEY_USER msg=audit(1455711374.472:29072): pid=12411 uid=0 auid=-1 ses=-1 msg='op=destroy kind=server fp=2a:3c:0f:33:24:f5:1b:d9:38:ae:fc:9a:b2:62:0c:65 direction=? spid=12411 suid=0  exe="/usr/sbin/sshd" hostname=? addr=10.11.12.13 terminal=? res=success'
-1       12411    1455711374.472 29073: node=ec2-aws.example.com type=CRYPTO_KEY_USER msg=audit(1455711374.472:29073): pid=12411 uid=0 auid=-1 ses=-1 msg='op=destroy kind=server fp=18:d5:59:1c:c8:88:5e:d1:1e:45:a4:3b:35:ad:e6:0c direction=? spid=12411 suid=0  exe="/usr/sbin/sshd" hostname=? addr=10.11.12.13 terminal=? res=success'
-1       12410    1455711374.560 29074: node=ec2-aws.example.com type=CRYPTO_SESSION msg=audit(1455711374.560:29074): pid=12410 uid=0 auid=-1 ses=-1 msg='op=start direction=from-server cipher=aes128-ctr ksize=128 mac=hmac-sha2-256 pfs=diffie-hellman-group1-sha1 spid=12411 suid=74 rport=56282 laddr=192.168.1.100 lport=22  exe="/usr/sbin/sshd" hostname=? addr=10.11.12.13 terminal=? res=success'
-1       12410    1455711374.560 29075: node=ec2-aws.example.com type=CRYPTO_SESSION msg=audit(1455711374.560:29075): pid=12410 uid=0 auid=-1 ses=-1 msg='op=start direction=from-client cipher=aes128-ctr ksize=128 mac=hmac-sha2-256 pfs=diffie-hellman-group1-sha1 spid=12411 suid=74 rport=56282 laddr=192.168.1.100 lport=22  exe="/usr/sbin/sshd" hostname=? addr=10.11.12.13 terminal=? res=success'
-1       12410    1455711375.040 29076: node=ec2-aws.example.com type=USER_AUTH msg=audit(1455711375.040:29076): pid=12410 uid=0 auid=-1 ses=-1 msg='op=pubkey_auth rport=56282 acct="ec2-user" exe="/usr/sbin/sshd" hostname=? addr=10.11.12.13 terminal=? res=success'
-1       12410    1455711375.040 29077: node=ec2-aws.example.com type=USER_AUTH msg=audit(1455711375.040:29077): pid=12410 uid=0 auid=-1 ses=-1 msg='op=key algo=ssh-rsa size=2048 fp=00:01:02:03:04:05:06:07:08:09:0a:0b:0c:0d:0e:0f rport=56282 acct="ec2-user" exe="/usr/sbin/sshd" hostname=? addr=10.11.12.13 terminal=? res=success'
-1       12410    1455711375.044 29078: node=ec2-aws.example.com type=USER_ACCT msg=audit(1455711375.044:29078): pid=12410 uid=0 auid=-1 ses=-1 msg='op=PAM:accounting grantors=pam_unix,pam_localuser acct="ec2-user" exe="/usr/sbin/sshd" hostname=client.example.net addr=10.11.12.13 terminal=ssh res=success'
-1       12410    1455711375.044 29079: node=ec2-aws.example.com type=CRYPTO_KEY_USER msg=audit(1455711375.044:29079): pid=12410 uid=0 auid=-1 ses=-1 msg='op=destroy kind=session fp=? direction=both spid=12411 suid=74 rport=56282 laddr=192.168.1.100 lport=22  exe="/usr/sbin/sshd" hostname=? addr=10.11.12.13 terminal=? res=success'
-1       12410    1455711375.044 29080: node=ec2-aws.example.com type=USER_AUTH msg=audit(1455711375.044:29080): pid=12410 uid=0 auid=-1 ses=-1 msg='op=success acct="ec2-user" exe="/usr/sbin/sshd" hostname=? addr=10.11.12.13 terminal=ssh res=success'
-1       12410    1455711375.044 29081: node=ec2-aws.example.com type=CRED_ACQ msg=audit(1455711375.044:29081): pid=12410 uid=0 auid=-1 ses=-1 msg='op=PAM:setcred grantors=pam_env,pam_unix acct="ec2-user" exe="/usr/sbin/sshd" hostname=client.example.net addr=10.11.12.13 terminal=ssh res=success'

545      12410    1455711375.044 29082: node=ec2-aws.example.com type=LOGIN msg=audit(1455711375.044:29082): pid=12410 uid=0 old-auid=-1 auid=500 old-ses=-1 ses=545 res=1
"""
