package dict

type UnitFileList struct {
	Repo  string `json:"repo"`
	Files []File `json:"files"`
}

type File struct {
	DirName   string `json:"dirname"`
	FileNames string `json:"filenames"`
	FileTypes string `json:"filetypes"`
}
