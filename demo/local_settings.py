from tlsauth import CertAuthority

TLS_CA=CertAuthority('/home/stef/tasks/tlsauth/CA/public/root.pem',
                     '/home/stef/tasks/tlsauth/CA/private/root.pem',
                     '/home/stef/tasks/tlsauth/CA/conf/serial',
                     '/home/stef/tasks/tlsauth/CA/dummy.pem',
                     'http://www.example.com/crl.pem',
                     '/home/stef/tasks/tlsauth/CA/incoming',
                     )
TLS_ADMINGROUPS=['CA admins']
TLS_SCRUTINIZER=None
TLS_BLINDSIGN=False
