package page

type Card struct {
	Iden string
	Head string
	Desc string
	Path string
}

type Date struct {
	When string
	Past string
}

type Vary struct {
	Primary   Date
	Changelog Date
	Filelists Date
	Safe      string
}

type Page struct {
	Name string
	Vers string
	Host string
	Conn string
	Dict map[string]Vary
	Park []Card
}
