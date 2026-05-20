from __future__ import print_function
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
                # We found the desired result, so return it
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
            servers += root_server_ip

        for server in servers:
            for name in name_list:
                if changed:
                    ret = resolve(name, query_type('A'), server)
                else:
                    ret = resolve(name, rdtype, server)
                if ret is not None:
                    if changed:
                        ret = resolve(qname, rdtype, ret[0])
                    return ret

    return None


def main(argv):
    # Process user input
    s_query = argv[0]       # Website URL
    s_query_type = argv[1]  # Record type: A, NS, or MX

    qtype = query_type(s_query_type)
    for server in root_server_ip:
        ret = resolve(s_query, qtype, server)
        if ret is not None:
            print(ret)
            break


if __name__ == "__main__":
    main(sys.argv[1:])
