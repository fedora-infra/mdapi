package dict

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
