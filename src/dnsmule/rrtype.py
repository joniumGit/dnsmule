from enum import IntEnum
from typing import Any, Union


class RRType(IntEnum):

    @staticmethod
    def _check_range(value: int):
        try:
            if not 0 <= value <= 65535:
                raise ValueError('Value our of bounds for RR [0, 65535]', value)
        except TypeError as e:
            raise ValueError('Value could not be compared', value) from e

    @classmethod
    def to_text(cls, value: Union['RRType', int]) -> str:
        RRType._check_range(value)
        for k, v in cls.__members__.items():
            if v == value:
                return k
        return str(value)

    @classmethod
    def from_text(cls, value: str) -> Union['RRType', int]:
        value = value.upper()
        for v in cls.__members__.keys():
            # Could be str derivative with different hash
            if value == v:
                return cls.__members__[v]
        return cls.make(int(value))

    @classmethod
    def make(cls, value: int):
        RRType._check_range(value)
        for v in cls.__members__.values():
            if v == value:
                return v
        return value

    @classmethod
    def from_any(cls, value: Union[int, str, Any]) -> Union['RRType', int]:
        if isinstance(value, int):
            return cls.make(value)
        else:
            return cls.from_text(str(value))

    def __str__(self):
        return RRType.to_text(self)

    def __repr__(self):
        return self.__str__()

    A: int = 1
    """
    a host address
    """

    NS: int = 2
    """
    an authoritative name server
    """

    MD: int = 3
    """
    a mail destination (OBSOLETE - use MX)
    """

    MF: int = 4
    """
    a mail forwarder (OBSOLETE - use MX)
    """

    CNAME: int = 5
    """
    the canonical name for an alias
    """

    SOA: int = 6
    """
    marks the start of a zone of authority
    """

    MB: int = 7
    """
    a mailbox domain name (EXPERIMENTAL)
    """

    MG: int = 8
    """
    a mail group member (EXPERIMENTAL)
    """

    MR: int = 9
    """
    a mail rename domain name (EXPERIMENTAL)
    """

    NULL: int = 10
    """
    a null RR (EXPERIMENTAL)
    """

    WKS: int = 11
    """
    a well known service description
    """

    PTR: int = 12
    """
    a domain name pointer
    """

    HINFO: int = 13
    """
    host information
    """

    MINFO: int = 14
    """
    mailbox or mail list information
    """

    MX: int = 15
    """
    mail exchange
    """

    TXT: int = 16
    """
    text strings
    """

    RP: int = 17
    """
    for Responsible Person
    """

    AFSDB: int = 18
    """
    for AFS Data Base location
    """

    X25: int = 19
    """
    for X.25 PSDN address
    """

    ISDN: int = 20
    """
    for ISDN address
    """

    RT: int = 21
    """
    for Route Through
    """

    NSAP: int = 22
    """
    for NSAP address, NSAP style A record (DEPRECATED)
    """

    NSAP_PTR: int = 23
    """
    for domain name pointer, NSAP style (DEPRECATED)
    """

    SIG: int = 24
    """
    for security signature
    """

    KEY: int = 25
    """
    for security key
    """

    PX: int = 26
    """
    X.400 mail mapping information
    """

    GPOS: int = 27
    """
    Geographical Position
    """

    AAAA: int = 28
    """
    IP6 Address
    """

    LOC: int = 29
    """
    Location Information
    """

    NXT: int = 30
    """
    Next Domain (OBSOLETE)
    """

    EID: int = 31
    """
    Endpoint Identifier
    """

    NIMLOC: int = 32
    """
    Nimrod Locator
    """

    SRV: int = 33
    """
    Server Selection
    """

    ATMA: int = 34
    """
    ATM Address
    """

    NAPTR: int = 35
    """
    Naming Authority Pointer
    """

    KX: int = 36
    """
    Key Exchanger
    """

    CERT: int = 37
    """
    CERT
    """

    A6: int = 38
    """
    A6 (OBSOLETE - use AAAA)
    """

    DNAME: int = 39
    """
    DNAME
    """

    SINK: int = 40
    """
    SINK
    """

    OPT: int = 41
    """
    OPT
    """

    APL: int = 42
    """
    APL
    """

    DS: int = 43
    """
    Delegation Signer
    """

    SSHFP: int = 44
    """
    SSH Key Fingerprint
    """

    IPSECKEY: int = 45
    """
    IPSECKEY
    """

    RRSIG: int = 46
    """
    RRSIG
    """

    NSEC: int = 47
    """
    NSEC
    """

    DNSKEY: int = 48
    """
    DNSKEY
    """

    DHCID: int = 49
    """
    DHCID
    """

    NSEC3: int = 50
    """
    NSEC3
    """

    NSEC3PARAM: int = 51
    """
    NSEC3PARAM
    """

    TLSA: int = 52
    """
    TLSA
    """

    SMIMEA: int = 53
    """
    S/MIME cert association
    """

    UNASSIGNED: int = 54
    """

    """

    HIP: int = 55
    """
    Host Identity Protocol
    """

    NINFO: int = 56
    """
    NINFO
    """

    RKEY: int = 57
    """
    RKEY
    """

    TALINK: int = 58
    """
    Trust Anchor LINK
    """

    CDS: int = 59
    """
    Child DS
    """

    CDNSKEY: int = 60
    """
    DNSKEY(s) the Child wants reflected in DS
    """

    OPENPGPKEY: int = 61
    """
    OpenPGP Key
    """

    CSYNC: int = 62
    """
    Child-To-Parent Synchronization
    """

    ZONEMD: int = 63
    """
    Message Digest Over Zone Data
    """

    SVCB: int = 64
    """
    General-purpose service binding
    """

    HTTPS: int = 65
    """
    SVCB-compatible type for use with HTTP
    """

    SPF: int = 99
    """

    """

    UINFO: int = 100
    """

    """

    UID: int = 101
    """

    """

    GID: int = 102
    """

    """

    UNSPEC: int = 103
    """

    """

    NID: int = 104
    """

    """

    L32: int = 105
    """

    """

    L64: int = 106
    """

    """

    LP: int = 107
    """

    """

    EUI48: int = 108
    """
    an EUI-48 address
    """

    EUI64: int = 109
    """
    an EUI-64 address
    """

    TKEY: int = 249
    """
    Transaction Key
    """

    TSIG: int = 250
    """
    Transaction Signature
    """

    IXFR: int = 251
    """
    incremental transfer
    """

    AXFR: int = 252
    """
    transfer of an entire zone
    """

    MAILB: int = 253
    """
    mailbox-related RRs (MB, MG or MR)
    """

    MAILA: int = 254
    """
    mail agent RRs (OBSOLETE - see MX)
    """

    ANY: int = 255
    """
    A request for some or all records the server has available
    """

    URI: int = 256
    """
    URI
    """

    CAA: int = 257
    """
    Certification Authority Restriction
    """

    AVC: int = 258
    """
    Application Visibility and Control
    """

    DOA: int = 259
    """
    Digital Object Architecture
    """

    AMTRELAY: int = 260
    """
    Automatic Multicast Tunneling Relay
    """

    RESINFO: int = 261
    """
    Resolver Information as Key/Value Pairs
    """

    TA: int = 32768
    """
    DNSSEC Trust Authorities
    """

    DLV: int = 32769
    """
    DNSSEC Lookaside Validation (OBSOLETE)
    """


__all__ = [
    'RRType',
]
