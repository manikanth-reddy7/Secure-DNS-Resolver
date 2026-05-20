import time
import mydig as dns_r
import dns.resolver as dr
import dns.message as dm
import dns.query as dq
import dns.rdatatype
import numpy as np
import matplotlib.pyplot as plt

google_public_dns='8.8.8.8'
dns_r.option='A'
top_sites=['Google.com','Youtube.com','Facebook.com','Baidu.com','Yahoo.com','Wikipedia.org',
           'Google.co.in','Tmall.com','Qq.com','Amazon.com','Sohu.com','Google.co.jp','Taobao.com',
           'Live.com','Vk.com','Twitter.com','360.cn','Instagram.com','Linkedin.com','Yahoo.co.jp',
           'Sina.com.cn','Jd.com','Google.de','Reddit.com','Google.co.uk']
avg_time_to_resolve_mydig=[]
avg_time_to_resolve_local=[]
avg_time_to_resolve_gpd=[]

root_server_ip = ['198.41.0.4', '192.228.79.201', '192.33.4.12', '199.7.91.13',
                  '192.203.230.10', '192.5.5.241', '192.112.36.4', '198.97.190.53',
                  '192.36.148.17', '192.58.128.30', '193.0.14.129', '199.7.83.42',
                  '202.12.27.33']


def main():
    for site_ind in range(25):
        # dns_r.user_input=top_sites[site_ind]
        print(top_sites[site_ind])
        start_time = time.time()
        for count in range(10):
            dns_r.resolve(top_sites[site_ind], dns.rdatatype.A, root_server_ip[0])
        running_time = (time.time() - start_time)
        avg_run_time=running_time/10
        avg_time_to_resolve_mydig.append(avg_run_time)
    print(avg_time_to_resolve_mydig)
    #
    # for site_ind in range(25):
    #     print(top_sites[site_ind])
    #     start_time = time.time()
    #     resolver = dns.resolver.Resolver(configure=False)
    #     resolver.nameservers = ['130.245.9.242']
    #     for count in range(10):
    #         response=dr.query(top_sites[site_ind], 'A')
    #     running_time = (time.time() - start_time)
    #     avg_run_time = running_time / 10
    #     avg_time_to_resolve_local.append(avg_run_time)
    # print(avg_time_to_resolve_local)
    #
    # for site_ind in range(25):
    #     print(top_sites[site_ind])
    #     start_time = time.time()
    #     resolver = dns.resolver.Resolver(configure=False)
    #     resolver.nameservers = ['8.8.8.8']
    #     for count in range(10):
    #         # query = dm.make_query(top_sites[site_ind], 1)
    #         response = dr.query(top_sites[site_ind], 'A')
    #     running_time = (time.time() - start_time)
    #     avg_run_time = running_time / 10
    #     avg_time_to_resolve_gpd.append(avg_run_time)
    # print(avg_time_to_resolve_gpd)

    # avg_time_to_resolve_mydig = [0.05369210243225098, 0.050852203369140626, 0.03372499942779541, 1.2353032112121582,
    #                              0.047919607162475585, 0.07413837909698487, 0.1248317003250122, 0.09925298690795899,
    #                              1.8292111158370972, 0.03788919448852539, 2.020819592475891, 0.2679563045501709,
    #                              0.10062210559844971, 0.08391189575195312, 0.4243782997131348, 0.04001169204711914,
    #                              4.0412641048431395, 0.28450589179992675, 0.03630938529968262, 0.35335769653320315,
    #                              1.6275480031967162, 0.3264401912689209, 0.1873543977737427, 0.04003291130065918,
    #                              0.1103438138961792]

    avg_time_to_resolve_local = [0.021610593795776366, 0.01812160015106201, 0.00881190299987793, 0.010378003120422363,
                                 0.009561920166015625, 0.023015093803405762, 0.019799113273620605, 0.033954191207885745,
                                 0.008649396896362304, 0.010518288612365723, 0.013028502464294434, 0.024208998680114745,
                                 0.010724616050720216, 0.010894417762756348, 0.00942850112915039, 0.008534717559814452,
                                 0.07715821266174316, 0.012785506248474122, 0.010097908973693847, 0.01973280906677246,
                                 0.08702969551086426, 0.12439279556274414, 0.02266969680786133, 0.009807181358337403,
                                 0.024155402183532716]

    avg_time_to_resolve_gpd = [0.020658493041992188, 0.026722812652587892, 0.009758400917053222, 0.01426708698272705,
                               0.00950169563293457, 0.020901918411254883, 0.016964483261108398, 0.021261382102966308,
                               0.010713410377502442, 0.009293293952941895, 0.008844709396362305, 0.01957359313964844,
                               0.00914781093597412, 0.010693502426147462, 0.008390212059020996, 0.61961989402771,
                               0.020069193840026856, 0.01243278980255127, 0.008242392539978027, 0.023051190376281738,
                               0.019893693923950195, 0.06203300952911377, 0.020854496955871583, 0.009482908248901366,
                               0.024856305122375487]


    avg_time_to_resolve_local_np=np.array(avg_time_to_resolve_local)
    avg_time_to_resolve_mydig_np=np.array(avg_time_to_resolve_mydig)
    avg_time_to_resolve_gpd_np=np.array(avg_time_to_resolve_gpd)
    sortd_avg_time_to_resolve_local_np=np.sort(avg_time_to_resolve_local_np)
    sortd_avg_time_to_resolve_mydig_np=np.sort(avg_time_to_resolve_mydig_np)
    sortd_avg_time_to_resolve_gpd_np = np.sort(avg_time_to_resolve_gpd_np)
    x = 1. * np.arange(len(sortd_avg_time_to_resolve_local_np)) / (len(sortd_avg_time_to_resolve_local_np) - 1)
    y = 1. * np.arange(len(sortd_avg_time_to_resolve_mydig_np)) / (len(sortd_avg_time_to_resolve_mydig_np) - 1)
    z = 1. * np.arange(len(sortd_avg_time_to_resolve_gpd_np)) / (len(sortd_avg_time_to_resolve_gpd_np) - 1)

    fig=plt.figure(figsize=(10,10), dpi=100)
    plt.plot(sortd_avg_time_to_resolve_mydig_np, y, c='r', linewidth=2.5, label='Mydig')
    plt.plot(sortd_avg_time_to_resolve_local_np, x, c='g', linewidth=2.5,label='Local DNS Resolver')
    plt.plot(sortd_avg_time_to_resolve_gpd_np, z, c='b', linewidth=2.5,label='Google Public DNS')
    plt.legend(loc='lower right')
    plt.xlabel('$time (seconds)$',fontsize=20)
    fig.suptitle('Cumulative distribution function')
    plt.show()
    plt.savefig('plot.png')

if __name__=='__main__':
    main()