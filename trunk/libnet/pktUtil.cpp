#include <Python.h>
#include <string>
#include <vector>
#include <pcap.h>

#ifdef WIN32
#include <win32/libnet.h>
#else
#include <libnet.h>
#endif

using namespace std;

int main()
{

    printf("%d",sizeof(int8_t));
    return 0;
}


PyObject* ListDevices( PyObject* self , PyObject * args )
{
    if ( !PyArg_ParseTuple(args , "") )
        return NULL;

    pcap_if_t *alldevs;
    char pcap_errbuf[PCAP_ERRBUF_SIZE]={0};
    if ( pcap_findalldevs(&alldevs , pcap_errbuf) == -1 )
        return NULL;

    PyObject * pList = PyList_New(0);
    pcap_if_t *pDevIndex = alldevs;
    for (  ; pDevIndex ; pDevIndex = pDevIndex->next )
    {
        PyList_Insert( pList , 0 , Py_BuildValue("s" ,pDevIndex->name ));
    }

    return pList;
}

PyObject * LibnetInit( PyObject * self , PyObject * args )
{

    char * device_name = NULL;
    if ( !PyArg_ParseTuple(args , "s", &device_name ) )
        return NULL;

    char libnet_errbuf[LIBNET_ERRBUF_SIZE] = {0};
    libnet_t * pLibNet = NULL;
    pLibNet = libnet_init( LIBNET_LINK , device_name , libnet_errbuf );
    return Py_BuildValue("i",pLibNet);

}

PyObject * SendSysLog( PyObject * self , PyObject * args )
{
    char * des_mac = NULL;
    char * src_mac = NULL;
    char * des_ip = 0;
    char * src_ip = 0;
    char * payload = NULL;
    libnet_t * pLibNet = NULL;
    

    if ( !PyArg_ParseTuple(args , "isssss" ,
            &pLibNet,
            &des_mac,
            &src_mac,
            &des_ip,
            &src_ip,
            &payload ) )
        return NULL;

    int payload_length = strlen(payload);

    libnet_ptag_t udp_ret = 0;
    udp_ret = libnet_build_udp( 
        1024,
        514,
        payload_length + LIBNET_UDP_H,
        0,
        (unsigned char*)payload,
        payload_length,
        pLibNet,
        0 );

    if ( -1 == udp_ret )
    {
        return NULL;
    }


    libnet_ptag_t ip_ret = 0;
    ip_ret = libnet_build_ipv4( 
        LIBNET_IPV4_H + LIBNET_UDP_H + payload_length,
        0,
        libnet_get_prand(LIBNET_PR16),
        IP_DF,
        0,
        IPPROTO_UDP,
        0 ,
        inet_addr(src_ip),
        inet_addr(des_ip),
        NULL,
        0,
        pLibNet,
        0 );

    if ( -1 == ip_ret )
    {
        return NULL;
    }

    libnet_ptag_t ethernet_ret = 0;
    
    int mac_convert_len = 0;
    unsigned char *des_mac_c = libnet_hex_aton( (int8_t*)des_mac , &mac_convert_len );
    unsigned char *src_mac_c = libnet_hex_aton( (int8_t*)src_mac , &mac_convert_len );

    ethernet_ret = libnet_build_ethernet(
            des_mac_c,
            src_mac_c,
            ETHERTYPE_IP,
            NULL,
            0,
            pLibNet,
            0 );

    if ( -1 == ethernet_ret )
    {
        free( des_mac_c );
        free( src_mac_c );
        return NULL;
    }


    int write_ret = libnet_write(pLibNet);
    libnet_clear_packet( pLibNet );

    free( des_mac_c );
    free( src_mac_c );


    return Py_BuildValue("i",write_ret);


}

PyObject * LibnetDestroy( PyObject * self , PyObject * args )
{
    libnet_t * pLibNet = NULL;
    if ( !PyArg_ParseTuple(args , "i" , &pLibNet ) )
        return NULL;

    libnet_destroy( pLibNet );

    return Py_BuildValue("i",1);
}

static PyMethodDef exampleMethods[] = 
{
    {"ListDevices", ListDevices, METH_VARARGS},
    {"LibnetInit", LibnetInit, METH_VARARGS},
    {"SendSysLog", SendSysLog, METH_VARARGS},
    {"LibnetDestroy", LibnetDestroy, METH_VARARGS},
    {NULL, NULL}
};

extern "C" void initpktUtil() 
{
  PyObject* m;
  m = Py_InitModule("pktUtil", exampleMethods);
}

