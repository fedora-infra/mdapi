package dict

type UnitOther struct {
	Repo       string      `json:"repo"`
	Changelogs []Changelog `json:"changelogs"`
}

type Changelog struct {
	Author    string `json:"author"`
	Changelog string `json:"changelog"`
	Date      uint64 `json:"date"`
}
