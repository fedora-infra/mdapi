package sxml

import "encoding/xml"

type RepoMD struct {
	XMLName  xml.Name   `xml:"repomd"`
	XMLNS    string     `xml:"xmlns,attr"`
	XMLNSRPM string     `xml:"xmlns:rpm,attr"`
	Revision uint64     `xml:"revision"`
	Data     []UnitData `xml:"data"`
}

type UnitData struct {
	XMLName      xml.Name     `xml:"data"`
	Type         string       `xml:"type,attr"`
	ChecksumComp ChecksumComp `xml:"checksum"`
	ChecksumOpen ChecksumOpen `xml:"open-checksum"`
	Location     LocationMD   `xml:"location"`
	TimeStamp    uint64       `xml:"timestamp"`
	SizeComp     uint64       `xml:"size"`
	SizeOpen     uint64       `xml:"open-size"`
}

type ChecksumMDBase struct {
	Type string `xml:"type,attr"`
	Data string `xml:",chardata"`
}

type ChecksumComp struct {
	XMLName xml.Name `xml:"checksum"`
	ChecksumMDBase
}

type ChecksumOpen struct {
	XMLName xml.Name `xml:"open-checksum"`
	ChecksumMDBase
}

type LocationMD struct {
	XMLName xml.Name `xml:"location"`
	Href    string   `xml:"href,attr"`
}
