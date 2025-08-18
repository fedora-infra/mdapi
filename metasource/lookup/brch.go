package lookup

import (
	"metasource/metasource/config"
	"os"
	"strings"
)

func InsertBranch(list *[]string, name *string) {
	var avbl bool
	var item string

	for _, item = range *list {
		if item == *name {
			avbl = true
			break
		}
	}

	if !avbl {
		*list = append(*list, *name)
	}
}

var ReadBranches = func() ([]string, error) {
	var expt error
	var rslt []string
	var item os.DirEntry
	var list []os.DirEntry
	var name string

	rslt = []string{}

	list, expt = os.ReadDir(config.DBFOLDER)
	if expt != nil {
		return rslt, expt
	}

	for _, item = range list {
		name = item.Name()
		if !item.IsDir() && strings.HasPrefix(item.Name(), "metasource-") && strings.HasSuffix(item.Name(), "-primary.sqlite") {
			name = strings.Replace(name, "metasource-", "", -1)
			name = strings.Replace(name, "-primary.sqlite", "", -1)
			name = strings.Replace(name, "-testing", "", -1)
			name = strings.Replace(name, "-updates", "", -1)
			InsertBranch(&rslt, &name)
		}
	}

	return rslt, expt
}
