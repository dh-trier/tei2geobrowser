"""
Script to extract place name information from letters encoded in XML-TEI. 
Expects each placeName element to have @ref attribute. 
Expects each @ref attribute to have as its value a Getty ID: "tgn/12345678"
Expects each letter to have a date element with a @when-iso attribute.
For each place name, the script pulls the latitude and longitude from Getty TGN.
The script saves a CSV file suitable for input into the DARIAH Geobrowser.
"""


import os
import re
import glob
import csv
import requests
import json
from bs4 import BeautifulSoup as bs
    

xmlpath = "corpus/*TGN.xml"


def read_xml(xmlfile):
    """
    Reads an XML file.
    Transforms it to a Beautiful soup object.
    """
    print("read_xml")
    with open(xmlfile, "r", encoding="utf8") as infile: 
        xml = infile.read()
    xml = bs(xml, "xml")
    return xml


def get_date(xml): 
    """
    Extracts the date when the letter was written from the XML file.
    """
    date = xml.find_all("date")[1]["when-iso"]
    return date


def download_rdf(tgn): 
    """
    For a given Getty ID, loads the RDF file about the location. 
    """
    baseurl = "http://vocab.getty.edu/tgn/"
    url = baseurl + str(tgn) + ".rdf" 
    data = requests.get(url)
    rdf = data.text    
    return rdf


def get_geolocation(tgn): 
    """
    For a given Getty RDF object, gets latitude and longitude.
    """
    rdf = download_rdf(tgn) # calls another function
    rdf = bs(rdf, "xml")
    lat = rdf.latitude.string
    lng = rdf.longitude.string
    return lat, lng
     

def get_placenames(xml): 
    """
    Extracts all place names encoded in the XML file. 
    """
    print("get_placenames")
    placenames = xml.find_all("placeName")
    return placenames

    
def get_placenamedata(xml, placenames, placenamedata): 
    """
    For each place name, also extracts the Getty ID. 
    Based on the Getty ID, also gets the latitude and longitude (from a separate function)
    """
    print("get_placenamedata")
    date = get_date(xml) # calls another function
    for item in placenames: 
        name = item.string
        tgn = item["ref"][4:]
        lat,lng = get_geolocation(tgn) # calls another function
        placenamedata.append([name, lat, lng, tgn, date])
    return placenamedata


def save_placenamedata(placenamedata): 
    """
    Saves all entries in a CSV file.
    For each place name found in one of the letters, saves in one row: 
    Name, Latitude, Longitude, GettyID, TimeStamp (=date of the letter). 
    The other columns are required by the Geobrowswer. 
    Saves a CSV file suitable for input into the Geobrowser.
    """
    print("\nsave_placenamedata")
    with open("placename-data.csv", "w", encoding="utf8") as csvfile: 
        writer = csv.writer(csvfile)
        columns = ["Name", "Address", "Latitude", "Longitude", "GettyID", "TimeStamp", "TimeSpan:begin", "TimeSpan:end"]
        writer.writerow(columns)
        for i in placenamedata:
            #print(item)
            writer.writerow([i[0], i[0], i[1], i[2], i[3], i[4], "", ""])
        

def main(xmlpath): 
    """
    Coordinates the script.
    """
    placenamedata = []
    for xmlfile in glob.glob(xmlpath): 
        print("\n" + xmlfile)
        xml = read_xml(xmlfile)
        placenames = get_placenames(xml)
        placenamedata = get_placenamedata(xml, placenames, placenamedata)
    save_placenamedata(placenamedata)
    
main(xmlpath)
