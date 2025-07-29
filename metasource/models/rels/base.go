package rels

type Releases struct {
	Page  int    `json:"page"`
	Pages int    `json:"pages"`
	Total int    `json:"total"`
	Rows  int    `json:"rows_per_page"`
	List  []Unit `json:"releases"`
}

type Unit struct {
	Name                    string `json:"name"`
	LongName                string `json:"long_name"`
	Version                 string `json:"version"`
	IdPrefix                string `json:"id_prefix"`
	Branch                  string `json:"branch"`
	DistTag                 string `json:"dist_tag"`
	StableTag               string `json:"stable_tag"`
	TestingTag              string `json:"testing_tag"`
	CandidateTag            string `json:"candidate_tag"`
	PendSigningTag          string `json:"pending_signing_tag"`
	PendTestingTag          string `json:"pending_testing_tag"`
	PendStableTag           string `json:"pending_stable_tag"`
	OverrideTag             string `json:"override_tag"`
	MailTemplate            string `json:"mail_template"`
	State                   string `json:"state"`
	ComposedByBodhi         bool   `json:"composed_by_bodhi"`
	CreateAutomaticUpdates  bool   `json:"create_automatic_updates"`
	PackageManager          string `json:"package_manager"`
	TestingRepository       string `json:"testing_repository"`
	ReleasedOn              string `json:"released_on"`
	Eol                     string `json:"eol"`
	MandateTestDaysCritPath int    `json:"critpath_mandatory_days_in_testing"`
	MandateTestDaysStandard int    `json:"mandatory_days_in_testing"`
	MinKarmaCritPath        int    `json:"critpath_min_karma"`
	MinKarmaStandard        int    `json:"min_karma"`
	SettingStatus           string `json:"setting_status"`
}
