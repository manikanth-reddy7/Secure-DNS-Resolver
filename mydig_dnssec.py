from __future__ import print_function
import warnings
warnings.filterwarnings("ignore")
import time
import datetime
import math
import sys
import dns.resolver
import copy
import dns.dnssec
import dns.message
import dns.rdataclass
import dns.rdatatype
import dns.query

root_server = ['a.root-servers.net', 'b.root-servers.net', 'c.root-servers.net',
               'd.root-servers.net', 'e.root-servers.net', 'f.root-servers.net',
               'g.root-servers.net', 'h.root-servers.net', 'i.root-servers.net',
               'j.root-servers.net', 'k.root-servers.net', 'l.root-servers.net',
               'm.root-servers.net']

root_server_ip = ['198.41.0.4', '192.228.79.201', '192.33.4.12', '199.7.91.13',
                  '192.203.230.10', '192.5.5.241', '192.112.36.4', '198.97.190.53',
                  '192.36.148.17', '192.58.128.30', '193.0.14.129', '199.7.83.42',
                  '202.12.27.33']

ANSWER = 1
AUTHORITY = 2
ADDITIONAL = 3

def query_type(s_query):
    if s_query == 'A':
        return dns.rdatatype.A
    if s_query == 'NS':
        return dns.rdatatype.NS
    if s_query == 'MX':
        return dns.rdatatype.MX

    return dns.rdatatype.CNAME


# Get a list of items like IP addresses, NS, or MX records
def get_result(items, section_type, rdtype):
    ret = []
    for item in items:
        if section_type == ANSWER:
            if item.rdtype != rdtype:
                continue
            if rdtype == query_type('NS') or rdtype == query_type('CNAME'):
                ret.append(str(item.target))
            elif rdtype == query_type('A'):
                ret.append(str(item.address))
            elif rdtype == query_type('MX'):
                ret.append(str(item.exchange))
        elif section_type == AUTHORITY:
            ret.append(str(item.target))
        elif section_type == ADDITIONAL:
            if item.rdtype == query_type('A'):
                ret.append(str(item.address))

    return ret

# Find the Key Signing Key (KSK) in a DNS section
def get_ksk(section_list):
    for section in section_list:
        for item in section.items:
            if item.flags == 257:   # KSK flag
                return item
    return None


# Find the Delegation Signer (DS) record in a DNS section
def get_ds(section_list):
    for section in section_list:
        for item in section.items:
            if item.rdtype == 43:   # DS type
                return item
    return None


# Extract the domain name from a section
def get_current_name(section_list):
    for section in section_list:
        return section.name


# Get the hashing algorithm name from its type ID
def get_algorithm_for_digest(digest_type):
    if digest_type == 1:
        return 'SHA1'
    if digest_type == 2:
        return 'SHA256'
    if digest_type == 4:
        return 'SHA384'
    return None


def resolve(name, rdtype, server):      # Take the website name, record type, and server to query
    try:
        qname = dns.name.from_text(str(name))
        query = dns.message.make_query(qname, rdtype)
        response = dns.query.udp(query, server, 2.0)
    except:
        return None

    # Check if the query was successful without errors
    if response.rcode() == dns.rcode.NOERROR:
        answer = response.answer
        ret = []
        cname_list = []

        # If there's an answer, we found the IP address we are looking for
        if len(answer) != 0:
            for ans in answer:
                # Get all IPs if there are multiple addresses available
                ret += get_result(ans.items, ANSWER, rdtype)
                
                # Sometimes a server only has a canonical name (CNAME) instead of the IP.
                # In that case, we keep track of it so we can restart our search from the root.
                cname_list += get_result(ans.items, ANSWER, query_type('CNAME'))

            if len(ret) != 0:
                # We found the desired result, return it after doing DNSSEC validation
                
                # Verify DNSSEC: Check the DNS keys, resource records, and signatures
                # Prepare queries for the records and keys
                q = dns.message.make_query(qname, dns.rdatatype.A, want_dnssec=True)
                q_sec = dns.message.make_query(qname, dns.rdatatype.DNSKEY, want_dnssec=True)
                
                # Send the queries
                r = dns.query.udp(q, server)
                r_sec = dns.query.udp(q_sec, server)

                a = r.answer
                a_sec = r_sec.answer
                
                # Check if the server actually supports DNSSEC
                if len(a) == 0 or len(a_sec) == 0:
                    print('DNSSEC not supported')
                    return 'failed'

                # Validate the resource records and keys
                try:
                    dns.dnssec.validate(a[0], a[1], {qname: a_sec[0]})
                    dns.dnssec.validate(a_sec[0], a_sec[1], {qname: a_sec[0]})
                except:
                    print('DNSSec verification failed')
                    return 'failed'
                return ret

            # If we only needed the canonical name and we have it, we can return it here
            if len(cname_list) != 0:
                if rdtype == query_type('NS') or rdtype == query_type('MX'):
                    return cname_list

        # If we didn't find the final answer, we need to dig further.
        # We can either use a canonical name to restart from the root,
        # use an IP from the additional section, or fetch the A record from the authority section.
        name_list = []
        servers = []
        changed = False
        if len(cname_list) != 0:
            name_list += cname_list
            servers += root_server_ip
        elif len(response.additional) != 0:
            name_list.append(str(qname))
            for i in range(len(response.additional)):
                servers += get_result(response.additional[i].items, ADDITIONAL, None)
        else:
            changed = True
            for i in range(len(response.authority)):
                name_list += get_result(response.authority[i].items, AUTHORITY, None)
            if rdtype == query_type('NS'):
                return name_list
            servers += root_server_ip

        for next_server in servers:
            for next_name in name_list:
                if changed:
                    ret = resolve(next_name, query_type('A'), next_server)
                else:
                    # Implement the chain of trust for DNSSEC
                    # We need to securely verify the child server using the parent server's DS record
                    current_name = str(get_current_name(response.authority))
                    rrset_query = dns.message.make_query(current_name, dns.rdatatype.A, want_dnssec=True)
                    ds_query = dns.message.make_query(current_name, dns.rdatatype.DS, want_dnssec=True)
                    dnskey_query_child = dns.message.make_query(current_name, dns.rdatatype.DNSKEY, want_dnssec=True)

                    rrset_response = dns.query.tcp(rrset_query, server)
                    ds_response = dns.query.tcp(ds_query, server)
                    dnskey_response_child = dns.query.tcp(dnskey_query_child, next_server)

                    # Get the stored DS value from the parent and the KSK from the child
                    ds = get_ds(ds_response.answer)
                    child_ksk = get_ksk(dnskey_response_child.answer)

                    # Ensure both values exist to proceed with validation
                    if (ds is not None) and (child_ksk is not None):
                        # Determine the hashing algorithm
                        algorithm = get_algorithm_for_digest(ds.digest_type)
                        
                        # Calculate the child's DS value and match it against the parent's DS value
                        child_ds = dns.dnssec.make_ds(current_name, child_ksk, algorithm)
                        
                        if ds.digest == child_ds.digest:
                            try:
                                # Validate keys for this level
                                dns.dnssec.validate(dnskey_response_child.answer[0], dnskey_response_child.answer[1],
                                                    {dns.name.from_text(current_name): dnskey_response_child.answer[0]})
                            except:
                                print('DNSSec verification failed')
                                return "failed"
                        else:
                            print('DNSSec verification failed')
                            return "failed"
                    else:
                        print('DNSSEC not supported')
                        return "failed"

                    # Validation passed, go to the next level
                    ret = resolve(next_name, rdtype, next_server)
                if ret is not None:
                    if changed and ret != 'failed':
                        ret = resolve(qname, rdtype, ret[0])
                    return ret
    return None


def main(argv):
    # Process user input
    s_query = argv[0]       # Website URL
    for server in root_server_ip:
        ret = resolve(s_query, dns.rdatatype.A, server)
        if ret is not None:
            if ret != 'failed':
                print(ret)
            break


if __name__ == "__main__":
    main(sys.argv[1:])
