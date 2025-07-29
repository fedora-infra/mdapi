package dict

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
