/*
* Copyright (c) 1999 - 2005 NetGroup, Politecnico di Torino (Italy)
* Copyright (c) 2005 - 2006 CACE Technologies, Davis (California)
* All rights reserved.
*
* Redistribution and use in source and binary forms, with or without
* modification, are permitted provided that the following conditions
* are met:
*
* 1. Redistributions of source code must retain the above copyright
* notice, this list of conditions and the following disclaimer.
* 2. Redistributions in binary form must reproduce the above copyright
* notice, this list of conditions and the following disclaimer in the
* documentation and/or other materials provided with the distribution.
* 3. Neither the name of the Politecnico di Torino, CACE Technologies
* nor the names of its contributors may be used to endorse or promote
* products derived from this software without specific prior written
* permission.
*
* THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
* "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
* LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
* A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
* OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
* SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
* LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
* DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
* THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
* (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
* OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*
*/

#ifdef WIN32
/*
 * we do not want the warnings about the old deprecated and unsecure CRT functions
 * since these examples can be compiled under *nix as well
 */
//#define _CRT_SECURE_NO_WARNINGS
#define _WINSOCK_DEPRECATED_NO_WARNINGS

#include <pcap.h>
#include <stdlib.h>
#include <iostream>
#include <string>
#include <direct.h>

int gettimeofday(struct timeval* tv)
{
    union {
        long long ns100;
        FILETIME ft;
    } now;

    GetSystemTimeAsFileTime(&now.ft);
    tv->tv_usec = (long)((now.ns100 / 10LL) % 1000000LL);
    tv->tv_sec = (long)((now.ns100 - 116444736000000000LL) / 10000000LL);
    return (0);
}
#else
    #include <pcap.h>
    #include <stdlib.h>
    #include <iostream>
    #include <string>
    #include <cstdio>
    #include <cstring>
    #include <sys/stat.h>
    #include <arpa/inet.h>
    #define _snprintf snprintf
#endif

/* pcap file magic number */
#define PCAP_MAGIC          0xa1b2c3d4
/*
 * the length of ethernet packet header
 *  + destination address: 6 bytes
 *  + source address: 6 bytes
 *  + type: 2 bytes
 */
#define ETHPKT_HEADER_LEN 14

using namespace std;

/* 4-byte IP address */
typedef struct {
    u_char byte1;
    u_char byte2;
    u_char byte3;
    u_char byte4;
} ip_address_t;

/* 24-byte IPv4 header */
typedef struct {
    u_char  ver_ihl;        // Version (4 bits) + Internet header length (4 bits)
    u_char  tos;            // Type of service
    u_short tlen;           // Total length
    u_short identification; // Identification
    u_short flags_fo;       // Flags (3 bits) + Fragment offset (13 bits)
    u_char  ttl;            // Time to live
    u_char  proto;          // Protocol
    u_short crc;            // Header checksum
    ip_address_t saddr;     // Source address
    ip_address_t daddr;     // Destination address
    u_int   op_pad;         // Option + Padding
} ip_header_t;

/* 8-byte UDP header */
typedef struct {
    u_short sport;          // Source port
    u_short dport;          // Destination port
    u_short len;            // Datagram length
    u_short crc;            // Checksum
} udp_header_t;

int write_file_header(FILE* output_file) {
    /* 24(4+2+2+4+4+4+4)-byte pcap file header */
    // struct pcap_file_header {
    //     4   bpf_u_int32 magic;
    //     2   u_short version_major;
    //     2   u_short version_minor;
    //     4   bpf_int32 thiszone;     /* gmt to local correction */
    //     4   bpf_u_int32 sigfigs;    /* accuracy of timestamps */
    //     4   bpf_u_int32 snaplen;    /* max length saved portion of each pkt */
    //     4   bpf_u_int32 linktype;   /* data link type (LINKTYPE_*) */
    // };
    struct pcap_file_header fh;

    fh.magic = PCAP_MAGIC;

    fh.version_major = 2;
    fh.version_minor = 4;

    fh.thiszone = 0;

    fh.sigfigs = 0;
    fh.snaplen = 102400;

    fh.linktype = DLT_EN10MB;

    fwrite(&fh, sizeof(fh), 1, output_file);
    // printf("sizeof(global_header)=%d\n", sizeof(fh));
    return 0;
}

int getFileName(char* filename, int len, const char* veledyne_device_type, const char* name) {
    // find LiDAR's ip
    if(!strcmp(veledyne_device_type, "find_ip")) {
        #ifdef __WINDOWS_
            _snprintf(filename, len, ".\\pcap\\find_ip.pcap");
        #else
            _snprintf(filename, len, "./pcap/find_ip.pcap");
        #endif
    }
    else {
        struct timeval tp;
    #ifdef __WINDOWS_
        gettimeofday(&tp);
    #else
        struct timezone tz;
        gettimeofday(&tp, &tz);
    #endif
        struct tm *ltime;
        char timestr[32];

        time_t local_tv_sec;

        // convert the timestamp to readable format
        local_tv_sec = tp.tv_sec;
        ltime = localtime(&local_tv_sec);

        strftime(timestr, sizeof(timestr), "%x %X", ltime);
        printf("--------- Time: %s [usec]%ld ---------\n", timestr, tp.tv_usec);
        strftime(timestr, sizeof(timestr), "%Y%m%d%H%M%S", ltime);

    #ifdef __WINDOWS_
        _snprintf(filename, len, ".\\pcap\\%s_%s[%s].pcap", name, timestr, veledyne_device_type);
    #else
        _snprintf(filename, len, "/media/usb/pcap/%s_%s[%s].pcap", name, timestr, veledyne_device_type);
    #endif
    }


    return 0;
}

/* prototype of the packet handler */
void packet_handler(u_char *param, const struct pcap_pkthdr *header, const u_char *pkt_data);

int createDir(const char* DirName) {
#ifdef WIN32
    FILE* fp = NULL;
    char TempDir[200];
    memset(TempDir, '\0', sizeof(TempDir));
    sprintf(TempDir, DirName);
    strcat(TempDir, "\\");
    strcat(TempDir, ".temp.fortest");
    fp = fopen(TempDir, "w");
    if (!fp) {
        if (_mkdir(DirName) == 0)        {
            return 0;
        } else {
            return -1;              // can not make a dir;
        }
    } else {
        fclose(fp);
        remove(TempDir);
    }
    return 0;
#else
    if (mkdir(DirName, S_IRWXU | S_IRWXG | S_IROTH | S_IXOTH) == 0)        {
        return 0;
    } else {
        return -1;              // can not make a dir;
    }
#endif
}

int main(int argc, char** argv) {
    // printf("sizeof(ip_address_t)=%d\n", sizeof(ip_address_t));
    // printf("sizeof(ip_header_t)=%d\n", sizeof(ip_header_t));
    // printf("sizeof(udp_header_t)=%d\n", sizeof(udp_header_t));

    char velodyne_device_type[16] = "HDL32";
    char name[64] = "usi";
    if (argc > 1) {
        strcpy(velodyne_device_type, argv[1]);
        if(argc == 3) {
            strcpy(name, argv[2]);
        }
    }
    // printf("velodyne_device_type=%s, name=%s\n", velodyne_device_type, name);

    pcap_if_t *alldevs;
    pcap_if_t *d;
    int inum;
    int i = 0;
    pcap_t *adhandle;
    char errbuf[PCAP_ERRBUF_SIZE];
    char packet_filter[128];
    if(!strcmp(velodyne_device_type, "find_ip")) {
        strcpy(packet_filter, "");
    }
    else {
        // LiDAR's filter
        strcpy(packet_filter, "src 192.168.1.201 and port 2368");
        // imu's filter
        // char packet_filter[] = "src 195.0.0.29 and port 5001";
    }

    /* Retrieve the device list */
    if (pcap_findalldevs(&alldevs, errbuf) == -1) {
        fprintf(stderr, "Error in pcap_findalldevs: %s\n", errbuf);
        exit(1);
    }

    /* Always select eth0 */

    // /* Print the list */
    // for (d = alldevs; d; d = d->next) {
    //     printf("%d. %s", ++i, d->name);
    //     if (d->description)
    //         printf(" (%s)\n", d->description);
    //     else
    //         printf(" (No description available)\n");
    // }
    // if (i == 0) {
    //     printf("\nNo interfaces found! Make sure libpcap is installed and pcap driver is running.\n");
    //     return -1;
    // }
    //
    // printf("Enter the interface number (1-%d):", i);
    // scanf("%d", &inum);
    //
    // /* Check if the user specified a valid adapter */
    // if (inum < 1 || inum > i) {
    //     printf("\nAdapter number out of range.\n");
    //
    //     /* Free the device list */
    //     pcap_freealldevs(alldevs);
    //     return -1;
    // }
    //
    // /* Jump to the selected adapter */
    // for (d = alldevs, i = 0; i < inum - 1; d = d->next, i++);


#ifndef WIN32
    #define PCAP_OPENFLAG_PROMISCUOUS 0
#endif
    /* Open the adapter */
    if ((adhandle = pcap_open_live("eth0",//d->name                          // name of the device
                                   65536,                                   // portion of the packet to capture.
                                   // 65536 grants that the whole packet will be captured on all the MACs.
                                   PCAP_OPENFLAG_PROMISCUOUS,               // promiscuous mode (nonzero means promiscuous)
                                   1000,                                    // read timeout
                                   errbuf                                   // error buffer
                                  )) == NULL) {
        fprintf(stderr, "\nUnable to open the device %s\n", errbuf);
        /* Free the device list */
        pcap_freealldevs(alldevs);
        return -1;
    }

    /* check the link layer. we support only ethernet for simplicity. */
    if (pcap_datalink(adhandle) != DLT_EN10MB) {
        fprintf(stderr, "\nthis program works only on ethernet networks.\n");
        /* free the device list */
        pcap_freealldevs(alldevs);
        return -1;
    }

    bpf_u_int32 netmask;
    bpf_u_int32 net;
    bpf_program filter;

    pcap_lookupnet("eth0"/*d->name*/, &net, &netmask, errbuf);

    if (pcap_compile(adhandle, &filter, packet_filter, 1, 0xffffff) < 0) {
        fprintf(stderr, "\nUnable to compile the packet filter. Check the syntax.\n");
        /* Free the device list */
        pcap_freealldevs(alldevs);
        return -1;
    }

    // set the filter
    if (pcap_setfilter(adhandle, &filter) < 0) {
        fprintf(stderr, "\nError setting the filter.\n");
        /* Free the device list */
        pcap_freealldevs(alldevs);
        return -1;
    }

    FILE* output;
    // 16 + 64 + 32
    char filename[112];
    getFileName(filename, sizeof(filename), velodyne_device_type, name);

    createDir("/media/usb/pcap");
    output = fopen(filename, "wb");

    if (output == NULL) {
        printf("Fail to create pcap file......\n");
        return 0;
    }


    write_file_header(output);

    printf("\nlistening on %s... Press Ctrl+C to stop...\n", "eth0"/*d->name*/);

    /* At this point, we don't need any more the device list. Free it */
    pcap_freealldevs(alldevs);

    /* start the capture */
#ifdef WIN32
    pcap_loop(adhandle, 0, packet_handler, reinterpret_cast<u_char*>(output));
#else
    pcap_loop(adhandle, 0, packet_handler, reinterpret_cast<u_char*>(output));
#endif

    fclose(output);

    return 0;
}

/* Callback function invoked by libpcap for every incoming packet */
static unsigned int flush_counter = 0;
#define FLUSH_PKT_NUM 1600
void packet_handler(u_char* param, const struct pcap_pkthdr* header, const u_char* pkt_data) {
    flush_counter++;

    struct tm* ltime;
    char timestr[16];
    ip_header_t* ih;
    udp_header_t* uh;
    u_int ip_len;
    u_short sport, dport;
    time_t local_tv_sec;

    // unused parameter
    FILE* output = reinterpret_cast<FILE*>(param);
    fwrite(header, sizeof(pcap_pkthdr), 1, output);
    // printf("sizeof(local_header)=%d\n", sizeof(pcap_pkthdr));
    fwrite(pkt_data, header->caplen, 1, output);

    // flush the file buffer every FLUSH_PKT_NUM packets to avoid unexpected dump
    if(flush_counter == FLUSH_PKT_NUM){
        fflush(output);
        flush_counter = 0;
    }

    /* retireve the position of the ip header */
    ih = (ip_header_t *)(pkt_data + ETHPKT_HEADER_LEN);

    /* retireve the position of the udp header */
    ip_len = (ih->ver_ihl & 0xf) * 4;
    uh = (udp_header_t *)((u_char*)ih + ip_len);

    /* convert from network byte order to host byte order */
    sport = ntohs(uh->sport);
    dport = ntohs(uh->dport);

    /* print ip addresses and udp ports */
    if(flush_counter < 1){
        /* convert the timestamp to readable format */
        local_tv_sec = header->ts.tv_sec;
        ltime = localtime(&local_tv_sec);
        strftime(timestr, sizeof timestr, "%H:%M:%S", ltime);

        /* print timestamp and length of the packet */
        //printf("%s.%6ld len:%d headlen:%lu ", timestr, header->ts.tv_usec, header->len, sizeof(pcap_pkthdr));

        printf(" IP: %d.%d.%d.%d:%d -> %d.%d.%d.%d:%d [%s.%06ld]\n",
         ih->saddr.byte1,
         ih->saddr.byte2,
         ih->saddr.byte3,
         ih->saddr.byte4,

         sport,

         ih->daddr.byte1,
         ih->daddr.byte2,
         ih->daddr.byte3,
         ih->daddr.byte4,

         dport,

         timestr, header->ts.tv_usec);
    }
}
