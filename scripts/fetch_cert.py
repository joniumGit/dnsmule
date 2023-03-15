if __name__ == '__main__':
    import sys
    import ssl
    import socket

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as raw_socket:
        with ctx.wrap_socket(raw_socket, do_handshake_on_connect=True) as s:
            s.connect((sys.argv[1], 443))
            with open('cert-tuples.txt', 'w') as f:
                f.write(repr(s.getpeercert(binary_form=False)))
            with open('cert-pem.txt', 'w') as f:
                f.write(ssl.DER_cert_to_PEM_cert(s.getpeercert(binary_form=True)))
