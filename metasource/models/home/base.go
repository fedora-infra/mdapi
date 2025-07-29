package home

import "database/sql"

type LinkUnit struct {
	Name string
	Link string
}

type FileUnit struct {
	Name string
	Path string
	Type string
	Hash Checksum
	Keep bool
}

type Checksum struct {
	Data string
	Type string
}

type PackUnit struct {
	Key     int
	Id      sql.NullString
	Name    sql.NullString
	Source  sql.NullString
	Epoch   sql.NullString
	Version sql.NullString
	Release sql.NullString
	Arch    sql.NullString
	Summary sql.NullString
	Desc    sql.NullString
	Link    sql.NullString
}

type DepsUnit struct {
	Id      int
	Key     int
	Name    sql.NullString
	Epoch   sql.NullString
	Version sql.NullString
	Release sql.NullString
	Flags   sql.NullString
}

type ExtnUnit struct {
	Supplements []DepsUnit
	Recommends  []DepsUnit
	Conflicts   []DepsUnit
	Obsoletes   []DepsUnit
	Provides    []DepsUnit
	Requires    []DepsUnit
	Enhances    []DepsUnit
	Suggests    []DepsUnit
	CoPackages  []string
}

type FilelistUnit struct {
	Key       int
	Directory sql.NullString
	Name      sql.NullString
	Type      sql.NullString
}

type FilelistRslt struct {
	List []FilelistUnit
}

type OthrUnit struct {
	Key    int
	Author sql.NullString
	Text   sql.NullString
	Date   uint64
}

type OthrRslt struct {
	List []OthrUnit
}
