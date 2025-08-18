package models

type File struct {
	DirName   string `json:"dirname"`
	FileNames string `json:"filenames"`
	FileTypes string `json:"filetypes"`
}

type UnitFileList struct {
	Repo  string `json:"repo"`
	Files []File `json:"files"`
}

type Version struct {
	Epoch   string `json:"epoch"`
	Version string `json:"version"`
	Release string `json:"release"`
}

type UnitBase struct {
	Epoch   string `json:"epoch"`
	Version string `json:"version"`
	Release string `json:"release"`
	Name    string `json:"name"`
	Flags   string `json:"flags"`
}

type Changelog struct {
	Author    string `json:"author"`
	Changelog string `json:"changelog"`
	Date      uint64 `json:"date"`
}

type UnitOther struct {
	Repo       string      `json:"repo"`
	Changelogs []Changelog `json:"changelogs"`
}

type UnitPrimary struct {
	Epoch       string     `json:"epoch"`
	Version     string     `json:"version"`
	Release     string     `json:"release"`
	Repo        string     `json:"repo"`
	Arch        string     `json:"arch"`
	Summary     string     `json:"summary"`
	Description string     `json:"description"`
	Basename    string     `json:"basename"`
	URL         string     `json:"url"`
	Supplements []UnitBase `json:"supplements"`
	Recommends  []UnitBase `json:"recommends"`
	Conflicts   []UnitBase `json:"conflicts"`
	Obsoletes   []UnitBase `json:"obsoletes"`
	Provides    []UnitBase `json:"provides"`
	Requires    []UnitBase `json:"requires"`
	Enhances    []UnitBase `json:"enhances"`
	Suggests    []UnitBase `json:"suggests"`
	CoPackages  []string   `json:"co-packages"`
}
