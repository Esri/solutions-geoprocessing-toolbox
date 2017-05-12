# -*- coding: utf-8 -*-
import os.path
import urllib2
import xml.etree.ElementTree as et


XLINK_NAMESPACE = "http://www.w3.org/1999/xlink"
THREDDS_NAMESPACE = \
    "http://www.unidata.ucar.edu/namespaces/thredds/InvCatalog/v1.0"


def universal_name(
        name,
        namespace=THREDDS_NAMESPACE):
    """
    Return a qualified *name* formatted as a universal name using *namespace*.

    See also: http://effbot.org/zone/element-namespaces.htm
    """
    return "{{{namespace}}}{name}".format(namespace=namespace, name=name)


def construct_dataset_url(
        request,
        service_base,
        url):
    """
    Construct a url to a dataset, given a *catalog request*, *service_base*
    and *url*.

    It is assumed that *url* is relative to *service_base*.
    """
    return "{}://{}{}{}".format(request.get_type(), request.get_host(),
        service_base, url)


def construct_catalog_url(
        request,
        url):
    """
    Construct a *url* that is referenced by *request*.

    It is assumed that *url* is relative to *request*.

    See also: http://www.unidata.ucar.edu/Projects/THREDDS/tech/catalog/InvCatalogSpec.html

    TODO: Update to allow *url* to be absolute.
    """
    return "{}/{}".format(os.path.split(request.get_full_url())[0], url)


def urls_to_datasets(
        url_to_catalog):
    """
    Open catalog XML pointed to by *url_to_catalog* and returns a list with
    urls to opendap served datasets present in the catalog.

    This function opens nested catalogs, pointed to by catalogRef elements,
    also.
    """
    request = urllib2.Request(url_to_catalog)
    catalog = urllib2.urlopen(request).read()
    root = et.fromstring(catalog)
    result = []

    opendap_service = None
    for service_name in ["ncdods", "opendap"]:
        if opendap_service is None:
            opendap_service = \
                root.find("{service}/{service}[@name=\"{name}\"]".format(
                    service=universal_name("service"), name=service_name))

    if not opendap_service is None:
        # Information about the opendap service is needed to be able to
        # create urls.
        service_base = opendap_service.attrib["base"]

        # Select all dataset elements that have an urlPath attribute.
        for dataset in root.findall(".//{}[@urlPath]".format(universal_name(
                "dataset"))):
            result.append(construct_dataset_url(request, service_base,
                dataset.attrib["urlPath"]))

    # Select all catalogRef elements and recurse.
    for catalog_ref in root.findall(".//{}".format(universal_name(
            "catalogRef"))):
        result += urls_to_datasets(construct_catalog_url(request,
            catalog_ref.attrib[universal_name("href", XLINK_NAMESPACE)]))

    return result
